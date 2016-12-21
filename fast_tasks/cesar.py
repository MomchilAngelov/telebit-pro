 # Известен е кодът на Цезар, при който всяка малка буква от латинската
 # азбука се заменя с друга малка буква от латинската азбука (възможно е
 # дадена буква да се замени със себе си).   Например думата “abc” може
 # да се кодира в думата „cwz”, като буквата ‘a’ се замени с буквата ‘c’,
 # буквата ‘b’ се замени с буквата ‘w’ и буквата ‘c’ се замени с буквата
 # ‘z’.

 # Разполагате с N на брой кодирани думи. Известно е, че преди да се
 # кодират, думите са били подредени по азбучен ред (лексикографски).

 # Вашата задача е да напишете програма cezarc, която намира всяка една
 # малка буква от азбуката, с коя друга малка буква от азбуката се
 # замества така, че след разкодирането на думите, те да бъдат подредени
 # по азбучен ред (лексикографски).

 # Вход От първия ред на стандартния вход се въвежда едно цяло число N –
 # броят на думите. На следващите N реда са записани кодираните думи.

 # Изход Ако задачата има решение, на първия ред на стандартния изход се
 # извежда “Yes“ (без кавичките) и на следващия ред се извежда редицата
 # от всичките 26 малки букви, като първата буква съответства на ‘а’,
 # втората на ‘b’ и т.н. Ако задачата няма решение, се извежда “No” (без
 # кавичките). Ако решенията са повече от едно, изведете което и да било
 # от тях.

 # Ограничения: 1 < N < 100 Буквите във всяка дума са повече от една и
 # по-малко от 10.

 # Пример 1  Вход 5 pa pc mpac mama maca

 # Изход Yes pamcbdefghijklnoqrstuvwxyz

 # Пример 2 Вход 5 pn mp mn nm np

 # Изход NO

 # Обяснение на пример 1: Ако заместим малките букви от азбуката: {a, b,
 # c,… ,z} с тези от изхода, то след разкодирането на думите, те ще бъдат
 # подредени по азбучен ред (лексикографски). pa  →  ab pc  →  am mpac  →
 # cabd mama  →  cbcb maca  →  cbdb

import sys
import copy

powers = []
alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]

current_unique_char = 0
try:
	number_of_words = int(input(""))
except Exception as e:
	print("Wrong input! Number of words should be a number!")
	sys.exit(1)

if number_of_words < 1 or number_of_words > 100:
	print("Wrong input! Number of words must be between 1 and 100")
	sys.exit(1)

words = []

for x in range(number_of_words):
	word = input("")
	if len(word) < 1 or len(word) > 10:
		print("Wrong input! Size of words must be between 1 and 10")
		sys.exit(1)

	words.append(word)

max_len = 0

for word in words:
	if len(word) > max_len:
		max_len = len(word)

for word_index in range(len(words)):
	try:
		index_now = 0
		while True:
			if words[word_index][index_now] == words[word_index+1][index_now]:
				if words[word_index][index_now] not in powers:
					powers.append(words[word_index][index_now])
				print(index_now*"\t"+"Comparing:", words[word_index][index_now], "and", words[word_index+1][index_now])
				index_now += 1
				print(powers)
				continue
			else:
				print(index_now*"\t"+"Comparing:", words[word_index][index_now], "and", words[word_index+1][index_now])
				if (words[word_index][index_now] not in powers) and (words[word_index+1][index_now] not in powers):
					print("\t"*(index_now+1)+"Both not in list!")
					powers.append(words[word_index][index_now])	
					powers.append(words[word_index+1][index_now])
					break
				elif (words[word_index][index_now] not in powers) and (words[word_index+1][index_now] in powers):
					where_to_insert = powers.index(words[word_index+1][index_now+1])
					powers.insert(where_to_insert, words[word_index+1][index_now])
					break
				elif (words[word_index][index_now] in powers) and (words[word_index+1][index_now] not in powers):
					where_to_insert = powers.index(words[word_index][index_now]) + 1
					powers.insert(where_to_insert, words[word_index+1][index_now])
					break
				else:
					should_be_smaller = powers.index(words[word_index][index_now])
					should_be_bigger = powers.index(words[word_index+1][index_now])
					if should_be_bigger < should_be_smaller:
						print(powers)						
						powers.remove(words[word_index][index_now])
						print("SWAPPING!")
						powers.insert(should_be_bigger, words[word_index][index_now])
						print(powers)
					break
		print(powers)
	except Exception as e:
		print(e)
		continue

for k in alphabet:
	if k not in powers:
		powers.append(k)

print(powers)

decrypted_words = []

for word in words:
	decrypted_word = ""

	for char in word:
		where_is_in_power = powers.index(char)
		decrypted_char = alphabet[where_is_in_power]
		decrypted_word += decrypted_char

	decrypted_words.append(decrypted_word)


for ind in range(len(decrypted_words)):
	print(decrypted_words[ind])
	print(words[ind])

copied_dec = copy.copy(decrypted_words)
decrypted_words.sort()


if copied_dec == decrypted_words:
	print("YES")
	for k in powers:
		print(k, end=",")
	print()
else:
	print("NO")
