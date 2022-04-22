import time
import tomotopy as tp
from typing import List


class TopicModel:
    def __init__(self):
        """
        :param k: number of topics
        :param method: method chosen for the topic model
        """
        # self.dictionary: corpora.Dictionary = None
        self.corpus: tp.utils.Corpus = None
        self.model: tp.HDPModel = None

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

        print(
            "Num docs:",
            len(model.docs),
            ", Vocab size:",
            len(model.used_vocabs),
            ", Num words:",
            model.num_words,
        )

        print("Removed top words:", model.removed_top_words)
        batch_size = 100
        for i in range(0, iteration, batch_size):
            model.train(batch_size)
            if i % int(iteration / 10) == 0:
                print(
                    "Iteration: {}\tLog-likelihood: {}\tNum. of topics: {}".format(
                        i, model.ll_per_word, model.live_k
                    )
                )

        model.summary()
        print("Topic model took:", round(time.time() - t1, 1))

    def vectorize(self, tokens_list):
        """
        Get vector representations
        """

        # turn tokenized documents into a id <-> term dictionary
        # if not self.dictionary:
        #     self.dictionary = corpora.Dictionary(tokens_list)

        # convert tokenized documents into a document-term matrix
        # self.corpus = [self.dictionary.doc2bow(text) for text in tokens_list]

        assert self.model

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
                _doc = self.model.make_doc(doc)
                docs_vector.append(self.model.infer(_doc)[0])

        return docs_vector


if __name__ == "__main__":
    import json

    articles = []
    with open(r"pipeline\tmp\preprocessed_articles.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    hdpmodel = TopicModel()

    tokens_list = [article["excerpt_segmented_tokens"] for article in articles]
    # lower all tokens
    tokens_list = [[token.lower() for token in doc] for doc in tokens_list]

    hdpmodel.train(tokens_list, initial_k=100, iteration=5000)
    vecs = hdpmodel.vectorize(tokens_list)

    from sklearn.cluster import KMeans

    k_cluster = hdpmodel.model.live_k
    # k_cluster = len(articles) / 4 # 4 is number of news sources
    cluster_model = KMeans(n_clusters=int(k_cluster))
    cluster_model.fit(vecs)

    for index, article in enumerate(articles):
        article["topic"] = cluster_model.labels_[index]

    topic_articles = {}

    for article in articles:
        if article["topic"] not in topic_articles:
            topic_articles[article["topic"]] = []
        topic_articles[article["topic"]].append(article)

    sorted_topic = sorted(
        topic_articles.items(), key=lambda x: len(x[1]), reverse=False
    )

    for topic in sorted_topic:
        print(f"\nTopic {topic[0]}")
        for article in topic[1]:
            print("\t", article["source"], "\t", article["title"])

    # articles.sort(key=lambda x: x["topic"])
    # current_topic = None
    # for article in articles:
    #     if article["topic"] != current_topic:
    #         current_topic = article["topic"]
    #         print("\n")
    #         print(f"Topic {current_topic}:")
    #     print("\t",article["source"], "-", article["title"])
