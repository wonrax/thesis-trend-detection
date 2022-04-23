import sys

sys.path.append(".")

import json
from models.topic import TopicModel
from sklearn.cluster import KMeans
from sklearn import metrics

articles = []
with open(r"pipeline\tmp\preprocessed_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# PREPROCESSING
articles = list(filter(lambda x: x["title_segmented_tokens"], articles))
articles = list(filter(lambda x: x["content_segmented_tokens"], articles))
tokens_list = [article["excerpt_segmented_tokens"] for article in articles]
# lower all tokens
tokens_list = [[token.lower() for token in doc] for doc in tokens_list]

# TRAIN MODEL
hdpmodel = TopicModel()
hdpmodel.train(tokens_list, initial_k=50, iteration=5000)
vecs = hdpmodel.vectorize(tokens_list)

# CLUSTERING
k_cluster = hdpmodel.model.live_k
# k_cluster = len(articles) / 4 # 4 is number of news sources
cluster_model = KMeans(n_clusters=int(k_cluster))
cluster_model.fit(vecs)
silhouette_avg = metrics.silhouette_score(vecs, cluster_model.labels_)
print("Number of clusters: %d" % k_cluster)
print("Silhouette Coefficient: %0.3f" % silhouette_avg)
print("----------------------")

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
    print(f"\nTopic {topic[0]}")
    for article in topic[1]:
        print("\t", article["source"], "\t", article["title"])
