from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import os.path
from os.path import expanduser
import json
import codecs
from pymongo import MongoClient
import math
import enchant
from nltk.stem.snowball import SnowballStemmer

global D

client = MongoClient('localhost', 27017)
db = client['songs']
D = db['LyricsDB'].count()



def wordNorm(text):
    # Text normalizer: split the text in array without all spaces, stopwords, numbers
    # Stemming all words, and return only the english words.
    stemmer = SnowballStemmer("english")
    new_text = []
    tokenizer = RegexpTokenizer(r'\w+')
    word_list = tokenizer.tokenize(text.lower())
    filtered_words_en = [word for word in word_list if word not in stopwords.words('english')]
    stemming_words = [stemmer.stem(word) for word in filtered_words_en]
    d = enchant.Dict("en_US")
    for word in stemming_words:
        if not word.isdigit() and len(word)>1 and d.check(word):
            new_text.append(word)
    return new_text

def allWords(jsondir):
    # This function returns in an array all the words of all lyrics (saved as JSON file)
    k = []
    count = 0
    for file in os.listdir(jsondir):
        try:
            d = json.loads(codecs.open(jsondir + file, "r", encoding='ISO-8859-1').read())
            count += 1
        except:
            continue
        word_list = wordNorm(d['lyrics'])
        for item in word_list:
            k.append(item)
        print(count, '---> JSON IN VOCABULARY')
    return k

def createVocab(allwords):
    # This function take in input an array with all words, create the set and assign an ID to each term
    # vocabulary = {term : termID}
    vocabulary = {}
    word_list = sorted(list(set(allwords)))
    for ID, elem in enumerate(word_list):
        vocabulary.update({elem : ID})
    return vocabulary

def term_freq(term, txt):
# Compute the term frequencies in a given text
    count = 0
    if len(txt) <= 0:
        return 0
    else:
        for t in txt:
            if t == term:
                count += 1
        return count / len(txt)



def invertedIndex(vocab ,jsondir):
    # invIndex = {termID : (doc, TF)}
    invIndex = {}
    counter = 0
    for file in os.listdir(jsondir):
        try:
            d = json.loads(codecs.open(jsondir + file, "r", encoding='ISO-8859-1').read())
            counter += 1
            txt = wordNorm(d['lyrics'])
            for word in vocab:
                tf = term_freq(word, txt)
                if(tf>0):
                    try:
                        invIndex[vocab[word]] += [(file, tf)]
                    except:
                        invIndex[vocab[word]] = [(file, tf)]


            print(counter, "----->IN INVERTED INDEX!")
        except:
            print("!!!!!!!!!!!IN EXCEPT",file)
            pass
    return invIndex

def idf(invIndex, k):
    idf = math.log((D / len(invIndex[str(k)])))
    return(idf)

def getText(json_name):
    # Get lyrics text from MongoDB by json name file
    db = client['songs']
    collection = db['LyricsDB']
    cursor = collection.find({"_id": json_name}, {"_id": 0, "Info.lyrics": 1})
    for doc in cursor:
        text = doc['Info']['lyrics']
    return text

def getInvertedIndex():
    # Rebuild inverted index from MongoDB
    invertedIndex = {}
    db = client['songs']
    collection = db['Index']
    for i in collection.find({},{'_id':0}):
        invertedIndex.update({**i})
    return invertedIndex


################### MAIN ######################

'''k = allWords(expanduser('~/Desktop/LyricsDB/'))

#SAVE VOCABULARY AND INVERTED INDEX AS LOCAL FILE
v= createVocab(k)
file = open(expanduser('~/Desktop/vocab.json'), 'w')
try:
    json.dump(v, file)
except:
    pass

dizionario = invertedIndex(v,expanduser('~/Desktop/LyricsDB/'))
file2 = open(expanduser('~/Desktop/dizionario.json'), 'w')
try:
    json.dump(dizionario, file2)
except:
    pass

# INSERT VOCABULARY ON MONGODB
collection = db['Vocab']
v = json.loads(open(expanduser('~/Desktop/vocab.json'), 'r').read())
#db['Vocab'].insert(v)
for i in db['Vocab'].find({},{"_id":0}):
    vocab = i

# INSERT INVERTED INDEX ON MONGO DB    
collectionInd = db['Index']
index = json.loads(open(expanduser('~/Desktop/dizionario.json'), 'r').read())
for k,v in index.items():
    d = {k:v}
    db['Index'].insert(d)

'''
