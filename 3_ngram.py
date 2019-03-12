import os
import json
from math import inf
from nltk.tokenize import word_tokenize

## Config

DATASET_DIR = 'dataset'
LOWEST_N = 2 # also acts as an default
DISSIMILAR_THRESHHOLD = 3


## Globals

ngram_index = dict()

def set_N(n):
  global N, OUTPUT_FILENAME
  N = n
  OUTPUT_FILENAME = f'ngram_{n}.json'


## Generate N-gram Index and output as JSON

def save_as_json(ngram):
  # Convert to JSON serializable format
  json_serializable_data = dict(ngram)
  for ngram in json_serializable_data:
    json_serializable_data[ngram] = list(json_serializable_data[ngram])
  
  with open(OUTPUT_FILENAME, 'w') as output_file:
    json.dump(json_serializable_data, output_file)
  print(f'N-Gram(N={N}) index saved as {OUTPUT_FILENAME}!!')
    
def normalize(word):
  return word.lower()

def generate_ngram_index(dataset_dir):
  print(f'Generation of N-gram(N={N}) index started ...')
  # List all .txt documents in the directory
  documents = [ document for document in os.listdir(dataset_dir) if document.endswith('.txt') ]
  for document in documents:
    with open(f'{dataset_dir}/{document}', 'r') as input_file:
      raw_data = input_file.read()

      # Step 1: Tokenize words
      words = word_tokenize(raw_data)

      for word in words:
        # Step 2: Normalize word
        word = normalize(word)

        # Step 3: Add to N-Gram Index
        for i in range(N, len(word) + 1):
          split = word[i-N : i]
          if split not in ngram_index:
            ngram_index[split] = set()
          ngram_index[split].add(word)
        
  save_as_json(ngram_index)

## Parsing
  
def get_edit_distance(word1, word2):
  # Uses Levenshtein distance
  no_of_cols = len(word2) + 1
  no_of_rows = len(word1) + 1

  distance_matrix = [[ -1 for j in range(no_of_cols)] for i in range(no_of_rows)]

  for i in range(no_of_rows):
    distance_matrix[i][0] = i

  for j in range(no_of_cols):
    distance_matrix[0][j] = j

  for i in range(1, no_of_rows):
    for j in range(1, no_of_cols):
      if word1[i-1] == word2[j-1]:
        distance_matrix[i][j] = min([distance_matrix[i-1][j-1], distance_matrix[i][j-1] + 1, distance_matrix[i-1][j] + 1])
      else:
        distance_matrix[i][j] = min([distance_matrix[i-1][j-1] + 1, distance_matrix[i][j-1] + 1, distance_matrix[i-1][j] + 1])
  
  return distance_matrix[no_of_rows - 1][no_of_cols - 1]

def get_similar_words(ngrams, threshhold = 0, ptr = -1):
  if ptr == -(len(ngrams)+1):
    return None
  else:
    ngram = ngrams[ptr]
    ngram_words = ngram_index[ngram] if ngram in ngram_index.keys() else None

    # Ngram not in index
    if ngram_words is None:
      return get_similar_words(ngrams, threshhold, ptr-1)
    
    # Matches that dont use this ngram
    skipped_matches = None
    if threshhold < DISSIMILAR_THRESHHOLD:
      skipped_matches = get_similar_words(ngrams, threshhold + 1, ptr-1)
    if skipped_matches is None:
      skipped_matches = set()
    
    # Matches that use this ngram
    matches = get_similar_words(ngrams, threshhold, ptr-1)
    included_matches = ngram_words.intersection(matches) if matches is not None else ngram_words

    return included_matches.union(skipped_matches)

def parse(query_word):
  query_word = normalize(query_word)

  # Step 1: Create list of Ngrams
  ngrams = list()
  for i in range(N, len(query_word) + 1):
    ngrams.append(query_word[i-N : i])

  # Step 2: Get similar words
  similar_words = get_similar_words(ngrams)
  if similar_words is None:
    raise Exception("BAD DATASET - Dataset doesn't contain such N-grams")

  # Step 3: Return one with minimum distance
  min_dist = inf
  min_dist_word = None
  for word in similar_words:
    edit_distance = get_edit_distance(query_word, word)
    if edit_distance < min_dist:
      min_dist = edit_distance
      min_dist_word = word
  return min_dist_word, min_dist

if __name__ == '__main__':
  n_input = input('What type of N-gram do you want to generate(2: bigram, 3: trigram and so on): ')
  if n_input.isdecimal() and int(n_input, base=10) >= LOWEST_N:
    set_N(int(n_input, base=10))
  else:
    print(f'Invalid Input. Falling Back on default value: {LOWEST_N}!')
    set_N(LOWEST_N)
  generate_ngram_index(DATASET_DIR)

  while True:
    query_word = input('Enter your query(q to quit):')
    if query_word.lower() == 'q':
      break
    else:
      try:
        corrected_word, min_diff = parse(query_word)
        if min_diff == 0:
          print("No correction found!")
        elif min_diff == inf:
          print("No similar words found!")
        else:
          print("Corrected Word: " + corrected_word)
      except Exception as e:
        print(str(e))
  
  print('Exiting ....')
    