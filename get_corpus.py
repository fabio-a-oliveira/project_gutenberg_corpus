# =============================================================================
# Import libraries
# =============================================================================

import pandas as pd
from os import getcwd, chdir, listdir, mkdir
from os.path import join
import requests
from zipfile import ZipFile
from tarfile import TarFile
import re
import time

HOME = getcwd()
DEBUG = False

# =============================================================================
# Download and extract metadata file
# =============================================================================

URL = "https://www.gutenberg.org/cache/epub/feeds/rdf-files.tar.zip"

if 'temp' not in listdir():
    mkdir('temp')
    
if 'rdf-files.tar.zip' not in listdir('temp'):
    r = requests.get(URL).content
    filepath = join('temp', 'rdf-files.tar.zip')
    with open(filepath, 'wb') as file:
        file.write(r)

if 'rdf-files.tar' not in listdir('temp'):
    filepath = join('temp', 'rdf-files.tar.zip')
    file = ZipFile(filepath)
    file.extractall('temp')
    
if 'cache' not in listdir('temp'):
    filepath = join('temp', 'rdf-files.tar')
    file = TarFile(filepath)
    file.extractall('temp')
    
# =============================================================================
# Read all files and extract relevant metadata
# =============================================================================

path = join('temp', 'cache', 'epub')
names = []
titles = []
urls = []
languages = []
f = []

for folder in listdir(path):
    filename = listdir(join(path, folder))[0]
    filepath = join(path, folder, filename)
    
    f.append(folder)
    
    with open(filepath, encoding='utf-8') as file:
        content = file.read()
        
        # get the contents
        name = re.findall('<pgterms:name>(.*)</pgterms:name>', content)
        title = re.findall('<dcterms:title>(.*)</dcterms:title>', content, re.DOTALL)
        url = re.findall('<pgterms:file rdf:about="(https://www.gutenberg.org/files/.*/.*.txt)">', content)
        language = re.findall('<dcterms:language>(.*)</dcterms:language>', content, re.DOTALL)
        language = [language[0] if len(language)>0 else ''][0]
        language = re.findall('<rdf:value rdf:datatype="http://purl.org/dc/terms/RFC4646">(.*)</rdf:value>', language)
        
        # basic cleanup
        name = [name[0] if len(name)>0 else None][0]
        title = [title[0] if len(title)>0 else None][0]
        if title != None:
            title = title.replace('\n', ' ')
        url = [url[0] if len(url)>0 else None][0]
        language = [language[0] if len(language)>0 else None][0]
        
        # add contents to lists
        names.append(name)
        titles.append(title)
        urls.append(url)
        languages.append(language)

# =============================================================================
# Create data frame with data and export to .csv
# =============================================================================

df = pd.DataFrame({'Author':names,
                   'Title':titles,
                   'URL':urls,
                   'Language':languages,
                   'ref':f})

df.dropna(inplace=True)

filepath = time.strftime('project_gutenberg_corpus___%Y_%m_%d.csv')
df.to_csv(filepath, sep = '|', encoding='utf-8', index=False)

# =============================================================================
# Debug
# =============================================================================

if DEBUG == True:
    
    # check for unavailable titles
    
    df.loc[df.Title == '']
    
    with open(join('temp', 'cache', 'epub', '10005', 'pg10005.rdf')) as file:
        text = file.read()
    
    re.findall('<dcterms:title>(.*)</dcterms:title>', text, re.DOTALL)
    
    # check for unavailable URLs
    
    df.loc[df.URL == ''][['Title','URL', 'ref']]
    
    with open(join('temp', 'cache', 'epub', '10900', 'pg10900.rdf'), encoding='utf-8') as file:
        text = file.read()
    
    url = re.findall('<pgterms:file rdf:about="(https://www.gutenberg.org/files/.*/.*.txt)">', content)
    url[0]
    len(url)
    
    # check for unavailable Author
    
    df.loc[df.Author == '']
    
    with open(join('temp', 'cache', 'epub', '10', 'pg10.rdf'), encoding='utf-8') as file:
        content = file.read()
    
    re.findall('<pgterms:name>(.*)</pgterms:name>', content)
    re.findall('<pgterms:name>(.*)</pgterms:name>', content)
    
    # check for unavailable language
    
    df.loc[df.Language =='']
