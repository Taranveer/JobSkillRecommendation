import multiprocessing
from gensim.models.doc2vec import LabeledSentence, TaggedDocument
from gensim.models import Doc2Vec
from phraseMapper import *
from sklearn.preprocessing import normalize


"""
This is wrapper class over training Doc2Vec model.
"""

class DocumentEmbedder(object):
    def __init__ (self, dirname):
        """
        This is the class constructor which only takes the directory name
        of the books contents txt files' folder as the input.
        In our case dirname = "../books-content"
        :param dirname:
        """
        self.dirname = dirname
        self.conceptMapping = getConceptPhrases()
        self.getPageTaggedDocuments()
        return

    def getTaggedDocuments(self):
        """
        This function creates a list of 'TaggedDocument' objects over the different paragraphs
        in the books pages, treating each of the paragraphs as docs with docID represented as
        '<book_name>_<page_id/page_no>_<paragraph_id>'
        :return:
        """
        taggedDocs = []
        documentDict = {}
        for docFile in os.listdir(self.dirname):
            print docFile
            fd = open("%s%s"%(self.dirname,docFile), 'r')
            fileData = fd.read()
            pages = fileData.split('\x0c')
            print len(pages)
            for page_id in xrange(len(pages)):
                paragraphs = pages[page_id].split('\n\n')
                for paragraph_id in xrange(len(paragraphs)):
                    paragraph = paragraphs[paragraph_id]
                    taggedDocs.append(TaggedDocument(words = paragraph.split(), tags = ["%s_%s_%s"%(docFile, page_id +1, paragraph_id+1)]))
                    documentDict["%s_%s_%s"%(docFile, page_id +1, paragraph_id+1)] = paragraph
        self.taggedDocs = taggedDocs
        self.documents = documentDict
        return

    def getPageTaggedDocuments(self):
        """
        This function creates a list of 'TaggedDocument' objects over the different paragraphs
        in the books pages, treating each of the paragraphs as docs with docID represented as
        '<book_name>_<page_id/page_no>_<paragraph_id>'
        :return:
        """
        taggedDocs = []
        documentDict = {}
        for docFile in os.listdir(self.dirname):
            print docFile
            fd = open("%s%s"%(self.dirname,docFile), 'r')
            fileData = fd.read()
            fileData = fileData.replace("\n\n"," ")
            pages = fileData.split('\x0c')
            print len(pages)
            for page_id in xrange(len(pages)):
                taggedDocs.append(TaggedDocument(words = pages[page_id].split(), tags = ["%s_%s"%(docFile, page_id +1)]))
                documentDict["%s_%s"%(docFile, page_id +1)] = pages[page_id]
        self.taggedDocs = taggedDocs
        self.documents = documentDict
        return

    def createDoc2VecModel(self, windowSize = 10, epochs = 100):
        """
        This function takes the number of epochs on which we want to train the model
        :param epochs:
        :param windowSize:
        :return: trained Doc2Vec model
        """
        print "Start Model Training"
        self.model = Doc2Vec(self.taggedDocs, size=200, window=windowSize, min_count=5, workers=multiprocessing.cpu_count(), iter = epochs)
        print "Model Training Complete"
        self.concepts = list(set(self.conceptMapping.values()) & set(self.model.wv.vocab))
        self.conceptsVectors = normalize(self.model[self.concepts])
        return self.model


    def loadDoc2VecModel(self, filename):
        """
        Loads a Previously saved Model
        :param filename:
        :return:
        """
        self.model = Doc2Vec.load(filename)
        self.concepts = list(set(self.conceptMapping.values()) & set(self.model.wv.vocab))
        self.conceptsVectors = normalize(self.model[self.concepts])
        print "Model Loaded"
        return self.model


    def getClosestDocuments(self, word, n):
        """
        This function takes the concept name anf returns the closest documents
        pertaining to those concepts.
        :param word:
        :param n:
        :return:
        """
        if word not in self.model.wv.vocab:
            print "Word not Present"
        else:
            wordVector = self.model.wv[word]
            docsSimilarities = self.model.docvecs.most_similar([wordVector])
            self.printSimilarDocContent(docsSimilarities,n)


    def printSimilarDocContent(self,docsSimilarities,n=5):
        """
        Give the similarty score matrix of the documents, it prints the closest ones from the list
        :param docsSimilarities:
        :param n:
        :return:
        """
        n = min(10, n)
        for i in xrange(n):
            docID, similarityScore = docsSimilarities[i]
            print
            print "Document NO: %s , ID:%s " % (i + 1, docID)
            print self.documents[docID]
            print
        return


    def getClosestWords(self,word):
        """
        This functions prints the closest concepts int he embeddign space to
        the given one.
        :param word:
        :return:
        """
        if word not in self.model.wv.vocab:
            print "Word not Present"
        else:
            similarConcepts = self.model.wv.most_similar(word)
            for concept, similarityScore in similarConcepts:
                print "%s : %s"%(concept,similarityScore)


    def getSimilarContent(self,content):
        """
        This function shows similar content for any new piece of text/forum we want to map to.
        :param content:
        :return:
        """
        content = content.lower()
        content = cleanContentPage(content)
        for phrase in self.conceptMapping:
            content = content.replace(phrase, self.conceptMapping[phrase])
        print content
        print "Creating Vector Representation"
        contentVector = self.model.infer_vector(content.split(), steps=100000)
        print "Found!. Finding Similar Docs"
        docsSimilarities = self.model.docvecs.most_similar([contentVector])
        self.printSimilarDocContent(docsSimilarities)
        return

    def getConceptRanking(self,content,steps = 100000, n = 10):
        """
        This function given any content tries to get top n concept
        rankings for that content.
        :param content:
        :param n:
        :return:
        """
        content = content.lower()
        content = cleanContentPage(content)
        for phrase in self.conceptMapping:
            content = content.replace(phrase, self.conceptMapping[phrase])
        print "Creating Vector Representation"
        contentVector = self.model.infer_vector(content.split(), steps=steps)
        print "Found!. Finding Similar Docs"
        conceptRankings,conceptDistances = self.getRanking(contentVector, n)
        for index in conceptRankings:
            print "%s : %s"%(self.concepts[index],conceptDistances[index])
        return


    def getConceptRankPosition(self,content,concept, steps = 100000, n = 1000):
        """
        This function give the positin of the rank in the list
        :param content:
        :param concept:
        :param steps:
        :param n:
        :return:
        """
        content = content.lower()
        content = cleanContentPage(content)
        for phrase in self.conceptMapping:
            content = content.replace(phrase, self.conceptMapping[phrase])
        print "Creating Vector Representation"
        contentVector = self.model.infer_vector(content.split(), steps=steps)
        print "Found!. Finding Similar Docs"
        conceptRankings,conceptDistances = self.getRanking(contentVector, n)
        for i in conceptRankings[:10]:
            print "%s : %s" % (self.concepts[i], conceptDistances[i])
        rank = 0
        for index in conceptRankings:
            rank+=1
            if(self.concepts[index] == concept):
                print "%s:%s, Rank: %d"%(concept,conceptDistances[index],rank)
                return
        print "not found"


    def getRanking(self,conceptVector,n):
        """
        Calculates internal Ranking
        :param conceptVector:
        :param n:
        :return:
        """
        #conceptVector = conceptVector.reshape(conceptVector.shape[0],1)
        conceptVector = normalize(conceptVector)
        conceptDistances = np.dot(self.conceptsVectors, conceptVector.T)
        conceptDistances = conceptDistances.reshape(conceptDistances.shape[0])
        rankedIndices = conceptDistances.argsort()[-n:][::-1]
        return rankedIndices,conceptDistances






