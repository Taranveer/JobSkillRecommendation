import multiprocessing
from gensim import utils
from gensim.models.doc2vec import LabeledSentence, TaggedDocument
from gensim.models import Doc2Vec
import os
from scipy.spatial.distance import cosine
from sklearn.preprocessing import normalize

class base_model(object):
    def __init__(self):
        pass

    def load_model(self, path):
        """
        Load a pretrained gensim model
        :param path: Path to the model
        :return: Returns the loaded model
        """
        pass

    def save_model(self, model, path):
        """
        Save the model
        :param model: Model
        :param path: Path
        :return: None
        """
        pass

    def train_model(self, data, windowSize, epochs):
        """
        Helper to train a model using gensim
        :param data: data (list of lists)
        :param windowSize: Window Size of the model
        :param epochs: Number of epochs
        :return: trained Model
        """
        pass

    def load_concepts(self, path):
        """
        Helper function to load processed concepts from a txt file
        :param path: Path to concept file
        :return: List of concepts
        """
        f = open(path, "r")
        concepts = f.readlines()
        concepts = self.__process_concepts(concepts)
        f.close()
        return list(set(concepts))

    def __process_concepts(self, concepts):
        """
        Process concepts depending on the dataset
        # TODO: Make this function specific to a dataset
        :param concepts: List of concepts to be modified
        :return: Modified list of concepts.
        """
        processed_concepts = []
        for concept in concepts:
            concept_break = concept.strip().split()
            concept_w = "w_" + "_".join(concept_break) + "_w"
            concept_v = "v_" + "_".join(concept_break) + "_v"
            concept_t = "t_" + "_".join(concept_break) + "_t"
            processed_concepts.append(concept_w)
            processed_concepts.append(concept_v)
            processed_concepts.append(concept_t)
        return processed_concepts




