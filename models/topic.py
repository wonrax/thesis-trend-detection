import time
from typing import List
from gensim.models.hdpmodel import HdpModel
from gensim.corpora import Dictionary


class TopicModel:
    def __init__(self):
        """
        :param k: number of topics
        :param method: method chosen for the topic model
        """
        self.dictionary: Dictionary = None
        self.model: HdpModel = None

    def train(self, tokens_list: List[List[str]], initial_k=20, iteration=20000):
        """Train the topic model

        Args:
            tokens_list (List[List[str]]): list of tokenized documents
            initial_k (int, optional): Initial k to train the topic model. Defaults to 20.
        """

        t1 = time.time()

        dictionary = Dictionary(tokens_list)
        self.dictionary = dictionary

        bow_corpus = [dictionary.doc2bow(doc) for doc in tokens_list]

        model = HdpModel(bow_corpus, dictionary, K=100, T=200, chunksize=10000,)
        self.model = model

        topic_info = model.print_topics(num_topics=10, num_words=4)
        for topic in topic_info:
            print(topic)

        print("Topic model took:", round(time.time() - t1, 1))

    def vectorize(self, tokens_list: List[List[str]]):
        """
        Get vector representations for documents

        Args:
            tokens_list (List[List[str]]): list of tokenized documents
        """

        # turn tokenized documents into a id <-> term dictionary
        # if not self.dictionary:
        #     self.dictionary = corpora.Dictionary(tokens_list)

        # convert tokenized documents into a document-term matrix
        # self.corpus = [self.dictionary.doc2bow(text) for text in tokens_list]

        assert self.model
        assert self.dictionary

        if False:  # Testing predefined k topics
            lda = model.convert_to_lda(0.02)[0]
            print("Converted to LDA")

            print(f"Num of topics: {len(lda.get_count_by_topics())}")
            docs_vector = []
            for doc in corpus:
                docs_vector.append(lda.infer(lda.make_doc(doc))[0])

            self.vec["HDP"] = docs_vector
            self.k = len(lda.get_count_by_topics())
        else:
            docs_vector = []
            for doc in tokens_list:
                _doc = self.dictionary.doc2bow(doc)
                docs_vector.append(self.model[_doc])

        return docs_vector
