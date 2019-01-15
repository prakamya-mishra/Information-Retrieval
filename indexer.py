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
                    if word not in invertedIndex:
                        invertedIndex[stemmer.stem(word).lower()] = set(str(documentId))
                    elif documentId not in invertedIndex[word]:
                        invertedIndex[stemmer.stem(word).lower()].add(str(documentId))

    # Save as CSV
    with open('inverted-index.csv', 'w') as outputFile:
        for word in invertedIndex:
            indexRow = word + ',' + ','.join(sorted(invertedIndex[word])) + '\n'
            outputFile.write(indexRow)
    # Save Document Id List
    with open('document-list.txt', 'w') as outputFile:
        outputFile.write('\n'.join(documentList))