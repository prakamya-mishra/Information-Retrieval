import os
import click

from inverted_index import PositionalInvertedIndex
from query import process_file, Parser

# Config
OBJ_FILENAME = 'inverted-index.obj'
DATASET_DIR = 'dataset'

# Functions
def generateFromDir(dirpath, inverted_index):
    # List all required dataset documents
    documents = [ document for document in os.listdir(dirpath) if document.endswith('.txt') ]
    print('\n\nParsing all files in the given directory: ' + dirpath + ' ...')
    print('Generating inverted-index ...')

    # Show progressbar while processing files
    with click.progressbar(documents) as docs:
      for data_file in docs:
        docId = inverted_index.insert_doc(data_file.replace('.txt', ''))
        processed_words = process_file(dirpath + '/' + data_file)
        for i in range(len(processed_words)):
          inverted_index.insert(processed_words[i], docId, i)
          # Creates a bi-word index
          if i > 0:
            inverted_index.insert(processed_words[i-1] + ' ' + processed_words[i], docId, i-1)

# Main
if __name__ == '__main__':
  try:
    invertedIndex = PositionalInvertedIndex.load(OBJ_FILENAME)
  except FileNotFoundError:
    invertedIndex = PositionalInvertedIndex()
    generateFromDir(DATASET_DIR, invertedIndex)
    invertedIndex.save(OBJ_FILENAME)
  except:
    print("<-- Unknown error has occured -->")
    raise
  
  # CSV Section
  should_print_CSV = input('Should we print a CSV for you(y or n)?')
  if should_print_CSV == 'y':
    filename = input('Enter output filename:')
    if filename.rfind('.csv') == -1:
      filename += '.csv'
    invertedIndex.createCSVFile(filename)
  else:
    print('Ignoring CSV ...')

  # Query Section
  parser = Parser(invertedIndex)
  while True:
    output_ids = []
    query = input('Enter your query(q to quit):')
    if query.lower() == 'q':
      break
    else:
      output_ids = parser.parse(query)
    print('### Relevant Documents ### \n')
    print('\n'.join(invertedIndex.convertToDocs(output_ids)))
    print()

  print('Exiting ....')
    