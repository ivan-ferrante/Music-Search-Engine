import Index as ind
from os.path import expanduser
import json
import codecs
import os.path
import time
import heapq, numpy
from sklearn.cluster import KMeans
from pymongo import MongoClient
from wordcloud import WordCloud
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


def toSearch(input, invertedInd, vocab):
# Splits and normalize inputs and return the list of the doc name with respective tf_idf
    wordToFind = ind.wordNorm(input)
    IDs = []
    doclist = []
    for word in wordToFind:
        IDs.append(vocab[word])
    for id in IDs:
        doclist.extend(invertedInd[str(id)])
    return (doclist)


def text_in_vector(text_song, invIndex, vocab, json_name):
# Build number vector from lyrics song mapped on vocabulary for cosine similarity
    word_vector = []
    text = ind.wordNorm(text_song)
    for v in vocab:
        if v in text:
            for (file, tf) in invIndex[str(vocab[v])]:
                if file == json_name:
                    word_vector.append(tf*ind.idf(invIndex,vocab[v]))
        else:
            word_vector.append(0)
    return (word_vector)


def makeQuery(input, vocab):
# Build number vector from query mapped on vocabulary for cosine similarity
    query_vector=[]
    wordToFind = ind.wordNorm(input)
    for v in vocab:
        if v in wordToFind:
            query_vector.append(1)
        else:
            query_vector.append(0)
    return (query_vector)


def get_cosine(vec1, vec2):
#This metod take two vectors of number and calculate the cosine similarity.
    vec_1 = numpy.array(vec1)
    vec_2 = numpy.array(vec2)

    numerator = sum(vec_1 * vec_2)
    sum1 = sum(numpy.power(vec_1,2))
    sum2 = sum(numpy.power(vec_2,2))
    denominator = numpy.sqrt(sum1) * numpy.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def unionQuery(query, invIndex, vocab):
# Union query return the 10 tuples (json_name, TF_IDF) of the searched query
    cosine = []
    q = ind.wordNorm(query)
    for x in q:
        searched = (toSearch(x, invIndex, vocab))
        vector_query = makeQuery(x, vocab)
        for (file, tf) in searched:
            song = ind.getText(file)
            tv = text_in_vector(song, invIndex, vocab, file)
            cosine.append([file,get_cosine(vector_query, tv)])
        heapq._heapify_max([cos for (file,cos) in cosine])
    return cosine[:10]

def getIntersection(query, invIndex, vocab):
# Get intersection find the name of the shared songs of the query
    q = ind.wordNorm(query)
    doc = set(tup[0] for tup in toSearch(q[0], invIndex, vocab))
    for x in q:
        doc2 = toSearch(x, invIndex, vocab)
        doc = set([tup[0] for tup in doc2]) & doc
    return doc


def andQuery(query, k, index, v):
# Construct the vector normalized used by kmeans algorithm, and return the word cloud of cluster.
    cluster = []
    u = getIntersection(query, index, v)
    mergeddata = []

    for file in u:
        song = ind.getText(file)
        tv = text_in_vector(song, index, v, file)
        norm = numpy.linalg.norm(tv)
        tv_norm = [i / norm for i in tv]
        cluster.append(tv_norm)
    kmeans = KMeans(n_clusters=k, init='random')

    try:
        kmeans.fit(cluster)
        c = kmeans.predict(cluster)

        for row in range(0, len(cluster)):
            line = cluster[row]
            line.append(int(c[row]))
            mergeddata.append(line)
        text = ""
        for i in range(k):
            print("Cluster " + str(k))
            for file in u:
                song = ind.getText(file)
                text = text + str(song)
            wordCloud(text)
            text = ""
        return c
    except:
        print('NO MATCH!')


def wordCloud(text):
# Create word cloud given a text
    mask = np.array(Image.open("notaio2.jpeg"))
    # Generate a word cloud image
    plt.figure(figsize=(15, 8))
    wordcloud = WordCloud(mask=mask, background_color="white", colormap="Reds", width=800, height=400).generate(
            text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()



############################# MAIN #############################



client = MongoClient('localhost', 27017)
db = client['songs']
for i in db['Vocab'].find({},{"_id":0}):
    vocab = i
index = ind.getInvertedIndex()

n = input('Type 0 for UNION query - Type 1 for AND query:')

if n == '0':
    query = input('Type query:')
    print('Searching query...')
    start_time = time.time()
    u = unionQuery(query, index, vocab)
    print('Execution Time:', (time.time() - start_time))
    for (value) in u:
        print('SCORE:',value)
elif n == '1':
    query = input('Type query:')
    k = input('Type number of cluster:')
    print('Searching query...')
    start_time = time.time()
    q = andQuery(query, int(k), index, vocab)
    print('Execution Time:', (time.time() - start_time))
    print(q)
else:
    print('INVALID CHOICE!')



