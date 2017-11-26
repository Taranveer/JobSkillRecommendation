import numpy as np
import pickle
from collections import Counter
# shared global variables to be imported from model also
UNK = "$UNK$"
NUM = "$NUM$"


class Dataset(object):
    def __init__(self, filename, emb_file):
        self.filename = filename
        self.emb_file = emb_file


    def generate_vocab(self):
        text_vocab = self.get_vocabs()
        emb_vocab = self.get_w2v_vocab()
        self.vocab = text_vocab & emb_vocab
        # self.vocab.add(UNK)
        return self.vocab



    def get_vocabs(self):
        """
        This function just returns the vocabulary in the text
        :return:
        """
        print "Building vocab from text ..."
        with open(self.filename) as f:
            data = pickle.load(f)
            data = data[0]
            data = [x.split() for x in data]
            vocab_words= set()
            for line in data:
                vocab_words.update(line)
            print("- done. {} tokens".format(len(vocab_words)))
        return vocab_words

    def get_w2v_vocab(self):
        """
        This function return the vocabulary we have in the
        word embedding file
        :return:
        """
        print "Building vocab from embeddings ..."
        vocab = set()
        with open(self.emb_file) as f:
            for line in f:
                word = line.strip().split(' ')[0]
                vocab.add(word)
        print("- done. {} tokens".format(len(vocab)))
        return vocab

def write_vocab(vocab, filename):
    """
    Writes a vocab to a file
    :param vocab:
    :param filename:
    :return: write a word per line
    """

    print("Writing vocab...")
    with open(filename, "w") as f:
        for i, word in enumerate(vocab):
            if i != len(vocab) - 1:
                f.write("{}\n".format(word))
            else:
                f.write(word)
    print("- done. {} tokens".format(len(vocab)))

def load_vocab(filename):
    """
    Loads vocab from a file
    :param filename:
    :return: d: dict[word] = index
    """
    try:
        d = dict()
        with open(filename) as f:
            for idx, word in enumerate(f):
                word = word.strip()
                d[word] = idx

    except IOError:
        print "Generate the vocabulary and embeddings first"
    return d


def export_trimmed_w2v_vectors(vocab, glove_filename, trimmed_filename, dim=300):
    """Saves glove vectors in numpy array

    Args:
        vocab: dictionary vocab[word] = index
        glove_filename: a path to a glove file
        trimmed_filename: a path where to store a matrix in npy
        dim: (int) dimension of embeddings

    """
    embeddings = np.zeros([len(vocab), dim])
    with open(glove_filename) as f:
        for line in f:
            line = line.strip().split(' ')
            word = line[0]
            embedding = [float(x) for x in line[1:]]
            if word in vocab:
                word_idx = vocab[word]
                embeddings[word_idx] = np.asarray(embedding)

    np.savez_compressed(trimmed_filename, embeddings=embeddings)


def get_trimmed_w2v_vectors(filename):
    """
    Load embeddings vectors
    :param filename:
    :return:
    """
    try:
        with np.load(filename) as data:
            return data["embeddings"]

    except IOError:
        print "File: %s, NOT FOUND."%(filename)