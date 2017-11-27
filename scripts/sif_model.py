import numpy as np
from sklearn.decomposition import TruncatedSVD
from argparse import ArgumentParser
from vocab_utils import *
from data_utils import *
import pprint
import phrase_tagger
from sklearn.preprocessing import normalize

def parse_args():
    parser = ArgumentParser(description= "SIF Embedding")

    # data paths
    data_path = "../corpus-tagged/book/" ## modify the paths according to the folder structure
    parser.add_argument('--data_path', default=data_path, type = str)
    parser.add_argument('--sentence_file', default="../corpus-tagged/book/book_union_linewise.pkl",type=str)
    parser.add_argument('--embeddings_file', default='../embeddings/w2v-books-union-300d.txt',type=str)


    #save file path
    parser.add_argument('--vocab_file', default=data_path+"vocab-union.txt",type=str)
    parser.add_argument('--trimmed_embedding_file', default=data_path+"trimmed_embedding-union.npz", type=str)

    parser.add_argument('--object_file', default=data_path+"object_file-union.npz", type=str)
    parser.add_argument('--concept_filenames', default="../concepts/concepts-union-clean.txt", type=str)

    # vocab building
    parser.add_argument('--build', dest='build_vocab', action='store_true')
    parser.set_defaults(build_vocab=False)

    # remove pca component
    parser.add_argument('--no_PCA', dest='pca', action='store_false')
    parser.set_defaults(pca=True)

    parser.add_argument('--n_components', default=1, type=int)


    args = parser.parse_args()
    return args

