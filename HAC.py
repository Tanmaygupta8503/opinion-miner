"""
 The HAC algorithm implementation - Extraction of potential features from the reviews
"""

import re
import nltk
import string
import enchant
import operator
from nltk.corpus import stopwords
from collections import OrderedDict 
from textblob import TextBlob, Word
from nltk.corpus import brown
from textblob import Blobber
from textblob.taggers import NLTKTagger

#Dict to convert the raw user text to meaningful words for analysis
apostropheList = {"n't" : "not","aren't" : "are not","can't" : "cannot","couldn't" : "could not","didn't" : "did not","doesn't" : "does not", \
				  "don't" : "do not","hadn't" : "had not","hasn't" : "has not","haven't" : "have not","he'd" : "he had","he'll" : "he will", \
				  "he's" : "he is","I'd" : "I had","I'll" : "I will","I'm" : "I am","I've" : "I have","isn't" : "is not","it's" : \
				  "it is","let's" : "let us","mustn't" : "must not","shan't" : "shall not","she'd" : "she had","she'll" : "she will", \
				  "she's" : "she is", "shouldn't" : "should not","that's" : "that is","there's" : "there is","they'd" : "they had", \
				  "they'll" : "they will", "they're" : "they are","they've" : "they have","we'd" : "we had","we're" : "we are","we've" : "we have", \
				  "weren't" : "were not", "what'll" : "what will","what're" : "what are","what's" : "what is","what've" : "what have", \
				  "where's" : "where is","who'd" : "who had", "who'll" : "who will","who're" : "who are","who's" : "who is","who've" : "who have", \
				  "won't" : "will not","wouldn't" : "would not", "you'd" : "you had","you'll" : "you will","you're" : "you are","you've" : "you have"}

#Removing stop words might lead to better data analysis				  
stopWords = stopwords.words("english")

#Exclude punctuations from the reviews
exclude = set(string.punctuation)
exclude.remove("_")

#Remove all the hyperlinks from the reviews
linkPtrn = re.compile("^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$")

#English vocabulary
enchVocab = enchant.Dict("en_US")
vocabList = set(w.lower() for w in nltk.corpus.words.words())

#Max hops to find the nearby noun from the position of adjective
maxHops = 4

#Find all the potential features from the reviews
def findFeatures(reviewContent,filename):
	#nounScores is the dict containing nouns from all reviews and their respective scores from HAC algorithm
	nounScores = dict()

	#adjDict dict contains adjective and the corresponding noun which it is assigned to
	adjDict = dict()
	tb = Blobber(pos_tagger = NLTKTagger())

	for a in range(len(reviewContent)):								#Stores the score of the nouns
		for i in range(len(reviewContent[a])):
			text = ' '.join([word for word in reviewContent[a][i].split() if word not in stopwords.words("english")])
			text = ''.join(ch for ch in text if ch not in exclude)
			text = nltk.word_tokenize(text)
			x = nltk.pos_tag(text)

			#Get the noun/adjective words and store it in tagList
			tagList = []
			for e in x:
				if(e[1] == "NN" or e[1] == "JJ"):
					tagList.append(e)
	
			#Add the nouns(which are not in the nounScores dict) to the dict
			for e in tagList:
				if e[1] == "NN":
					if e[0] not in nounScores:
						nounScores[e[0]] = 0

			#For every adjective, find nearby noun
			for l in range(len(tagList)):
				if("JJ" in tagList[l][1]):
					j = k = leftHop = rightHop = -1
				
					#Find the closest noun to the right of the adjective in the line
					for j in range(l + 1, len(tagList)):
						if(j == l + maxHops):
							break
						if("NN" in tagList[j][1]):
							rightHop = (j - l)
							break

					#Find the closest noun to the left of the adjective in the line
					for k in range(l - 1, -1, -1):
						#Incase hopped the 'maxHops' number of words and no noun was found, ignore the adjective
						if(j == l - maxHops):
							break
						if("NN" in tagList[k][1]):
							leftHop = (l - k)
							break

					#Compare which noun is closer to adjective(left or right) and assign the adj to corresponding noun
					if(leftHop > 0 and rightHop > 0):					#If nouns exist on both sides of adjective
						if (leftHop - rightHop) >= 0:						#If left noun is farther
							adjDict[tagList[l][0]] = tagList[j][0]
							nounScores[tagList[j][0]] += 1
						else:														#If right noun is farther
							adjDict[tagList[l][0]] = tagList[k][0]
							nounScores[tagList[k][0]] += 1
					elif leftHop > 0:											#If noun is not found on RHS of adjective
						adjDict[tagList[l][0]] = tagList[k][0]
						nounScores[tagList[k][0]] += 1
					elif rightHop > 0:										#If noun is not found on LHS of adjective
						adjDict[tagList[l][0]] = tagList[j][0]
						nounScores[tagList[j][0]] += 1
	
	nounScores = OrderedDict(sorted(nounScores.items(), key=operator.itemgetter(1)))
	return filterAdj(nounScores, adjDict,filename)

def filterAdj(nounScores, adjDict,filename):
	adjectList = list(adjDict.keys())
	nouns = []
	for key, value in nounScores.items():
		if value >= 3:
			nouns.append(key)
	nouns1 = ["sound quality","battery life","great phone","cell phone","menu option","color screen","flip phone","samsung phone","nokia phones","corporate email","ring tone","tmobile service"]

	nouns = set(nouns)

	stopWords = stopwords.words("english")
	exclude = set(string.punctuation)
	reviewTitle = []
	reviewContent = []

	with open(filename) as f:
		review = []
		for line in f:
			if line[:6] == "[+][t]":
				if review:
					reviewContent.append(review)
					review = []
				reviewTitle.append(line.split("[+][t]")[1].rstrip("\r\n"))
			elif line[:6] == "[-][t]":
				if review:
					reviewContent.append(review)
					review = []
				reviewTitle.append(line.split("[-][t]")[1].rstrip("\r\n"))
			else:
				if "##" in line:
					x = line.split("##")
					#if len(x[0]) != 0:
					for i in range(1, len(x)):
						review.append(x[i].rstrip("\r\n"))
				else:
					continue
		reviewContent.append(review)

	tb = Blobber(pos_tagger=NLTKTagger())
	nounScores = dict()
	f = open('modified.txt', 'w')
	for a in range(len(reviewContent)):
		f.write("[t]"+reviewTitle[a])
		f.write("\r\n")	
										#Stores the score of the nouns
		for i in range(len(reviewContent[a])):
			text = reviewContent[a][i]
			x = tb(text).tags #Perceptron tagger
			#Get the noun/adjective words and store it in tagList
			tagList = []
			e = 0
			f.write("##")
	
			while e<len(x):
				tagList = []
				f.write(x[e][0])
				e = e+1
				count = e
				if(count<len(x) and x[count-1][1] == "NN" and x[count][1] == "NN"):
					tagList.append(x[count-1][0])
				
					while(count < len(x) and x[count][1] == "NN"):
						tagList.append(x[count][0])
						count = count+1
				if tagList != [] and len(tagList) == 2:
					if set(tagList) <= nouns: 
					
						for t in range(1,len(tagList)):
							f.write(tagList[t])
						e = count
				f.write(" ")
			f.write(".\r\n")

	return adjectList
		
	
