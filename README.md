# Music-Search-Engine

This Search Engine is builded on all .html file (saved in local) of azlyrics.com.
Our Search Engine is organized in 3 Python files:

**Scraping.py:** Class that contains all method for extracting data from html file, and generates json file.
**Index.py:** Class that contains all method for generate Vocabulary and Inverted Index from json files.
**Search.py:** Class that contains all method for the search function.

## Scraping.py

The most important method of this class is **parsingAZLyrics(path).** This method takes in input a path to the directory that contains all the html files and return a dictionary for each html file.
A second function of this class, **HTMLtoJSON(path,az),** creates the json file that contains a dictionary generated above.
In a first version of this Search Engine we stored all the json files on local disk, but now in the ‘main’ we have modified the code to upload all json files in a local MongoDB collection named LyricsDB.

## Index.py

In this python class the first method that we have realized is **wordNorm(text).** This function takes in input a string and return the normaliezed string. For the pre-processing of lyrics and queries we have used Python’s libraries NLTK to remove stopwords, punctuation and 
to stem the text. Another library that we have used in this pre-processing part is Enchant. We noticed that most of the songs were written in English  (81,000 out of 86,000 total songs), thus we decided to consider, in the vocabulary, only the English words. This is allowed by **check(word)** method of Enchant library.
All the methods of Index.py work on local json files stored in a directory named LyricsDB.
Vocabulary of Search Engine is built by **createVocab(allwords)** that takes  in input the result of an another function (**allWords(jsondir)**) that returns all the normalized words of all the lyrics song.
The vocabulary assigns at every word an ID: {term : termID}.
Instead, the inverted index is built from **invertedIndex(vocab, jsondir)**, that takes in input the vocabulary and the directory containing all the json files.
The Inverted Index is a dictionary that assigns at every vocabulary’s termID a list of tuples such as: 
**{termID : [(json_name, TF{term,filejson})]}**

## Search.py

This class contains all methods for search function. The first step is retrieve the name of the documents that contains the word we want to search (allowed by **toSearch(query, invertedIndex, vocab)** ).  The second step is to transform into an array the query (**makeQuery(query, vocab)** ) and the lyrics of the song that contains the query (**text_in_vector(text_song, invertedIndex, vocab, json_name)**). 
In the vector of the song, we put the relative TF-IDF value for each occurrence of every words of the vocabulary that is in the song, 0 otherwise. In the vector of the query, we put 1 for each occurrence of every words of the vocabulary that is in the query, 0 otherwise.
Thus, now the two vector have the same length (len(vocab)) and we can compute the cosine similarity for each lyrics song: 
**get_cosine(query_vector, lyrics_vector)**

In the union query we return the top 10 song based on the cosine similarity value ordinated by a max heap.

![alt text](http://it.tinypic.com/r/2nkigzd/9)

For the “and-query” we normalized the tf-idf vectors and then used the skleran.cluster library for implement KMeans.

![alt text](http://it.tinypic.com/r/11mc95e/9)

In conclusion, we built a wordcloud based on a note for each cluster in order to understand which words of the cluster have more occurences and are more important.

![alt text](http://it.tinypic.com/r/4ha71y/9)