class SIF_Model(object):
    def __init__(self, args):
        self.args = args
        self.alpha = 1e-3
        self.data = self.getData()
        self.vocab = args.vocab
        self.word_embeddings = args.word_embeddings ### Loaded from vocab_utils in main() below, filename passed above
        self.VOCAB_SIZE = len(self.vocab) ### Loaded from vocab_utils in main() below, filename passed above
        self.vocab_count = self.load_word_counters()
        self.getConceptVectors()
        # self.loadModel()

    def train(self):
        self.weights = self.getWeightedProbabilities() #getWeight corrosponding to each word
        self.sent_indices, self.sent_mask = self.createStructure() #getSequence of word indices for every sentence
        
        #get weights mapping to sentence sequence
        self.sent_weights = self.seq2weight(self.sent_indices, self.sent_mask, self.weights)
        print self.sent_weights.shape
        # self.saveEntries()
        
        #get trainEmbedding computed using word_embedding which was loaded before 
        self.trainEmbeddings = self.SIF_embedding(self.word_embeddings, self.sent_indices, self.sent_weights)
        print "Model Training Completed. Start Saving"

    # def saveEntries(self):
    #     np.savez_compressed(self.args.object_file, weights = self.weights,
    #                         sent_weights = self.sent_weights, sent_indices = self.sent_indices)
    #     print "done"
    #
    # def loadEntries(self):
    #     with np.load(self.args.object_file) as data:
    #         self.weights = data['weights']
    #         self.sent_indices = data['sent_indices']
    #         self.sent_weights = data['sent_weights']
    #     print "Entries Loaded"

    # def loadAndTrain(self):
    #     self.loadEntries()
    #     print "Begin Training"
    #     self.trainEmbeddings = self.SIF_embedding(self.word_embeddings, self.sent_indices, self.sent_weights)

    def saveModel(self):
        np.savez_compressed(self.args.object_file, weights = self.weights, pca_components = self.pc, sif_embeddings = self.trainEmbeddings,
                            )
        print "Model Saved"


    def loadModel(self):
        with np.load(self.args.object_file) as data:
            self.weights = data['weights']
            self.pc = data['pca_components']
            self.trainEmbeddings = data['sif_embeddings']
        print "Model Loaded"


    def getData(self):
        with open(self.args.sentence_file) as f:
            data = pickle.load(f)
            data = data[0]
            data = [x.split() for x in data]
            return data

    def load_word_counters(self):
        vocab_count = Counter()
        for line in self.data:
            vocab_count.update(line)

        # Filter Count
        filtered_dict = {k:v for k,v in vocab_count.iteritems() if k in self.vocab}
        return filtered_dict

    def getWeightedProbabilities(self):
        """
        Computes a array of 1*VOCAB_SIZE stores weights corrosponding to each word
        INPUT: vocab[word] : index mapping
        INPUT" vocab_count[word]: count mapping
        return: weights TFIDF type *** Add TFKLD here
        """
        freqs = np.zeros((1, self.VOCAB_SIZE), dtype="float")
        for word in self.vocab:
            idx = self.vocab[word]
            freqs[0, idx] = self.vocab_count[word]

        probs = freqs / np.sum(freqs)
        weights = self.alpha / (self.alpha + probs)
        return weights

    def printShapes(self):
        """
        print statements for debugging
        """
        print "Vocab Size: %s"%(self.VOCAB_SIZE)
        print self.weights.shape
        print self.sent_indices.shape
        print self.sent_indices.shape

    def prepare_data(self,list_of_seqs):
        """
        Helper function for create Structure
        param: list of sequence of a single sentence
        return: x, mask: x stores sequence of word indices in a sentence, mask stores 1 corrosponding to indices
        masks helps in indentifying variable lenght of sentence
        """
        lengths = [len(s) for s in list_of_seqs]
        n_samples = len(list_of_seqs)
        maxlen = np.max(lengths)
        print maxlen
        x = np.zeros((n_samples, maxlen)).astype('int32')
        x_mask = np.zeros((n_samples, maxlen)).astype('float32')
        for idx, s in enumerate(list_of_seqs):
            x[idx, :lengths[idx]] = s
            x_mask[idx, :lengths[idx]] = 1.
        x_mask = np.asarray(x_mask, dtype='float32')
        return x, x_mask

    def getConceptVectors(self):
        """
        Get words embeddibngs corrosponding to concept names
        To be used to see distance of a given sentence to a concept in getRanking function
        """
        concepts = []
        with open(self.args.concept_filenames) as f:
            data  = f.read()
            data = data.split('\n')
            for line in data:
                concepts.append('t_'+"_".join(line.split())+'_t')

        concepts = list(set(concepts))
        self.concepts = filter(lambda x : x in self.vocab, concepts)
        concepts_indices = filter(lambda x : x is not None, map(self.vocab.get, self.concepts))
        print len(concepts_indices)
        self.concepts_embeddings = self.word_embeddings[concepts_indices]
        self.concepts_embeddings = normalize(self.concepts_embeddings)

    def createStructure(self):
        """
        return x, mask: x stores sequence of word indices in a sentence, mask stores 1 corrosponding to indices
                masks helps in indentifying variable lenght of sentence
        
        """
        sentence_indices = []
        sentence_weights = []
        for line in self.data:
            indices_list = filter(lambda x : x is not None, map(self.vocab.get, line))
            # weight_list = []
            # for idx in indices_list:
            #     weight_list.append(self.weights[0,idx])
            sentence_indices.append(indices_list)
            # sentence_weights.append(weight_list)
        x1, m1 = self.prepare_data(sentence_indices)
        return x1, m1
        # sentence_weights = np.asarray(sentence_weights, dtype='float')
        # sentence_indices = np.asarray(sentence_indices, dtype='int')
        # return sentence_indices, sentence_weights

    def seq2weight(self, seq, mask, weight4ind):
        """
        param: sequence of word indices, mask of word indices of a sentence
        param: weight4ind weights corrosponding to word indices calculated using getWeightedProb
        return: weight as same shape as seq, weights of words corrosponding to sequence of sentences 
        """
        weight = np.zeros(seq.shape).astype('float32')
        for i in xrange(seq.shape[0]):
            for j in xrange(seq.shape[1]):
                if mask[i, j] > 0 and seq[i, j] >= 0:
                    weight[i, j] = weight4ind[0, seq[i, j]]
        weight = np.asarray(weight, dtype='float32')
        return weight

    def get_weighted_average(self, We, x, w):
        """
        Compute the weighted average vectors
        :param We: We[i,:] is the vector for word i
        :param x: x[i, :] are the indices of the words in sentence i
        :param w: w[i, :] are the weights for the words in sentence i
        :return: emb[i, :] are the weighted average vector for sentence i
        """
        n_samples = x.shape[0]
        emb = np.zeros((n_samples, We.shape[1]))
        for i in xrange(n_samples):
            emb[i, :] = w[i, :].dot(We[x[i, :], :]) / (np.count_nonzero(w[i, :]) + 1.0)
        return emb

    def compute_pc(self,X, npc=1):
        """
        Compute the principal components. DO NOT MAKE THE DATA ZERO MEAN!
        :param X: X[i,:] is a data point
        :param npc: number of principal components to remove
        :return: component_[i,:] is the i-th pc
        """
        svd = TruncatedSVD(n_components=npc, n_iter=7, random_state=0)
        svd.fit(X)
        return svd.components_

    def remove_pc(self, X, npc=1):
        """
        Remove the projection on the principal components
        :param X: X[i,:] is a data point
        :param npc: number of principal components to remove
        :return: XX[i, :] is the data point after removing its projection
        """
        pc = self.compute_pc(X, npc)
        self.pc = pc
        if npc == 1:
            XX = X - X.dot(pc.transpose()) * pc
        else:
            XX = X - X.dot(pc.transpose()).dot(pc)
        return XX

    def SIF_embedding(self, We, x, w):
        """
        Compute the scores between pairs of sentences using weighted average + removing the projection on the first principal component
        :param We: We[i,:] is the vector for word i
        :param x: x[i, :] are the indices of the words in the i-th sentence
        :param w: w[i, :] are the weights for the words in the i-th sentence
        :param params.rmpc: if >0, remove the projections of the sentence embeddings to their first principal component
        :return: emb, emb[i, :] is the embedding for sentence i
        """
        emb = self.get_weighted_average(We, x, w)
        print emb.shape
        print "Computed Embeddings"
        if self.args.pca:
            emb = self.remove_pc(emb,self.args.n_components)
        return emb

    def getSIFEmbedding(self, sent):
        """
        Get Sentence embedding for a new sentence
        INPUT: Sentence word indices sequence
        INPUT: word_embedding
        INPUT: weights 1*VOCABSIZE weights corrosponding to each word
        RETURN: Sentence embedding
        """
        corpus = [sent]
        concept_filenames = self.args.concept_filenames.split(",")
        clean_pages_space = map(lambda x: " " + "  ".join(x.split()),
                                corpus)  ##this line is **important** introduce double spaces
        tagged_corpus = phrase_tagger.concept_tagging(clean_pages_space, concept_filenames, "t")
        tagged_corpus.load_concepts()
        corpus_result = tagged_corpus.tag_corpus()
        result = corpus_result[0]
        words = result.split()
        indices_list = filter(lambda x: x is not None, map(self.vocab.get, words))
        #get average

        count = len(indices_list)
        sent_embedding = np.zeros((300),dtype="float32")
        for idx in indices_list:
            sent_embedding = sent_embedding + self.word_embeddings[idx,:] * self.weights[0,idx]

        if count <=0 :
            print "Empty Sentence"

        sent_embedding = sent_embedding.reshape(1,sent_embedding.shape[0])
        print sent_embedding.shape
        # a = np.dot(self.pc, self.pc.T)
        print self.pc.shape
        #remove component
        if self.args.pca:
            sent_embedding = sent_embedding - sent_embedding.dot(self.pc.transpose())*self.pc

        sent_embedding/=count

        return sent_embedding


    def getRanking(self, sent,n=10):
        """
        Get top10 concepts closest to sentence embeddings
        """
        sent = sent.lower()
        sent = cleanContentPage(sent)
        sent_embedding = normalize(self.getSIFEmbedding(sent))
        print sent_embedding.shape
        print self.concepts_embeddings.shape
        conceptDistances = np.dot(self.concepts_embeddings, sent_embedding.T)
        conceptDistances = conceptDistances.reshape(conceptDistances.shape[0])
        rankedIndices = conceptDistances.argsort()[-n:][::-1]
        print rankedIndices
        for idx in rankedIndices:
            print self.concepts[idx]


##**** DOSENT EXECUTE VOCAB ALREADY BUILT DEFAULT FALSE ****##
args = parse_args()
print pprint.pformat(args.__dict__)
if args.build_vocab:
    dataset = Dataset(args.sentence_file, args.embeddings_file)
    vocab = dataset.generate_vocab()

    #write to files
    write_vocab(vocab, args.vocab_file)
    vocab = load_vocab(args.vocab_file)
    export_trimmed_w2v_vectors(vocab, args.embeddings_file, args.trimmed_embedding_file)
    
### *****LOAD VOCAB AND WORD EMBEDDINGS HERE FROM VOCAB UTILS FUNCTION****###
args.vocab = load_vocab(args.vocab_file)
print len(args.vocab)
args.word_embeddings = get_trimmed_w2v_vectors(args.trimmed_embedding_file)
print args.word_embeddings.shape

sif_model = SIF_Model(args)
# sif_model.printShapes()


