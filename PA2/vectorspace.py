'''
This program aims at indexing the collection and returns a ranked list of documents for each query in a list of queries.
The program will receive at least four arguments on the command line. [weighting scheme for documents, weighting schem for queries, name of folder containing the collection of documents to be indexed, the name of the file with the test queries]
by Yi Yang, 05/29/1017, yeeyoung@umich.edu
'''
import os 
import sys
import re
import math
import preprocess

# Function that adds a document to the inverted index
def indexDocument(document, weightingDoc, weightingQuery, invertedIndex):
    # preprocess the content provided as input
    texts = preprocess.removeSGML(document)
    texts = preprocess.tokenizeText(texts)
    texts = preprocess.removeStopwords(texts)
    texts = preprocess.stemWords(texts)
    # add the tokens to the inverted index provided as input and calculate teh numbers necessary to calculate the weights for the given weighting schemes
    docID = texts[0]
    tf = {}
    for word in texts:
        if word not in tf:
            tf[word] = 0
        tf[word] += 1
    for word in tf.keys():
        if word not in invertedIndex:
            invertedIndex[word] = []
        invertedIndex[word].append((docID, tf[word]))
# helper function, calculate the maximum tf in docID
def maxtf(docID, invertedIndex):
    max_tf_in = 0
    for term in invertedIndex.keys():
        for pair in invertedIndex[term]:
            if pair[0] == docID and pair[1] > max_tf_in:
                max_tf_in = pair[1]
    return max_tf_in
# helper functon, calculate tfidf weights
def cal_tfidf(queList, tfque, docSet, invertedIndex):
    docWeight = {}
    queWeight = []
    for docID in docSet:
        max_tf = maxtf(docID,invertedIndex)
        docWeight[docID] = []
        for term in queList:
            tf = 0
            for pair in invertedIndex[term]:
                if pair[0] == docID:
                    tf = pair[1]
                    break
                else:
                    continue
            tf_normal = float(tf)/max_tf
            idf = math.log10(1200.0/len(invertedIndex[term]))
            docWeight[docID].append(tf_normal * idf)
    for term in queList:
        tf_normal = float(tfque[term])/max(tfque.values())
        idf = math.log10(1200.0/len(invertedIndex[term]))
        queWeight.append(tf_normal * idf)
    # normalize the vectors
    for docID in docWeight.keys():
        length = 0.0
        for val in docWeight[docID]:
            length += math.pow(val,2)
        length = math.sqrt(length)
        for idx, val in enumerate(docWeight[docID]):
            docWeight[docID][idx] = float(val)/length
    queleng = 0.0
    for idx, val in enumerate(queWeight):
        queleng += math.pow(val,2)
    queleng = math.sqrt(queleng)
    for idx, val in enumerate(queWeight):
        queWeight[idx] = float(val)/queleng
    return docWeight, queWeight

# helper function, calculate nxx weights for document
def cal_nxx(queList, docSet, invertedIndex):
    docWeight = {}
    for docID in docSet:
        max_tf = maxtf(docID,invertedIndex)
        docWeight[docID] = []
        for term in queList:
            tf = 0.0
            for pair in invertedIndex[term]:
                if pair[0] == docID:
                    tf = pair[1]
                    break
                else:
                    continue
            docWeight[docID].append(0.5 + 0.5 * float(tf)/max_tf)
    return docWeight

# helper function, calculate bpx weights for query
def cal_bpx(queList, tfque, invertedIndex):
    queWeight = []
    for term in queList:
        queWeight.append(math.log10((1200.0 - len(invertedIndex[term]))/len(invertedIndex[term])))
    return queWeight

# Function that retrieves information from the index for a given query
# the documents and associated weights is given as {docID: [w1, w2, ..., wq], ...}
def retrieveDocuments(query, invertedIndex, weightingDoc, weightingQuery):
    # preprocess the query 
    que = preprocess.removeSGML(query)
    que = preprocess.tokenizeText(que)
    que = preprocess.removeStopwords(que)
    que = preprocess.stemWords(que)
    del que[0]
    # decide the set of documents each of which contains at least 1 tokens in query
    tfque = {}
    docSet = set()
    for token in que:
        if token not in invertedIndex.keys():
            continue
        if token not in tfque:
            tfque[token] = 0
        tfque[token] += 1
        for pair in invertedIndex[token]:
            docSet.add(pair[0])
    queList = tfque.keys()
    relDoc = {}
    # tfidf.tfidf
    if weightingDoc == "tfidf" and weightingQuery == "tfidf":
        docWeight, queWeight = cal_tfidf(queList, tfque, docSet, invertedIndex)
        for docID in docWeight.keys():
            relDoc[docID] = 0
            for idx, tf in enumerate(docWeight[docID]):
                relDoc[docID] += tf * queWeight[idx]
    #tfidf.bpx
    elif weightingDoc == "tfidf" and weightingQuery == "bpx":
        docWeight, queWeight_f = cal_tfidf(queList, tfque, docSet, invertedIndex)
        queWeight = cal_bpx(queList, tfque, invertedIndex)
        for docID in docWeight.keys():
            relDoc[docID] = 0
            for idx, tf in docWeight[docID]:
                relDoc[docID] += tf * queWeight[idx]
    #nxx.tfidf
    elif weightingDoc == "nxx" and weightingQuery == "tfidf":
        docWeight_f, queWeight = cal_tfidf(queList, tfque, docSet, invertedIndex)
        docWeight = cal_nxx(queList, docSet, invertedIndex)
        for docID in docWeight.keys():
            relDoc[docID] = 0
            for idx, tf in enumerate(docWeight[docID]):
                relDoc[docID] += tf * queWeight[idx]
    #nxx.bpx
    elif weightingDoc == "nxx" and weightingQuery == "bpx":
        docWeight = cal_nxx(queList, docSet, invertedIndex)
        queWeight = cal_bpx(queList, tfque, invertedIndex)
        for docID in docWeight.keys():
            relDoc[docID] = 0
            for idx, tf in enumerate(docWeight[docID]):
                relDoc[docID] += tf * queWeight[idx]
    else:
        print "Weighting scheme for doc is [tfidf, nxx], for query is [tfidf, bpx]"
        quit()
    return relDoc

# main function starts here
if __name__ == '__main__':
    files = os.listdir(sys.argv[3])
    weightingDoc = sys.argv[1]
    weightingQuery = sys.argv[2]
    invertedIndex = {}
    for file in files:
        with open(sys.argv[3] + file, 'r') as f:
            content = f.read()
        indexDocument(content, weightingDoc, weightingQuery, invertedIndex)
        f.close()
    # for term weighting schemes, calculate and store the length of each document
    # open the file with queries, provided as the fourth argument on the command line, and read one query at a time from this file
    output = open("cranfield." + weightingDoc + "." + weightingQuery + "." + "output", 'w')
    f = open(sys.argv[4], 'r')
    line = f.readline()
    queryId = 1
    while line:
        relDoc = retrieveDocuments(line, invertedIndex, weightingDoc, weightingQuery)
        reverseddocID = sorted(relDoc, key = relDoc.get, reverse = True)
        for num, docID in enumerate(reverseddocID):
            output.write(str(queryId) + ' ' + str(docID) + ' ' + str(relDoc[docID]) + '\n')
            if num == 9:
                break
        line = f.readline()
        queryId += 1
    f.close()
    output.close()











