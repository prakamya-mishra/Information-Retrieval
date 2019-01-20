import os, click, nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

class IndexRow:
  def __init__(self):
    self.container = list()
    self.length = 0

  def insert(self, value):
    # Adds an item in such a manner that contents are sorted
    # in ascending order and no duplicates are included
    if self.length == 0:
      self.container.append(value)
      self.length = 1
      return
    tmp = list()
    for i in range(self.length):
      containerValue = self.container[i]
      if value == containerValue:
        return
      if value < containerValue:
        tmp.append(value)
      tmp.append(containerValue)
      if i == self.length - 1 and value > containerValue:
        tmp.append(value)
    self.container = tmp
    self.length += 1
    
  def __str__(self):
    output = ''
    if self.length > 0:
      output = str(self.container[0])
      for i in range(1, self.length):
        output += ',' + str(self.container[i])
    return output

  def __lt__(self, other):
    return self.length < other.length

  def AND(self, other):
    # For optimization, assuming self to be smaller in length
    tmp = IndexRow()
    i, j = 0, 0
    if other < self:
      self, other = other, self
    while i < self.length:
      if self.container[i] < other.container[j]:
        i += 1
      elif self.container[i] > other.container[j]:
        j += 1
      else:
        tmp.insert(self.container[i])
        i += 1
        j += 1
    return tmp

  def OR(self, other):
    tmp = IndexRow()
    i, j = 0, 0
    while i < self.length or j < other.length:
      if self.container[i] < other.container[j]:
        tmp.insert(self.container[i])
        i = i+1 if self.length - 1 > i else i
      elif self.container[i] > other.container[j]:
        tmp.insert(other.container[j])
        j = j+1 if other.length - 1 > j else j
      else:
        tmp.insert(self.container[i])
        i = i+1 if self.length - 1 > i else i
        j = j+1 if other.length - 1 > j else j
    return tmp

  def NOT(self, universal):
    # self is smaller than or equal to universal
    tmp = IndexRow()
    i, j = 0, -1
    while i < self.length:
      j += 1
      if self.container[i] == universal[j]:
        i += 1
        continue
      tmp.insert(universal[j])
    return tmp





class InvertedIndex:
  def __init__(self):
    self.container = dict()
    self.docs = list()
    self.universe = list()
    self.stemmer = PorterStemmer()

  def insert(self, word, value):
    stemmedWord = self.stemmer.stem(word).lower()
    if stemmedWord not in self.container.keys():
      self.container[stemmedWord] = IndexRow()
    self.container[stemmedWord].insert(value)

  def fetch(self, word):
    stemmedWord = self.stemmer.stem(word).lower()
    return self.container[stemmedWord]

  def generateFromDir(self, dirpath):
    docId = -1

    # List all required dataset documents
    documents = [ document for document in os.listdir(dirpath) if document.endswith('.txt') ]
    print('\n\nParsing all files in the given dataset ...')
    print('Generating inverted-index ...')

    # Show progressbar while processing files
    with click.progressbar(documents) as docs:
      for file in docs:
        docId += 1
        self.universe.append(docId)
        self.docs.append(file.replace('.txt', ''))
        # New Syntax: removes the need to write cleanup code ie. close() after open()
        with open('dataset/' + file, 'r') as inputFile:
          data = inputFile.read()
          words = word_tokenize(data)
          # Adding stemmed words into inverted index
          for word in words:
            self.insert(word, docId)

  def createCSVFile(self, filename):
    with open(filename, 'w') as outputFile:
      for word in self.container:
        print(word, self.container[word], sep=',', file=outputFile)

  def printDocList(self, docList):
    for docId in docList:
      print(self.docs[docId])



# MAIN Function
if __name__ == '__main__':
  invertedIndex = InvertedIndex()
  invertedIndex.generateFromDir('./dataset')

  # CSV Section
  printCSV = input('Should we print a CSV for you(y or n)?')
  if printCSV == 'y':
    invertedIndex.createCSVFile('inverted-index.csv')
  else:
    print('Ignoring CSV ...')

  # Query Section
  while True:
    query = input('Enter your query(q to quit):')
    if query.lower() == 'q':
        break
    