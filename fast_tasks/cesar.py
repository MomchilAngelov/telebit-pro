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

alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
alphabet_coded = {}
already_coded = []

current_unique_char = 0

number_of_words = int(input("Въведи брой думи: "))
words = []

for x in range(number_of_words):
	word = input("Въведи дума: ")
	words.append(word)

max_len = 0

for word in words:
	if len(word) > max_len:
		max_len = len(word)

for k in range(max_len):
	for word in words:
		try:
			if word[k] not in already_coded:
				already_coded.append(word[k])
				alphabet_coded[word[k]] = alphabet[current_unique_char]
				current_unique_char += 1
		except Exception as e:
			continue

for k in range(current_unique_char, len(alphabet)):
	for k in alphabet:
		if k not in already_coded:
			already_coded.append(k)
			alphabet_coded[k] = alphabet[current_unique_char]
			current_unique_char += 1


cryptic_words = []
for word in words:
	cryptic_word = ""
	for char in word:
		cryptic_word += alphabet_coded[char]
	cryptic_words.append(cryptic_word)

cryptic_words_sorted = sorted(cryptic_words)
if cryptic_words == cryptic_words_sorted:
	print("YES")
	for key in sorted(alphabet_coded, key=alphabet_coded.get):
		print(key, end=",")
	print()
else:
	print("NO")