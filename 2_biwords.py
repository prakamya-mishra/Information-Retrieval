import os
import json
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag

## Config

DATASET_DIR = 'dataset'
OUTPUT_FILENAME = 'biwords.json'


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
      
      # Step 2: Tag part of speech on all tokens
      words = pos_tag(words)
      prev_word = None
      prev_pos = None

      for i in range(len(words)):
        word, pos = words[i]
        # Step 3: Normalize Word
        processed_word = normalize(word)
        if processed_word is None:
          continue
        
        # Step 4: Add base word to inverted index
        if processed_word not in inverted_index.keys():
          inverted_index[processed_word] = []
        if doc_id not in inverted_index[processed_word]:
          inverted_index[processed_word].append(doc_id)

        # Step 5: Check for proper nouns, generate biwords accd. and add it to the index
        if i > 0 and pos == 'NNP' and prev_pos == 'NNP':
          biword = prev_word + ' ' + processed_word
          if biword not in inverted_index.keys():
            inverted_index[biword] = []
          if doc_id not in inverted_index[biword]:
            inverted_index[biword].append(doc_id)
        prev_word = processed_word
        prev_pos = pos 

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

def parse(query):
    query_terms = query.split()
    stack = []
    for i in range(1, len(query_terms)):
      biword = normalize(query_terms[i-1]) + ' ' + normalize(query_terms[i])
      stack.append(inverted_index[biword])
      if len(stack) > 1:
        doc_ids_2 = stack.pop()
        doc_ids_1 = stack.pop()
        stack.append(AND(doc_ids_1, doc_ids_2))
    return stack.pop()

  
if __name__ == '__main__':
  generate_inverted_index(DATASET_DIR)

  while True:
    output_ids = []
    query = input('Enter your query(q to quit):')
    if query.lower() == 'q':
      break
    elif len(query.split()) < 2:
      print('Invalid Query')
      continue
    else:
      output_ids = parse(query)
    print('\n### Relevant Documents ### \n')
    for doc_id in output_ids:
      print(docs[doc_id])
    print()

  print('Exiting ....')
    