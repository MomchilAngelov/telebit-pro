import random

alphabet_normal = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
alphabet_shuffled = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
random.shuffle(alphabet_shuffled)

words = []
for k in range(20):
	word = ""
	for c in range(10):
		r = random.randint(0, 25)
		word += alphabet_normal[r]

	words.append(word)

words.sort()


coded_words = []
for word in words:
	coded_word = ""
	for char in word:
		ind = alphabet_normal.index(char)
		coded_char = alphabet_shuffled[ind]
		coded_word += coded_char

	coded_words.append(coded_word)

print(20)
for word in coded_words:
	print(word)