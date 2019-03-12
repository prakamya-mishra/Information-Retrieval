import os
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

## Config

DATASET_DIR = 'dataset'
OUTPUT_FILENAME = 'proximity.json'


## Globals

inverted_index = dict()
docs = list()
LEMMATIZER = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words('english'))

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

      for i in range(len(words)):
        word = words[i]
        # Step 2: Normalize Words
        processed_word = normalize(word)
        if processed_word is None:
          continue
        
        # Step 3: Add to inverted index
        if processed_word not in inverted_index.keys():
          inverted_index[processed_word] = {}
        if doc_id not in inverted_index[processed_word].keys():
          inverted_index[processed_word][doc_id] = []
        inverted_index[processed_word][doc_id].append(i)

  save_as_json(inverted_index)
  print(f'Positional Inverted index saved as {OUTPUT_FILENAME}!!')

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

def proximity(obj_a, obj_b, dist):
  tmp = dict()
  docs_a = obj_a.keys()
  docs_b = obj_b.keys()
  docs_containing_both = AND(docs_a, docs_b)
  for doc_id in docs_containing_both:
    i, j = 0, 0
    pos_a = obj_a[doc_id]
    pos_b = obj_b[doc_id]
    while i < len(pos_a) and j < len(pos_b):
      if pos_b[j] - pos_a[i] < 0:
        j += 1
      elif pos_b[j] - pos_a[i] > dist:
        i += 1
      else:
        if doc_id not in tmp.keys():
          tmp[doc_id] = list()
        tmp[doc_id].append(pos_b[j])
        i += 1
  return tmp

def parse(query):
    query_terms = query.split()
    stack = []
    op_val = -1
    for i in range(len(query_terms)):
      if '/' == query_terms[i][0]:
        op_val = int(query_terms[i][1:])
        continue
      term = normalize(query_terms[i])
      stack.append(inverted_index[term])
      if len(stack) > 1:
        pl_2 = stack.pop()
        pl_1 = stack.pop()
        stack.append(proximity(pl_1, pl_2, op_val))
    return stack.pop().keys()

  
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
    