import sys
import copy

alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
powers = {}

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
			print(index_now*"\t"+"Comparing:", words[word_index][index_now], "and", words[word_index+1][index_now])
			if words[word_index][index_now] == words[word_index+1][index_now]:
				if words[word_index][index_now] not in powers:
					powers[words[word_index][index_now]] = 1

				print(powers)
				index_now += 1
				continue
			else:
				if (words[word_index][index_now] not in powers) and (words[word_index+1][index_now] not in powers):
					powers[words[word_index][index_now]] = 2
					powers[words[word_index+1][index_now]] = 1

				elif (words[word_index][index_now] not in powers) and (words[word_index+1][index_now] in powers):
					powers[words[word_index][index_now]] = powers.get(words[word_index+1][index_now])+1

				elif (words[word_index][index_now] in powers) and (words[word_index+1][index_now] not in powers):
					powers[words[word_index+1][index_now]] = powers.get(words[word_index][index_now])
					powers[words[word_index][index_now]] = powers.get(words[word_index][index_now]) + 1
				else:
					if powers.get(words[word_index][index_now]) <= powers.get(words[word_index+1][index_now]):
						powers[words[word_index][index_now]] = powers.get(words[word_index+1][index_now])+1
					else:
						powers[words[word_index][index_now]] += 1						

				print(powers)
				break
	except Exception as e:
		print(e)
		continue

for k in sorted(powers, key=lambda idx:powers[idx]):
	print("The char {0} has a power of {1}".format(k, powers[k]))