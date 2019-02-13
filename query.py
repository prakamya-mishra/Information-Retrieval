from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
import re

from inverted_index import PositionalPostingList

# Config
LEMMATIZER = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words('english'))

# Functions

def process_file(filepath):
  with open(filepath, 'r') as input_file:
    raw_data = input_file.read()
    words = word_tokenize(raw_data)
    output = []
    for i in range(len(words)):
      word = process_word(words[i])
      if word != None:
        output.append(word)
  return output

def process_word(word):
  output = word.lower() # Case Folding
  if output in STOP_WORDS or not word.isalnum(): # Stop Word Removal
    return None
  return LEMMATIZER.lemmatize(output) # Lemmatization

# Classes
class Parser:
  prec = { 'NOT': 1, 'AND': 2, 'OR': 3 }

  def __init__(self, inverted_index):
    self.inverted_index = inverted_index

  def parse(self, query):
    if re.search('AND|OR|NOT', query) != None:
      print('Deploying AND|OR|NOT parser')
      return self.parse_AON(query)
    elif re.search('\/\d*', query) != None:
      print('Deploying proximity search using positional index')
      return self.parse_proximity(query)
    else:
      print('Deploying phrase search using biwords index')
      return self.parse_phrase(query)

  def parse_AON(self, query):
    stack = []
    op_stack = []
    query_terms = query.split()
    # Create postfix
    for i in range(len(query_terms)):
      term = query_terms[i]
      if term not in ('AND', 'OR', 'NOT', '(', ')'):
        processed_word = process_word(term)
        stack.append(self.inverted_index.fetch(processed_word))
        continue
      else:
        if term == '(':
          op_stack.append('(')
        elif term == ')':
          tmp = op_stack.pop()
          while(tmp != '('): 
            stack.append(tmp)
            tmp = op_stack.pop()
        else:
          while(len(op_stack) > 0 and Parser.prec[term] > Parser.prec[op_stack[-1]]):
            stack.append(op_stack.pop())
          op_stack.append(term)
    while (len(op_stack) != 0):
      stack.append(op_stack.pop())
    # Evaluate Postfix
    for i in range(len(stack)):
      term = stack[i]
      if term not in ('AND', 'OR', 'NOT'):
        op_stack.append(term)
        continue
      elif term == 'AND':
        doc_ids_2 = op_stack.pop().get_doc_ids()
        doc_ids_1 = op_stack.pop().get_doc_ids()
        op_stack.append(Parser.AND(doc_ids_1, doc_ids_2))
      elif term == 'OR':
        doc_ids_2 = op_stack.pop().get_doc_ids()
        doc_ids_1 = op_stack.pop().get_doc_ids()
        op_stack.append(Parser.OR(doc_ids_1, doc_ids_2))
      elif term == 'NOT':
        doc_ids = op_stack.pop().get_doc_ids()
        op_stack.append(Parser.NOT(doc_ids, self.inverted_index.last_doc_id))
    return op_stack.pop().get_doc_ids()

  def parse_phrase(self, query):
    query_terms = query.split()
    stack = []
    for i in range(1, len(query_terms)):
      biword = process_word(query_terms[i-1]) + ' ' + process_word(query_terms[i])
      stack.append(self.inverted_index.fetch(biword))
      if len(stack) > 1:
        doc_ids_2 = stack.pop().get_doc_ids()
        doc_ids_1 = stack.pop().get_doc_ids()
        stack.append(Parser.AND(doc_ids_1, doc_ids_2))
    return stack.pop().get_doc_ids()


  def parse_proximity(self, query):
    query_terms = query.split()
    stack = []
    op_val = -1
    for i in range(len(query_terms)):
      if '/' == query_terms[i][0]:
        op_val = int(query_terms[i][1:])
        continue
      term = process_word(query_terms[i])
      stack.append(self.inverted_index.fetch(term))
      if len(stack) > 1:
        pl_2 = stack.pop()
        pl_1 = stack.pop()
        stack.append(Parser.proximity(pl_1, pl_2, op_val))
    return stack.pop().get_doc_ids()
  
  @staticmethod
  def AND(obj_a, obj_b):
    # For optimization, assuming a to be smaller in length
    tmp = PositionalPostingList()
    i, j = 0, 0
    docs_a = sorted(obj_a)
    docs_b = sorted(obj_b)
    if len(docs_b) < len(docs_a):
      docs_a, docs_b = docs_b, docs_a
    while i < len(docs_a):
      if docs_a[i] < docs_b[j]:
        i += 1
      elif docs_a[i] > docs_b[j]:
        j += 1
      else:
        tmp.insert(docs_a[i])
        i += 1
        j += 1
    return tmp

  @staticmethod
  def OR(obj_a, obj_b):
    tmp = PositionalPostingList()
    i, j = 0, 0
    docs_a = sorted(obj_a)
    docs_b = sorted(obj_b)
    if len(docs_b) < len(docs_a):
      docs_a, docs_b = docs_b, docs_a
    while i < len(docs_a):
      if docs_a[i] < docs_b[j]:
        tmp.insert(docs_a[i])
        i += 1
      elif docs_a[i] > docs_b[j]:
        tmp.insert(docs_b[j])
        j += 1
      else:
        tmp.insert(docs_a[i])
        i += 1
        j += 1
    while j < len(docs_b):
      tmp.insert(docs_b[j])
      j += 1
    return tmp

  @staticmethod
  def NOT(obj, last_id):
    # self is smaller than or equal to universal
    tmp = PositionalPostingList()
    i, j = 0, 0
    docs = sorted(obj)
    while i <= last_id:
      if i != docs[j]:
        tmp.insert(i)
      elif j < len(docs) - 1:
        j += 1
      i += 1
    return tmp

  @staticmethod
  def proximity(obj_a, obj_b, dist):
    tmp = PositionalPostingList()
    docs_a = obj_a.get_doc_ids()
    docs_b = obj_b.get_doc_ids()
    docs_containing_both = Parser.AND(docs_a, docs_b).get_doc_ids()
    for doc_id in docs_containing_both:
      i, j = 0, 0
      pos_a = obj_a.fetch_pos(doc_id)
      pos_b = obj_b.fetch_pos(doc_id)
      while i < len(pos_a) and j < len(pos_b):
        if int(pos_b[j]) - int(pos_a[i]) < 0:
          j += 1
        elif int(pos_b[j]) - int(pos_a[i]) > dist:
          i += 1
        else:
          tmp.insert(doc_id, pos_b[j])
          i += 1
    return tmp
            