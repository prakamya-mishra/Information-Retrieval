import os
import indexer

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
print(invertedIndex)