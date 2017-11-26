
# coding: utf-8

# In[33]:

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from collections import Counter 
from bs4 import BeautifulSoup 
import nltk
import re
#from nltk.tokenize import word_tokenize
#from nltk.util import ngrams
from sklearn.feature_extraction import text 
stop_words = text.ENGLISH_STOP_WORDS
#from nltk.stem import WordNetLemmatizer
#wordnet_lemmatizer = WordNetLemmatizer()
from nltk.stem import SnowballStemmer
snowball_stemmer = SnowballStemmer("english")
from nltk.tokenize import sent_tokenize
import argparse


# In[26]:

def getCleanText(text, stemming = False, word_size=-1):
    parse_text = BeautifulSoup(text).get_text()
    parse_text = re.sub(r'\([^)]*\)', '', parse_text)
    letters_only = re.sub(r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' url ', 
                          parse_text, flags=re.MULTILINE)
    
    
    letters_only = re.sub("[^a-zA-Z0-9\.:']",  
                      " ",                   
                      letters_only)
    
    
    letters_only = letters_only.replace('\n',"")
    letters_only = letters_only.replace('\r',"")
    letters_only = re.sub('[.]{2,}', '. ', letters_only)
    letters_only = re.sub(r'\b[0-9]+\b\s*', '', letters_only)
    
    #print letters_only
    
    
    
    #words = word_tokenize(lower)
    words = CountVectorizer().build_tokenizer()(letters_only.lower())
    
    #sent_tokenize_list = sent_tokenize(text.lower().decode('utf8'))
    

    #print "tokenization done"
    #print sent_tokenize_list
   
    #sent_words = [CountVectorizer().build_tokenizer()(sent) for sent in sent_tokenize_list]
    
    
    
    #words = CountVectorizer().build_tokenizer()(letters_only.lower())
    
    #print sent_words
    
    meaningful_words = [w for w in words if len(w) > word_size and len(w)<40 and w not in stop_words]    
    #lem_words = [wordnet_lemmatizer.lemmatize(w) for w in  meaningful_words]
   
    
    if stemming:
        #print "stemming"
        stem_words = [snowball_stemmer.stem(w) for w in meaningful_words]
        clean_text = " ".join(stem_words) 
    else:
        clean_text = " ".join(meaningful_words)

    return clean_text


# In[29]:

def load_concepts(filename, stemming):
    f = open(filename, "r")
    concepts = f.readlines()
    concepts = [getCleanText(concept, stemming) for concept in concepts]
    concepts = filter(lambda x: x!="", concepts)
    f.close()
    return concepts


# In[30]:

def write_concepts(concepts,filename):
    concept_file = open(filename,"wb")
    for concept in concepts:
        concept_file.write("%s\n" % concept)


# In[31]:

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="post aggregation of sentences")
    
    parser.add_argument('--concepts', dest='concepts_file', type=str,
                    help='book/video/wiki concepts', default="concepts_wiki.txt")
    
    parser.add_argument('--output', dest='output', type=str,
                    help='output after cleaning', default="concepts_clean.txt")
    

    args = parser.parse_args()

    concepts_file = args.concepts_file
    concepts = load_concepts(concepts_file, stemming=False)
    
    write_concepts(concepts, args.output)


# In[ ]:



