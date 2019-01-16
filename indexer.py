import os, nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

def createCSVFile():
    # Initialize Data Structures
    documentList = []
    invertedIndex = {}
    documentId = -1

    # Initialize Stemmer
    stemmer = PorterStemmer()

    # Iterating all files in 'dataset' directory
    for file in os.listdir("./dataset"):
        if file.endswith(".txt"):
            documentId += 1
            documentList.append(file.replace('.txt', ''))
            # New Syntax: removes the need to write cleanup code ie. close() after open()
            with open('dataset/'+file, 'r') as inputFile:
                data = inputFile.read()
                words = word_tokenize(data)
                # Adding stemmed words into inverted index
                for word in words:
                    stemmedWord = stemmer.stem(word).lower()
                    if stemmedWord not in invertedIndex:
                        invertedIndex[stemmedWord] = { documentId }
                    elif documentId not in invertedIndex[stemmedWord]:
                        invertedIndex[stemmedWord].add(documentId)

    # Save as CSV
    with open('inverted-index.csv', 'w') as outputFile:
        for word in invertedIndex:
            sortedDocIds = sorted(invertedIndex[word])
            for i in range(len(sortedDocIds)):
                sortedDocIds[i] = str(sortedDocIds[i])
            indexRow = word + ',' + ','.join(sortedDocIds) + '\n'
            outputFile.write(indexRow)
    # Save Document Id List
    with open('document-list.txt', 'w') as outputFile:
        outputFile.write('\n'.join(documentList))