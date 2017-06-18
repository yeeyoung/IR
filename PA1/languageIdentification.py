'''
Spec: letter-based-bigram probability model with add-one smoothing for language identification
by Yi Yang, 05/24/2017, yeeyoung@umich.edu
'''
import sys
import os
import re
import codecs
import math

# Helper function to increment the frequency of word or character
def incrementChar(character, frequencyDictionary):
    if character not in frequencyDictionary.keys():
        frequencyDictionary[character] = 1
    else:
        frequencyDictionary[character] += 1

# Function to train a bigram model
def trainBigramLanguageModel(trainingtext):
    charFrequency = {}
    bigramFrequency = {}
    bigram = zip(trainingtext[0:len(trainingtext) - 1],trainingtext[1:len(trainingtext)])
    for char in bigram:
        incrementChar(char, bigramFrequency)
        incrementChar(char[0], charFrequency)
    incrementChar(trainingtext[len(trainingtext) - 1], charFrequency)
    return charFrequency, bigramFrequency

# Function to determine the language of a string
# spec for input parameters: string(text for which the language is to be identified), list of strings(each string corresponding to a language name)
# list of dictionaries with single character frequencies(each dictionary corresponding to the single character frequency in a language)
# list of dictionaries with bigram character frequencies(each dictionary corresponding to the bigram character frequency in a language)
def identifyLanguage(texts, languages, singleCharFreqDictList, bigramCharFreqDictList):
    highestprobability = 0.0
    identifiedlanguage = ''
    probabilities = []
    i = 0
    while i < len(languages):
        probability = 0.0
        for char in zip(texts[0:len(texts) - 1], texts[1:]):
            if probability <= 0.0:
                if char not in bigramCharFreqDictList[i].keys():
                    if char[0] not in singleCharFreqDictList[i].keys():
                        probability = 1.0/len(singleCharFreqDictList[i])
                    else:
                        probability = 1.0/(singleCharFreqDictList[i][char[0]] + len(singleCharFreqDictList[i]))
                else:
                    probability = (1.0 + bigramCharFreqDictList[i][char])/(singleCharFreqDictList[i][char[0]] + len(singleCharFreqDictList[i]))
            else:
                if char not in bigramCharFreqDictList[i]:
                    if char[0] not in singleCharFreqDictList[i]:
                        probability *= 1.0/len(singleCharFreqDictList[i])
                    else:
                        probability *= 1.0/(singleCharFreqDictList[i][char[0]] + len(singleCharFreqDictList[i]))
                else:
                    probability *= (1.0 + bigramCharFreqDictList[i][char])/(singleCharFreqDictList[i][char[0]] + len(singleCharFreqDictList[i]))
        if probability > highestprobability:
            highestprobability = probability
            identifiedlanguage = languages[i]
        i += 1
        probabilities.append(probability)
    return identifiedlanguage

# main program starts here
if __name__ == '__main__':
    language_train = ["English", "French", "Italian"]
    singleFreq = []
    bigramFreq = []
    for lan in language_train:
        with codecs.open("languageIdentification.data/training/" + lan, "r", "iso-8859-1") as f:
            frequency = trainBigramLanguageModel(f.read())
            singleFreq.append(frequency[0])
            bigramFreq.append(frequency[1])
            f.close()
            
    InFile = codecs.open("languageIdentification.data/" + sys.argv[1], "r", "iso-8859-1")
    ind = 1
    languageNames = ["English", "French", "Italian"]
    OutFile = codecs.open("languageIdentification.output", 'w', 'iso-8859-1')
    for line in InFile:
        OutFile.write(str(ind) + " " + identifyLanguage(line,languageNames,singleFreq,bigramFreq) + '\n')
        ind += 1
    OutFile.close()
    InFile.close()
    # Calculate the accuracy of this language identifier and put the result in answers2.txt
    sol = open("languageIdentification.data/solution",'r')
    solution = sol.readlines()
    test = open("languageIdentification.output",'r')
    testsolution = test.readlines()
    i = 0
    j = 0
    for sol_line in solution:
        if sol_line != testsolution[i]:
            j += 1
        i += 1
    answers2 = open("answers2.txt",'w')
    answers2.write("The accuracy is: " + str(float(len(solution) - j)/float(len(solution))))
    answers2.close()
    test.close()
    sol.close()



















