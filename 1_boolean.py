import os
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

## Config

DATASET_DIR = 'dataset'
OUTPUT_FILENAME = 'boolean.json'


## Globals

inverted_index = dict()
docs = list()
LEMMATIZER = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words('english'))
PREC = { 'NOT': 1, 'AND': 2, 'OR': 3 }


## Generate Inverted Index and output as JSON

def normalize(word):
  output = word.lower() # Case Folding
  if output in STOP_WORDS or not word.isalnum(): # Stop Word & Punctuation Removal
    return None
  return LEMMATIZER.lemmatize(output) # Lemmatization

def save_as_json(data):
  with open(OUTPUT_FILENAME, 'w') as output_file:
    json.dump(data, output_file)
    

def generate_inverted_index(dataset_dir):
  print('Generation of inverted index started ...')
  # List all .txt documents in the directory
  documents = [ document for document in os.listdir(dataset_dir) if document.endswith('.txt') ]
  for document in documents:
    docs.append(document.replace('.txt', ''))
    doc_id = len(docs) - 1
    with open(f'{dataset_dir}/{document}', 'r') as input_file:
      raw_data = input_file.read()

      # Step 1: Tokenize words
      words = word_tokenize(raw_data)

      for word in words:
        # Step 2: Normalize Words
        processed_word = normalize(word)
        if processed_word is None:
          continue
        
        # Step 3: Add to inverted index
        if processed_word not in inverted_index.keys():
          inverted_index[processed_word] = []
        if doc_id not in inverted_index[processed_word]:
          inverted_index[processed_word].append(doc_id)

  save_as_json(inverted_index)
  print(f'Inverted index saved as {OUTPUT_FILENAME}!!')


## Parsing Queries

def AND(obj_a, obj_b):
  # For optimization, assuming a to be smaller in length
  tmp = []
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
      tmp.append(docs_a[i])
      i += 1
      j += 1
  return tmp

def OR(obj_a, obj_b):
  tmp = []
  i, j = 0, 0
  docs_a = sorted(obj_a)
  docs_b = sorted(obj_b)
  if len(docs_b) < len(docs_a):
    docs_a, docs_b = docs_b, docs_a
  while i < len(docs_a):
    if docs_a[i] < docs_b[j]:
      tmp.append(docs_a[i])
      i += 1
    elif docs_a[i] > docs_b[j]:
      tmp.append(docs_b[j])
      j += 1
    else:
      tmp.append(docs_a[i])
      i += 1
      j += 1
  while j < len(docs_b):
    tmp.append(docs_b[j])
    j += 1
  return tmp

def NOT(obj):
  # self is smaller than or equal to universal
  last_id = len(docs) - 1
  tmp = []
  i, j = 0, 0
  not_docs = sorted(obj)
  while i <= last_id:
    if i != not_docs[j]:
      tmp.append(i)
    elif j < len(not_docs) - 1:
      j += 1
    i += 1
  return tmp

def parse(query):
  stack = []
  op_stack = []
  query_terms = query.split()

  # Create postfix
  for i in range(len(query_terms)):
    term = query_terms[i]
    if term not in ('AND', 'OR', 'NOT', '(', ')'):
      processed_word = normalize(term)
      stack.append(inverted_index[processed_word])
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
        while(len(op_stack) > 0 and PREC[term] > PREC[op_stack[-1]]):
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
      doc_ids_2 = op_stack.pop()
      doc_ids_1 = op_stack.pop()
      op_stack.append(AND(doc_ids_1, doc_ids_2))
    elif term == 'OR':
      doc_ids_2 = op_stack.pop()
      doc_ids_1 = op_stack.pop()
      op_stack.append(OR(doc_ids_1, doc_ids_2))
    elif term == 'NOT':
      doc_ids = op_stack.pop()
      op_stack.append(NOT(doc_ids))
  return op_stack.pop()

  
if __name__ == '__main__':
  generate_inverted_index(DATASET_DIR)

  while True:
    output_ids = []
    query = input('Enter your query(q to quit):')
    if query.lower() == 'q':
      break
    else:
      output_ids = parse(query)
    print('\n### Relevant Documents ### \n')
    for doc_id in output_ids:
      print(docs[doc_id])
    print()

  print('Exiting ....')
    