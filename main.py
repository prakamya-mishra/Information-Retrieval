import os
import indexer
from nltk.stem import PorterStemmer

# Initialize Stemmer
stemmer = PorterStemmer()

# Check for inverted-index.csv
path_dir = os.path.abspath('.')
if not os.path.exists(os.path.join(path_dir, 'inverted-index.csv')):
    print('inverted-index.csv not found...\nGenerating one for you!')
    indexer.createCSVFile()
    print('Required files generated!')

# Parsing document-list.txt
documentList = []
with open('document-list.txt') as inputFile:
    documentList = inputFile.read().splitlines()
# Parsing inverted-index.csv
invertedIndex = {}
with open('inverted-index.csv') as inputFile:
    line = inputFile.readline()
    while line != '':
        line = line.rstrip('\n')
        separatedCsvRow = line.split(',')
        invertedIndex[separatedCsvRow.pop(0)] = separatedCsvRow
        line = inputFile.readline()

# Parsing queries
while True:
    query = input('Enter your query (q to quit):')
    if query.lower() == 'q':
        break
    else:
        # As of now supports only AND queries
        queryTerms = query.lower().split(' and ')
        termIndices = []
        for term in queryTerms:
            try:
                termIndex = invertedIndex[stemmer.stem(term)]
                docFrequency = len(termIndex)
                termIndices.append((docFrequency, termIndex))
            except:
                print(term + ': Not Found - ignoring')


        # Sort all required terms by their Document Frequency using insertion sort
        if len(termIndices) > 1:
            for i in range(len(termIndices)):
                keyTerm = termIndices[i]
                j = i-1
                while (j > 0 and keyTerm[0] < termIndices[j][0]):
                    termIndices[j+1] = termIndices[j]
                    j -= 1
                termIndices[j+1] = keyTerm
        
        # Using merge strategy for AND
        result = list()
        if len(termIndices) > 0:
            result = termIndices.pop(0)[1]
            while (len(termIndices) > 0):
                curr = termIndices.pop(0)
                currList = curr[1]
                currLength = curr[0]
                resultLength = len(result)
                tmp = list()
                i,j = 0,0
                while i < resultLength:
                    if int(result[i]) < int(currList[j]):
                        i += 1
                    elif int(result[i]) > int(currList[j]):
                        j += 1
                    else:
                        tmp.append(result[i])
                        i += 1
                        j += 1
                result = tmp

        # Print Output of search
        for docId in result:
            print(documentList[int(docId)])        