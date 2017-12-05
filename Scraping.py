import glob
from bs4 import BeautifulSoup
import os, errno
import json
from os.path import expanduser


# INSERT YOUR PATH TO lyrics_collection DIRECTORY:
directory = "/Users/IvanFerrante/Desktop/lyrics_collection/"

def parsingAZLyrics(path):
    # Scraping function with Beautiful soup method
    # Extract artist and title through itemprop tag
    # Remove all </br> tag from html page
    # Extract the text of the songs from id tag
    # Extract the URL from class = fb-like
    # Store all this information for every song in a dictionary. One dict for every song.
    az = {}
    page = path
    soup = BeautifulSoup(page.read(), "html.parser")

    artists = soup.find_all(itemprop='title')
    az['artist'] = artists[1].text
    az['title'] = artists[2].text

    for br in soup.findAll('br'):
        br.extract()
    lyrics = soup.find(id='content_h')
    if lyrics:
        az['lyrics'] = lyrics.get_text(separator=' ')
    else:
        raise Exception('COPYRIGHT!')

    url = soup.find_all('div', {'class':'fb-like'})
    for link in url:
        az['URL'] = link['data-href']

    return(az)


def create_directory(path):
    #Create a Directory on the Desktop to store all JSON file
    try:
        os.makedirs(expanduser('~/Desktop/')+path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def HTMLtoJSON(path,az):
    #Generate one file JSON given the path of the file and the dictionary (az)
    path = path.replace('.html','.json')
    file = open(path, 'w')
    try:
        json.dump(az, file)
    except:
        pass





#--------------------------------------------------- MAIN -------------------------------------!
'''from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['songs']
collection = db['LyricsDB']


create_directory('LyricsDB')
counter = 0
for filepath in glob.glob(os.path.join(directory, "*.html")):
    with open(filepath, "r",encoding='utf-8', errors='ignore') as f:
        content = f
        path = filepath.replace(directory, '')
        path = path.replace('.html', '.json')
        try:
            counter += 1
            k = parsingAZLyrics(content)
        except Exception as e:
            counter -= 1
            print(filepath, '------->' + str(e))  #Copyright file
            continue
        fullpath = os.path.join(expanduser('~/Desktop/LyricsDB/'),path)
        if k['lyrics']:
            db['LyricsDB'].insert_one({'_id': path, 'Info':k})
            print('FILE ON MONGODB--->', counter)
        #HTMLtoJSON(fullpath,k)
        #print(fullpath,'-------> SUCCESS' + ' ' +  str(counter))'''

