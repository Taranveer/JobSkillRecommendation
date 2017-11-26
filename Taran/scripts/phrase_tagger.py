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
from operator import itemgetter
import argparse

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



def read_corpus(corpus_file):
    f = open(corpus_file, 'rb')

    objs = []
    while 1:
        try:
            d = pickle.load(f)
            objs.append(d)
        except EOFError:
            break
    corpus = map(lambda x: x[1], objs)
    return corpus


class concept_tagging:
    def __init__(self, corpus, concept_filenames, tag):
        """
        Get arguments 
        """
        self.concept_filenames = concept_filenames
        self.corpus = corpus
        self.tag = tag

    # ----------------Helper functions-------------#
    def process_concepts(self, text, word_size=-1):
        """
        process_concepts only runs once
        """
        return self.getCleanText(text, word_size)

    def word_replace(self, text, phrase, replace):
        """
        word replace makes sure multiple words can also be tagged
        even if part of the next word was part of the conepts
        eg:
        concept: kernel density estimator 
        stemmed concept (phrase) : kernel desnsity estim ("searh string")
        text: kernel density estimation 
        ouput: kernel desnity estimator
        Since stemmed conept substring of text.
        """
        pattern = r'(\w*%s\w*)' % phrase
        text_rep = re.sub(pattern, replace, text)
        return text_rep

    def getCleanText(self, text, word_size=-1):
        """
        Just all sorts of pre-processing
        """
        parse_text = BeautifulSoup(text).get_text()
        parse_text = re.sub(r'\([^)]*\)', '', parse_text)
        letters_only = re.sub(r'http[s]?:\/\/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                              ' url ',
                              parse_text, flags=re.MULTILINE)

        letters_only = re.sub("[^a-zA-Z0-9\.:']",
                              " ",
                              letters_only)

        letters_only = letters_only.replace('\n', " ")
        letters_only = letters_only.replace('\r', " ")
        letters_only = re.sub('[.]{2,}', '. ', letters_only)


        words = CountVectorizer().build_tokenizer()(letters_only.lower())

        meaningful_words = [w for w in words if len(w) > word_size and len(w) < 40]

        clean_text = "  ".join(meaningful_words)
        return clean_text

    # ----------------Main Functions---------------#
    def stem_concepts(self, concept):
        """
        find concept by searching for stemmed words 
        """
        concept_break = concept.split("  ")
        concept_break[-1] = snowball_stemmer.stem(concept_break[-1])
        find_word = " " + "  ".join(concept_break)
        return find_word

    def join_phrase(self, concept):
        """
        Added delim which protects a conept from replacing it again.
        """
        #print "In join phrase concept:", concept
        concept_break = concept.split("  ")
        tag = self.tag
        left_tag = " " + tag + "_"
        right_tag = "_" + tag + " "
        joint_phrase = "_".join(concept_break)
        replace_string = left_tag + joint_phrase + right_tag
        return replace_string

    def parse_sort_concepts_by_word(self, concepts_all):
        """
        sort concepts so that concepts with higher no of words are replaced first
        and added delim so that it can't be replaced again.
        """
        concepts_all_tup = [(ent, self.stem_concepts(ent), self.join_phrase(ent), len(ent.split(" ")), len(ent)) for ent
                            in concepts_all]
        concepts_all_tup = sorted(concepts_all_tup, key=itemgetter(3, 4), reverse=True)
        return concepts_all_tup

    def phrase_tagger(self, text):
        """
        Phrase_tagging 
        After all concepts have find_word and replace string
        we do word_replace
        """
        tot = len(self.concepts_all_tup)
        for concept, find_word, replace_string, nwords, nlen in self.concepts_all_tup:
            print concept
            text = self.word_replace(text, find_word, replace_string)
        return text

    def load_concepts(self):
        """
        Load concepts from all the files specified
        Process the conepts
        """
        concepts_all = []
        for source_name in self.concept_filenames:
            f = open(source_name, 'rb')
            concepts = f.readlines()
            f.close()

            concepts = map(self.process_concepts, concepts)
            concepts_all = concepts_all + concepts

        concepts_all = filter(lambda x: x != "" and x != " ", concepts_all)
        self.concepts_all_tup = self.parse_sort_concepts_by_word(concepts_all)

    def tag_corpus(self):
        """
        tagg everything in a list
        """
        corpus = [self.phrase_tagger(doc) for doc in self.corpus]
        return corpus


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Give number of questions')
    parser.add_argument('--concept_filenames', dest='concept_filenames', type=str,
                        help='files to take concepts from', default="concept-enteries.txt")

    parser.add_argument('--corpus', dest='corpus_file', type=str,
                        help='book/video/wiki corpus', default="clean_pages")

    parser.add_argument('--output', dest='output', type=str,
                        help='output after tagging', default="corpus_parsed")

    parser.add_argument('--tag', dest='tag', type=str,
                        help='tag like t for textbook/v for videos/w for wikipedia', default="c")

    #parser.add_argument('--concept_tag_out', dest='tag_out', type=str, default = "concepts_all_tup")

    args = parser.parse_args()

    corpus_file = args.corpus_file
    corpus = load(corpus_file)  ## corpus should be a list of list of documents
    

    corpus = [corpus] ## there is some bug this fixes it.
    concept_filenames = args.concept_filenames.split(",")
    clean_pages_space = map(lambda x: " " + "  ".join(x.split()),  corpus)  ##this line is **important** introduce double spaces
    tagged_corpus = concept_tagging(clean_pages_space, concept_filenames, args.tag)
    tagged_corpus.load_concepts()
    corpus_result = tagged_corpus.tag_corpus()
    #tag_out_tup = map(lambda x: x[2],tagged_corpus.concepts_all_tup)
    #dump(tag_out_tup, args.tag_out)
    dump(corpus_result, args.output)






# #### After you have loaded your concepts use the below statement to tag all the corpus u have passed earlier






