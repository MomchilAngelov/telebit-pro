#!/usr/bin/env python3

import os, struct, sys, time, argparse

import gevent
from gevent import socket
from gevent.pool import Pool
from gevent.event import Event

# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST = 8 # Seems to be the same on Solaris.


def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    my_sum = 0
    count_to = (len(source_string) // 2) * 2
    for count in range(0, count_to, 2):
        this = (source_string[count + 1]) * 256
        
        this += source_string[count]
        my_sum = my_sum + this
        my_sum = my_sum & 0xffffffff # Necessary?

    if count_to < len(source_string):
        my_sum = my_sum + ord(source_string[len(source_string) - 1])
        my_sum = my_sum & 0xffffffff # Necessary?

    my_sum = (my_sum >> 16) + (my_sum & 0xffff)
    my_sum = my_sum + (my_sum >> 16)
    answer = ~my_sum
    answer = answer & 0xffff

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer

class GPing:
    """
    This class, when instantiated will start listening for ICMP responses.
    Then call its send method to send pings. Callbacks will be sent ping
    details
    """
    def __init__(self,timeout=2,max_outstanding=100):
        """
        :timeout            - amount of time a ICMP echo request can be outstanding
        :max_outstanding    - maximum number of outstanding ICMP echo requests without responses (limits traffic)
        """
        self.timeout = timeout
        self.max_outstanding = max_outstanding

        # id we will increment with each ping
        self.id = 0

        # object to hold and keep track of all of our self.pings
        self.pings = {}

        # Hold failures
        self.failures = []

        # event to file when we want to shut down
        self.die_event = Event()

        # setup socket
        icmp = socket.getprotobyname("icmp")
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        except socket.error as e:
            if e.errno == 1:
                # Operation not permitted
                e.message = str(e) + (
                    " - Note that ICMP messages can only be sent from processes"
                    " running as root."
                )
                raise socket.error(e.message)
            raise # raise the original error

        self.receive_glet = gevent.spawn(self.__receive__)
        self.processto_glet = gevent.spawn(self.__process_timeouts__)


    def die(self):
        """
        try to shut everything down gracefully
        """
        print("shutting down")
        self.die_event.set()
        socket.cancel_wait()
        gevent.joinall([self.receive_glet,self.processto_glet])


    def join(self):
        """
        does a lot of nothing until self.pings is empty
        """
        while len(self.pings):
            gevent.sleep()


    def send(self, dest_addr, callback, idx, current_data, data, datapsize=64):
        """
        Send a ICMP echo request.
        :dest_addr - where to send it
        :callback  - what to call when we get a response
        :psize     - how much data to send with it
        """
        # make sure we dont have too many outstanding requests
        number_of_packages = current_data[1]


        while len(self.pings) >= self.max_outstanding:
            gevent.sleep()

        psize = datapsize
        # figure out our id
        packet_id = self.id

        # increment our id, but wrap if we go over the max size for USHORT
        self.id = (self.id + 1) % 2 ** 16


        # make a spot for this ping in self.pings
        self.pings[packet_id] = {'sent':False,'success':False,'error':False,'dest_addr':dest_addr,'dest_ip':None,'callback':callback,
        'idx': idx, 'current_data': current_data, 'data_to_write_to': data, 'dtime': time.time(), 'packages_received': 0 }

        # Resolve hostname
        try:
            dest_ip = socket.gethostbyname(dest_addr)
            self.pings[packet_id]['dest_ip'] = dest_ip
        except socket.gaierror as ex:
            self.pings[packet_id]['error'] = True
            self.pings[packet_id]['message'] = str(ex)
            return


        # Remove header size from packet size
        psize = psize - 8

        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        my_checksum = 0

        # Make a dummy heder with a 0 checksum.
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, packet_id, 1)
        my_bytes = struct.calcsize("d")
        data = (psize - my_bytes) * "Q"
        data = struct.pack("d", time.time()) + bytes(data, "utf-8")

        # Calculate the checksum on the data and the dummy header.
        my_checksum = checksum(header + data)

        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack(
            "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), packet_id, 1
        )
        packet = header + data
        # note the send_time for checking for timeouts
        self.pings[packet_id]['data'] = data
        self.pings[packet_id]['application_id'] = current_data[4]
        self.pings[packet_id]['send_time'] = time.time()

        # send the packet
        for i in range(number_of_packages):
            self.socket.sendto(packet, (dest_ip, 1)) # Don't know about the 1

        #mark the packet as sent
        self.pings[packet_id]['sent'] = True


    def __process_timeouts__(self):
        """
        check to see if any of our pings have timed out
        """
        while not self.die_event.is_set():
            for i in self.pings:

                # Detect timeout
                if self.pings[i]['sent'] and time.time() - self.pings[i]['send_time'] > self.timeout:
                    self.pings[i]['error'] = True
                    self.pings[i]['message'] = 'Timeout after {} seconds'.format(self.timeout)

                # Handle all failures
                if self.pings[i]['error'] == True:
                    self.pings[i]['callback'](self.pings[i])
                    self.failures.append(self.pings[i])
                    del(self.pings[i])
                    break

            gevent.sleep()


    def __receive__(self):
        """
        receive response packets
        """
        while 1:
            # wait till we can recv
            try:
                socket.wait_read(self.socket.fileno())
            except socket.error as e:
                if e.errno == socket.EBADF:
                    print("interrupting wait_read")
                    return
                # reraise original exceptions
                print("re-throwing socket exception on wait_read()")
                raise

            time_received = time.time()
            received_packet, addr = self.socket.recvfrom(64)
            

            # while(received_packet):
            #     received_packet, addr = self.socket.recvfrom(1024)
            #     currently_received += 1

            icmpHeader = received_packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack(
                "bbHHh", icmpHeader
            )


            if packet_id in self.pings:
                bytes_received = struct.calcsize("d")
                time_sent = struct.unpack("d", received_packet[28:28 + bytes_received])[0]


                # i'd call that a success
                # call our callback if we've got one

                self.pings[packet_id]['packages_received'] = self.pings[packet_id]['packages_received'] + 1
                
                if self.pings[packet_id]['packages_received'] == self.pings[packet_id]['current_data'][1]:
                    self.pings[packet_id]['delay'] = time_received - time_sent
                    self.pings[packet_id]['success'] = True
                    self.pings[packet_id]['callback'](self.pings[packet_id])
                    del(self.pings[packet_id])

    def print_failures(self):
        template = '{hostname:45}{message}'
        for failure in self.failures:
            message = template.format(hostname=failure['dest_addr'], message=failure.get('message', 'unknown error'))

