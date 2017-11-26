import pickle
from nltk.tokenize import sent_tokenize


def dump(obj,filename):
    filehandler = open(filename,"wb")
    pickle.dump(obj,filehandler)
    filehandler.close()


def load(filename):
    file = open(filename,'rb')
    obj = pickle.load(file)
    file.close()
    return obj


def get_sentence_corpus(update_corpus):
    result = []
    for v in update_corpus:
        sent = sent_tokenize(v)
        result.append(sent)
    return result
# dump(result, 'update_corpus_sent.pkl')

