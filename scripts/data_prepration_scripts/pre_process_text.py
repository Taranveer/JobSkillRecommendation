
# coding: utf-8

# In[5]:

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from collections import Counter 
from bs4 import BeautifulSoup 
import nltk
import re
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from nltk.corpus import stopwords # Import the stop word list 
from nltk.stem import WordNetLemmatizer
wordnet_lemmatizer = WordNetLemmatizer()
from nltk.stem import SnowballStemmer
snowball_stemmer = SnowballStemmer("english")
from nltk.tokenize import sent_tokenize
import argparse


# In[2]:

import pickle
def dump(obj,filename):
    filehandler = open(filename,"wb")
    pickle.dump(obj,filehandler)
    filehandler.close()

def load(filename):
    file = open(filename,'rb')
    obj = pickle.load(file)
    file.close()
    return obj


# In[3]:

def getCleanText(text, stemming = False, word_size=-1):
    parse_text = BeautifulSoup(text).get_text()
    parse_text = re.sub(r'\([^)]*\)', '', parse_text)
    letters_only = re.sub(r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' url ', 
                          parse_text, flags=re.MULTILINE)
    
    
    letters_only = re.sub("[^a-zA-Z0-9\.:']",  
                      " ",                   
                      letters_only)
    
    
    letters_only = letters_only.replace('\n'," ")
    letters_only = letters_only.replace('\r'," ")
    letters_only = re.sub('[.]{2,}', '. ', letters_only)
    
    #print letters_only
    
    
    
    #words = word_tokenize(lower)
    #words = CountVectorizer().build_tokenizer()(letters_only.lower())
    sent_tokenize_list = sent_tokenize(text.lower().decode('utf8'))
    

    #print "tokenization done"
    #print sent_tokenize_list
   
    sent_words = [CountVectorizer().build_tokenizer()(sent) for sent in sent_tokenize_list]
    
    
    
    #words = CountVectorizer().build_tokenizer()(letters_only.lower())
    
    #print sent_words
    
    #meaningful_words = [w for w in words if len(w) > word_size and len(w)<40]    
    #lem_words = [wordnet_lemmatizer.lemmatize(w) for w in  meaningful_words]
   
    
    if stemming:
        #print "stemming"
        clean_text = map(lambda s: " ".join(map(lambda w: snowball_stemmer.stem(w), s)), sent_words)
        #clean_text = " ".join(stem_words) 
    else:
        clean_text = [" ".join(sent) for sent in sent_words]

    return clean_text


# In[6]:

def join_sentences(corpus):
    return map(lambda doc: " <s_d_e_l> ".join(doc), corpus)

def join_documents(corpus):
    return " <d_d_e_l> ".join(corpus)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    
    parser.add_argument('--corpus', dest='corpus_file', type=str,
                    help='book/video/wiki corpus', default="clean_pages")

    parser.add_argument('--output', dest='output', type=str,
                    help='output after cleaning', default="corpus_parsed")



    args = parser.parse_args()

    corpus_file = args.corpus_file
    corpus = load(corpus_file)
    
    corpus_clean = []
    
    for doc in corpus:
        corpus_clean.append(getCleanText(doc, stemming=False))
    
    corpus_clean_sent_concat = join_sentences(corpus_clean)
    corpus_clean_doc_concat = join_documents(corpus_clean_sent_concat)
    
    dump(corpus_clean_doc_concat, args.output)


# In[ ]:



