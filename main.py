import os
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

ps = PorterStemmer()


documentList = []
documentsProcessedWords = {}
documentCount = 0
for file in os.listdir("./dataset"):
    documentCount = documentCount + 1
    if file.endswith(".txt"):
        documentList.append(str(file))
        with open('dataset/'+file, 'r') as myfile:
            data = myfile.read()
            words = word_tokenize(data)
            for w in words:
                if w not in documentsProcessedWords:
                    documentsProcessedWords[w] = {str(documentCount)}
                else:
                    documentsProcessedWords[w].add(str(documentCount))
print(documentsProcessedWords)
                

