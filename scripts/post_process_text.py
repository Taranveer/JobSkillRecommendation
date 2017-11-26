
# coding: utf-8

# In[26]:

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


def aggregation(corpus, agg):
    """
    No of sentences to combine so that we can capture better context
    <d_d_e_l> : document del
    <s_d_e_l> : sentence del
    split on above and then aggregate
    """
    corpus_doc = corpus[0].split(" <d_d_e_l> ")
    corpus_doc_sent = map(lambda x: x.split(" <s_d_e_l> "),  corpus_doc)
    corpus_agg = []
    
    if agg > 0:
        for doc in corpus_doc_sent:
            sent_list = []
            for i in range(0,len(doc), agg):
                sent = ". ".join(doc[i:(i+agg)])
                sent_list.append(sent)
            corpus_agg.append(sent_list)
    else:
        corpus_agg = corpus_doc_sent
        
    return corpus_agg



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="post aggregation of sentences")
    
    parser.add_argument('--corpus', dest='corpus_file', type=str,
                    help='book/video/wiki corpus', default="clean_pages")
    
    parser.add_argument('--output', dest='output', type=str,
                    help='output after cleaning', default="corpus_parsed")
    
    parser.add_argument('--agg', dest='agg', type = int, 
                       help = 'level of aggregation', default = 0)

    args = parser.parse_args()

    corpus_file = args.corpus_file
    corpus = load(corpus_file)
    
    corpus_agg = aggregation(corpus, args.agg)
    
    dump(corpus_agg, args.output)


# In[ ]:



