'''
Spec: preprocess the textual documents: tokenization, remove the stop words, use Porter's stemmer to 
stem the words, in NLTK, we can use lemmatizer in stead of stemmer to process words
by Yi Yang, yeeyoung@umich.edu
05-20-2017
'''
import os
import sys
import re
import PorterStemmer

# contraction words list modified from http://stackoverflow.com/questions/19790188/expanding-english-language-contractions-in-python 
contractions = { 
        "ain't": "am not",
        "aren't": "are not",
        "can't": "cannot",
        "can't've": "cannot have",
        "'cause": "because",
        "could've": "could have",
        "couldn't": "could not",
        "couldn't've": "could not have",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hadn't've": "had not have",
        "hasn't": "has not",
        "haven't": "have not",
        "he'd": "he would",
        "he'd've": "he would have",
        "he'll": "he will",
        "he'll've": "he will have",
        "he's": "he is",
        "how'd": "how did",
        "how'd'y": "how do you",
        "how'll": "how will",
        "how's": "how is",
        "I'd": "I would",
        "I'd've": "I would have",
        "I'll": "I will",
        "I'll've": "I will have",
        "I'm": "I am",
        "I've": "I have",
        "isn't": "is not",
        "it'd": "it would",
        "it'd've": "it would have",
        "it'll": "it will",
        "it'll've": "it will have",
        "it's": "it is",
        "let's": "let us",
        "ma'am": "madam",
        "mayn't": "may not",
        "might've": "might have",
        "mightn't": "might not",
        "mightn't've": "might not have",
        "must've": "must have",
        "mustn't": "must not",
        "mustn't've": "must not have",
        "needn't": "need not",
        "needn't've": "need not have",
        "o'clock": "of the clock",
        "oughtn't": "ought not",
        "oughtn't've": "ought not have",
        "shan't": "shall not",
        "sha'n't": "shall not",
        "shan't've": "shall not have",
        "she'd": "she would",
        "she'd've": "she would have",
        "she'll": "she will",
        "she'll've": "she will have",
        "she's": "she is",
        "should've": "should have",
        "shouldn't": "should not",
        "shouldn't've": "should not have",
        "so've": "so have",
        "so's": "so is",
        "that'd": "that would",
        "that'd've": "that would have",
        "that's": "that is",
        "there'd": "there would",
        "there'd've": "there would have",
        "there's": "there is",
        "they'd": "they would",
        "they'd've": "they would have",
        "they'll": "they will",
        "they'll've": "they will have",
        "they're": "they are",
        "they've": "they have",
        "to've": "to have",
        "wasn't": "was not",
        "we'd": "we would",
        "we'd've": "we would have",
        "we'll": "we will",
        "we'll've": "we will have",
        "we're": "we are",
        "we've": "we have",
        "weren't": "were not",
        "what'll": "what will",
        "what'll've": "what will have",
        "what're": "what are",
        "what's": "what is",
        "what've": "what have",
        "when's": "when is",
        "when've": "when have",
        "where'd": "where did",
        "where's": "where is",
        "where've": "where have",
        "who'll": "who will",
        "who'll've": "who will have",
        "who's": "who is",
        "who've": "who have",
        "why's": "why is",
        "why've": "why have",
        "will've": "will have",
        "won't": "will not",
        "won't've": "will not have",
        "would've": "would have",
        "wouldn't": "would not",
        "wouldn't've": "would not have",
        "y'all": "you all",
        "y'all'd": "you all would",
        "y'all'd've": "you all would have",
        "y'all're": "you all are",
        "y'all've": "you all have",
        "you'd": "you would",
        "you'd've": "you would have",
        "you'll": "you will",
        "you'll've": "you will have",
        "you're": "you are",
        "you've": "you have"
        }
# construct a set to contain months
months = set(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])
# Function that removes the SGML tags.
def removeSGML(linestr):
    return re.sub(r"[<].*[>\n]","",linestr)

# Function that tokenizes the texts. processing dates format is really complicated and only three simple date formats are considered here
def tokenizeText(linestr):
    line1 = linestr.split() # generate a list of raw tokens with punctuations
    tokens = []
    date = []
    for word in line1:
        # deal with comma, comma may appear in numbers 
        if word.find(",") != -1:
            word = re.sub(r"[,]*","",word)
            if len(date) == 1:
                if word in range(1,32):
                    date.append(word + ",")# if this is a date format, then maintain the comma in the original date format
                    continue
                else:
                    tokens.append(' '.join(date))
                    date = []

        # deal with period, period may appear in acronyms, abbreviations, numbers 
        if word == ".":
            continue
        elif word[0:len(word) - 1].isdigit():# check if it is a number 
            word = re.sub(r"[.]*","",word)
        else: 
            pass # else the word containing periods is acronyms or abbreviations or dates in format "yyyy.mm.dd", keep the period
        # deal with apostrophes
        if word.find("'") != -1:
            apo = word.find("'",0,len(word))
            if word in contractions.keys(): # check if it is a contraction word
                tempStr = contractions[word]
                tempList = tempStr.split()
                tokens += tempList
            elif word[0] == "'" and word[len(word) - 1] == "'": # check if it is a quote
                tokens.append(word[1:len(word) - 1])
            else: # then it must be possessive
                tokens.append(word[0:apo])
                tokens.append(word[apo:])
        # deal with hyphenations
        if word.find("-") != -1: 
            pass # do nothing
        # put year in the third position of date list    
        if len(date) == 2:
            if word.isdigit():
                date.append(word)
                tokens.append(' '.join(date))
                date = []
                continue
            else:
                tokens.append(' '.join(date))
                date = []

        # deal with dates, we address dates formates as "mm/dd/yyyy", "yyyy.mm.dd", "May 12, 2017"
        if len(date) == 0:
            if word.lower() in months:
                date.append(word)
                continue
            else:
                pass
        # if the word is not a special format or preprocessed by throwing comma, appostrophe and period
        tokens.append(word)
    return tokens

# Function that removes the stopwords
def removeStopwords(list_of_tokens):
    # open a list of stopwords to filter a list of tokens w/o stopwords
    with open("stopwords","r") as f:
        stopwords = f.read().split()
    return filter(lambda token: token not in stopwords, list_of_tokens)

# Function that stems the words
def stemWords(list_of_tokens):
    p = PorterStemmer.PorterStemmer() # instance of a Porter Stemmer
    stemmed_list = []
    for token in list_of_tokens:
        if token.isalpha():
            stemmed_list.append(p.stem(token.lower(),0,len(token) - 1))
        else: # if non-aphabetical character exists, no stemming!
            stemmed_list.append(token.lower())
    return stemmed_list

# main program starts here
if __name__ == '__main__':
    folder = sys.argv[1] # cranfieldDocs/
    documents = os.listdir(folder) # list of documents in the folder
    dictionary = {}
    wordSize = 0
    vocabSize = 0
    for filename in documents:
        with open(folder+filename,'r') as f:
            texts = f.read() # a string of texts
            f.close()
        texts = texts.lower()
        texts = removeSGML(texts)
        texts = tokenizeText(texts)
        texts = removeStopwords(texts)
        texts = stemWords(texts)
        for word in texts:
            wordSize += 1
            if word not in dictionary:
                dictionary[word] = 0
            dictionary[word] += 1
    vocabSize = len(dictionary)
    sortedWords = sorted(dictionary, key = dictionary.get, reverse = True)
    f = open("preprocess.output",'w')
    f.write("Words " + str(wordSize) + '\n')
    f.write("Vocabulary " + str(vocabSize) + '\n')
    f.write("Top 50 words\n")
    for idx, i in enumerate(sortedWords, 1):
        f.write(i + " " + str(dictionary[i]) + '\n')
        if idx == 50:
            break
    f.close()

    
    






