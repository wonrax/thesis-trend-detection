import time
import tomotopy as tp
from typing import List
import logging


class TopicModel:
    def __init__(self, logger: logging.Logger = None):
        """
        :param k: number of topics
        :param method: method chosen for the topic model
        """
        # self.dictionary: corpora.Dictionary = None
        self.corpus: tp.utils.Corpus = None
        self.model: tp.HDPModel = None

        if logger is None:
            self.logger = logging.getLogger(__name__)
            # Do not log anything
            self.logger.addHandler(logging.NullHandler())
        else:
            self.logger = logger

    def train(self, tokens_list: List[List[str]], initial_k=20, iteration=20000):
        """Train the topic model

        Args:
            tokens_list (List[List[str]]): list of tokenized documents
            initial_k (int, optional): Initial k to train the topic model. Defaults to 20.
        """
        self.corpus = tp.utils.Corpus()

        for doc in tokens_list:
            self.corpus.add_doc(doc)

        t1 = time.time()

        model = tp.HDPModel(
            tw=tp.TermWeight.ONE,
            min_cf=0,
            rm_top=0,
            initial_k=initial_k,
            corpus=self.corpus,
        )

        self.model = model

        model.burn_in = 100
        model.train(0)

        self.logger.info(
            f"Num docs: {len(model.docs)}, Vocab size: {len(model.used_vocabs)}, Num words: {model.num_words}"
        )

        self.logger.info(f"Removed top words: {model.removed_top_words}")
        batch_size = 100
        for i in range(0, iteration, batch_size):
            model.train(batch_size)
            if i % int(iteration / 10) == 0:
                self.logger.info(
                    "Iteration: {}\tLog-likelihood: {}\tNum. of topics: {}".format(
                        i, model.ll_per_word, model.live_k
                    )
                )

        model.summary()
        self.logger.info(f"HDP model took: {round(time.time() - t1, 1)} seconds")

    def vectorize(self, tokens_list):
        """
        Get vector representations
        """

        assert self.model

        docs_vector = []

        for doc in tokens_list:
            _doc = self.model.make_doc(doc)
            docs_vector.append(self.model.infer(_doc)[0])

        return docs_vector
