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
                termIndices.append(set(invertedIndex[stemmer.stem(term)]))
            except:
                print(term + ': Not Found - ignoring')

        resultSet = set()
        for termIndex in termIndices:
            if len(resultSet) == 0:
                resultSet = termIndex
            else:
                resultSet = resultSet.intersection(termIndex)
        for docId in resultSet:
            print(documentList[int(docId)])
        