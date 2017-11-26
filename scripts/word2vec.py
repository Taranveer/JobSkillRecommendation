from base_model import base_model
import gensim
import multiprocessing
import math

class word2Vec(base_model):
    def load_model(self, path):
        """
        Loads the word2vec model from the given path
        :param path: path to the model
        :return: Model stored in the path
        """
        return gensim.models.word2vec.Word2Vec.load(path)

    def save_model(self, model, path):
        """
        Saves a word2vec model to the given path
        :param model: Word2vec model
        :param path: path to save the object
        :return: None
        """
        model.save(path)

    def train_model(self, data, windowSize = 10, epochs = 300):
        """
        Train a word2vec model on the given data.
        :param data:
        :param windowSize: Size of the window for the model
        :param epochs: Number of epochs to train the model
        :return: word2vec model trained on the given dataset
        """
        model = gensim.models.Word2Vec(data, size=300, window=windowSize, min_count=5, workers=multiprocessing.cpu_count(), iter = epochs)
        return model

    def get_similar_concepts(self, model, concept, concepts, ntops=5):
        """
        Fetches most similar concepts from a list of concepts based on the model
        :param model: word2vec model to get the similarity measure between two concepts
        :param concept: The target concept
        :param concepts: List of candidate concepts
        :param ntops: Number of concepts to return
        :return: List of ntops most similar concepts
        """
        scores = []
        for c in concepts:
            try:
                score = model.wv.similarity(concept, c)
                scores.append((c, score))
            except:
                pass
        scores = sorted(scores, cmp=self.custom_compare)
        return scores[:ntops]

    def custom_compare(self, item1, item2):
        """
        Helper compare function
        :param item1:
        :param item2:
        :return:
        """
        if item1[1] >= item2[1]:
            return -1
        else:
            return 1

    def get_frequent_concepts(self, model, concepts, ntop=50):
        """
        Returns the most frequent concepts used to train the model.
        :param model:
        :param concepts:
        :param ntop:
        :return:
        """
        counter = []
        for concept in concepts:
            try:
                count = model.wv.vocab[concept].count
                counter.append((concept, count))
            except:
                pass
        counter = sorted(counter, cmp=self.custom_compare)
        counter = [x[0] for x in counter]
        counter = list(set(counter))
        return counter[:ntop], counter

    def get_concept_complexity(self, data, concepts):
        complexity = {}
        for doc in data:
            doc_concepts = []
            for word in doc:
                if word in concepts:
                    doc_concepts.append(word)
            for word in set(doc_concepts):
                base_word = word.split("_")[1:-1].join("_")
                try:
                    complexity[word] += 1
                    complexity[base_word] += 1
                except:
                    complexity[word] = 1
                    complexity[base_word] = 1

        N = len(data)
        for concept in complexity.keys():
            complexity[concept] = math.log(N/(complexity[concept]))
        return complexity
