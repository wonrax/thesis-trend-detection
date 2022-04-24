if __name__ == "__main__":
    import sys

    sys.path.append(".")

from models.topic import TopicModel
from sklearn.cluster import KMeans
from sklearn import metrics
from pipeline.logger import get_common_logger
from pipeline.preprocess import PreprocessedArticle
from typing import List

# Set up logger
logger = get_common_logger(__name__)


def topic_analysis(articles: List[PreprocessedArticle]):
    # FILTERING
    articles = list(filter(lambda x: x.excerpt_segmented_tokens, articles))
    corpus = [article.excerpt_segmented_tokens for article in articles]
    corpus = [[token.lower() for token in doc] for doc in corpus]

    # TRAIN MODEL
    logger.info("Started training topic model.")
    hdpmodel = TopicModel(logger=logger)
    hdpmodel.train(corpus, initial_k=len(corpus), iteration=2000)
    vecs = hdpmodel.vectorize(corpus)

    # CLUSTERING
    num_topics = min(hdpmodel.model.live_k, len(corpus))
    logger.info("Started clustering articles.")
    logger.info(f"Number of clusters: {num_topics}")
    cluster_model = KMeans(n_clusters=num_topics)
    cluster_model.fit(vecs)
    logger.info("Finished clustering articles.")
    silhouette_avg = metrics.silhouette_score(vecs, cluster_model.labels_)
    logger.info(f"Silhouette Coefficient: {silhouette_avg}")

    # RESULT
    labels = cluster_model.labels_
    topic_articles: dict[int, List[PreprocessedArticle]] = {}

    for index, article in enumerate(articles):
        label = labels[index]
        if label not in topic_articles:
            topic_articles[label] = []
        topic_articles[label].append(article)

    return topic_articles


if __name__ == "__main__":
    from pipeline.constants import DATABASE_URL
    from mongoengine import connect
    from zoneinfo import ZoneInfo
    from data.model.article import Article
    from pipeline.preprocess import preprocess_articles
    import datetime

    assert DATABASE_URL
    connect(host=DATABASE_URL)

    end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    start_date = end_date - datetime.timedelta(days=1)

    articles = Article.objects.filter(date__gte=start_date, date__lte=end_date)
    processed_articles = preprocess_articles(articles)

    topic_articles = topic_analysis(processed_articles)

    sorted_topic = sorted(
        topic_articles.items(), key=lambda x: len(x[1]), reverse=False
    )

    for topic in sorted_topic:
        log_string = f"Topic {topic[0]}: {len(topic[1])} articles\n"
        for article in topic[1]:
            log_string += f"\t{article.source}\t{article.title}\n"
        logger.debug(log_string)
