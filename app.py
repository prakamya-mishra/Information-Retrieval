from inverted_index import *

OBJ_FILENAME = 'inverted-index.obj'
DATASET_DIR = 'dataset'


if __name__ == '__main__':
  try:
    invertedIndex = InvertedIndex.load(OBJ_FILENAME)
  except FileNotFoundError:
    invertedIndex = InvertedIndex()
    invertedIndex.generateFromDir(DATASET_DIR)
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
  while True:
    query = input('Enter your query(q to quit):')
    if query.lower() == 'q':
        break
    