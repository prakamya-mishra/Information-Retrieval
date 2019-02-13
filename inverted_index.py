import pickle

class PositionalPostingList:
  def __init__(self):
    self.__container = dict()
    self.__length = 0

  def insert(self, doc_id, position=None):
    # Adds an item in such a manner that contents are sorted
    # in ascending order and no duplicates are included
    if doc_id in self.__container.keys():
      self.__container[doc_id].append(position)
    else:
      self.__container[doc_id] = [position]
      self.__length += 1
    
  def get_doc_ids(self):
    return self.__container.keys()

  def fetch_pos(self, doc_id):
    return self.__container[doc_id]
  
  def __str__(self):
    output = ''
    if self.__length > 0:
      doc_ids = sorted(self.get_doc_ids())
      for i in range(len(doc_ids)):
        doc_id = doc_ids[i]
        output += ',' + str(doc_id) + ':<' + str(self.__container[doc_id][0])
        for j in range(1, len(self.__container[doc_id])):
          output += ',' + str(self.__container[doc_id][j])
        output += '>'
    return output[1:]

  def __len__(self):
    return self.__length



class _StorageContainer:

  def __init__(self, container, docs):
    self.container = container
    self.docs = docs
  
  @staticmethod
  def save(container, docs, filename):
    storage_obj = _StorageContainer(container, docs)
    with open(filename, 'wb') as obj_file:
      pickle.dump(storage_obj, obj_file)
  
  @staticmethod
  def load(obj, filename):
    with open(filename, 'rb') as obj_file:
      storage_obj = pickle.load(obj_file)
      obj.set_data(storage_obj.container, storage_obj.docs)
      del storage_obj
    


class PositionalInvertedIndex:
  def __init__(self):
    self.__container = dict()
    self.__docs = list()
    self.last_doc_id = -1

  def set_data(self, container, docs):
    self.__container = dict(container)
    self.__docs = list(docs)
    self.last_doc_id = len(self.__docs) - 1

  def insert(self, word, doc_id, position):
    if word not in self.__container.keys():
      self.__container[word] = PositionalPostingList()
    self.__container[word].insert(doc_id, position)

  def fetch(self, word):
    return self.__container[word]

  def insert_doc(self, doc):
    self.__docs.append(doc)
    self.last_doc_id += 1
    return self.last_doc_id

  def createCSVFile(self, filename):
    with open(filename, 'w') as outputFile:
      for word in self.__container:
        print(word, self.__container[word], sep=',', file=outputFile)

  def convertToDocs(self, doc_ids):
    output = []
    for doc_id in doc_ids:
      output.append(self.__docs[doc_id])
    return output
  
  def save(self, filename):
    _StorageContainer.save(self.__container, self.__docs, filename)

  @classmethod
  def load(cls, filename):
    new_obj = cls()
    _StorageContainer.load(new_obj, filename)
    return new_obj
