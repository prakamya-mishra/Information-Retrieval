import os
import json
import math
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

## Config

DATASET_DIR = 'dataset'
OUTPUT_FILENAME = 'vsm.json'


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
          inverted_index[processed_word][doc_id] = 0
        inverted_index[processed_word][doc_id] += 1

  save_as_json(inverted_index)
  print(f'Inverted index saved as {OUTPUT_FILENAME}!!')

## Parsing Queries
def generate_query_index_ltn(query):
  # Calculates ltn -> logarithmic tf - idf score(not normalized)
  # for the query terms 
  query_index = {}
  words = word_tokenize(query)

  for i in range(len(words)):
    word = words[i]
    processed_word = normalize(word)
    if processed_word is None:
      continue

    if processed_word not in query_index and processed_word in inverted_index:
      # Keep only words that are also present in Inverted Index
      query_index[processed_word] = 0
    query_index[processed_word] += 1
  
  for term in query_index:
    tf = query_index[term]
    df = len(inverted_index[term])
    query_index[term] = (1 + math.log10(tf)) * math.log10(len(docs) / df)
  return query_index

def use_second(elem):
  return elem[1]

def parse(query):
    vsm = [] # format: [(doc_id, score), ...]
    query_index = generate_query_index_ltn(query)
    for i in range(len(docs)):
      weights = {}
      normalizer = 0
      for term in query_index:
        tf = 0 if i not in inverted_index[term].keys() else inverted_index[term][i]
        weight = 0 if tf == 0 else 1 + math.log10(tf)
        weights[term] = weight
        normalizer += weight ** 2
      normalizer = normalizer ** 0.5
      
      if normalizer == 0:
        continue
      
      score = 0
      for term in query_index:
        score += query_index[term] * (weights[term] / normalizer)
      vsm.append((i, score))
    sorted_vsm = sorted(vsm, key=use_second, reverse=True)
    sorted_ids = [sorted_vsm[i][0] for i in range(len(sorted_vsm))]
    return sorted_ids

  
if __name__ == '__main__':
  generate_inverted_index(DATASET_DIR)

  while True:
    query = input('Enter your query(q to quit):')
    if query.lower() == 'q':
      break
    else:
      output_ids = parse(query) # These will be ranked in order
    print('\n### Relevant Documents ### \n')
    no_of_docs_printed = len(output_ids) if len(output_ids) < 10 else 10
    for i in range(no_of_docs_printed):
      print(docs[output_ids[i]])
    print()

  print('Exiting ....')
    