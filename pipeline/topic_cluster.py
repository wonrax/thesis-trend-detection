import sys

sys.path.append(".")

import json
from models.topic import TopicModel
from sklearn.cluster import KMeans
from sklearn import metrics
from pipeline.logger import get_logger
import logging

# Set up logger
log_filename = f"pipeline/logs/{__name__}.log"
LOG_LEVEL = logging.DEBUG
logger = get_logger(__name__, LOG_LEVEL, log_filename)

articles = []
with open(r"pipeline\tmp\preprocessed_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# PREPROCESSING
articles = list(filter(lambda x: x["title_segmented_tokens"], articles))
articles = list(filter(lambda x: x["content_segmented_tokens"], articles))
tokens_list = [article["content_segmented_tokens"] for article in articles]
# lower all tokens
tokens_list = [[token.lower() for token in doc] for doc in tokens_list]

# TRAIN MODEL
hdpmodel = TopicModel()
hdpmodel.train(tokens_list, initial_k=50, iteration=5000)
vecs = hdpmodel.vectorize(tokens_list)
num_topic = len(hdpmodel.model.get_topics())

_vecs = []
for vec in vecs:
    _vec = [0] * num_topic
    for topic_probability in vec:
        topic_id = topic_probability[0]
        probability = topic_probability[1]
        _vec[topic_id] = probability
    _vecs.append(_vec)

vecs = _vecs

# CLUSTERING
k_cluster = num_topic
# k_cluster = len(articles) / 4 # 4 is number of news sources
cluster_model = KMeans(n_clusters=int(k_cluster))
cluster_model.fit(vecs)
silhouette_avg = metrics.silhouette_score(vecs, cluster_model.labels_)
logger.info(f"Number of clusters: {k_cluster}")
logger.info(f"Silhouette Coefficient: {silhouette_avg}")

# PRINT OUT RESULT
for index, article in enumerate(articles):
    article["topic"] = cluster_model.labels_[index]

topic_articles = {}

for article in articles:
    if article["topic"] not in topic_articles:
        topic_articles[article["topic"]] = []
    topic_articles[article["topic"]].append(article)

sorted_topic = sorted(topic_articles.items(), key=lambda x: len(x[1]), reverse=False)

for topic in sorted_topic:
    log_string = f"Topic {topic[0]}: {len(topic[1])} articles\n"
    for article in topic[1]:
        log_string += f'\t{article["source"]}\t{article["title"]}\n'
    logger.info(log_string)
