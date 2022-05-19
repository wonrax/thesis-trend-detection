from models.topic import TopicModel
from sklearn.cluster import KMeans
from sklearn import metrics
from logger import get_common_logger
from preprocess import PreprocessedArticle
from typing import List

# Set up logger
logger = get_common_logger()


def topic_cluster(
    articles: List[PreprocessedArticle],
) -> tuple[dict[int, List[PreprocessedArticle]], float, float]:
    """Cluster articles into topics using Topic model and KMeans.

    Args:
        articles (List[PreprocessedArticle]): List of articles to cluster.

    Returns:
        tuple(dict[int, List[PreprocessedArticle]], float, float):
            Topic ids and associated articles, coherence score, and silhouette score.
    """

    # FILTERING
    articles = list(filter(lambda x: x.excerpt_segmented_tokens, articles))
    corpus = [article.excerpt_segmented_tokens for article in articles]
    corpus = [[token.lower() for token in doc] for doc in corpus]

    # TRAIN MODEL
    logger.info("Started training topic model...")
    hdpmodel = TopicModel(logger=logger)
    hdpmodel.train(corpus, initial_k=50, iteration=1000)
    coherence_score = hdpmodel.evaluate("c_v")
    logger.info("Vectorizing corpus...")
    vecs = hdpmodel.vectorize(corpus)
    logger.info(f"Coherence score (c_v): {coherence_score}")

    # CLUSTERING
    num_topics = min(hdpmodel.model.live_k, len(corpus) - 1)
    logger.info(f"Clustering {num_topics} clusters...")
    cluster_model = KMeans(n_clusters=num_topics)
    cluster_model.fit(vecs)
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

    return topic_articles, coherence_score, silhouette_avg


# For testing purpose
def main():
    from pipeline.preprocess import main as preprocess_main

    processed_articles, category = preprocess_main()

    topic_articles, coherence_score, silhouette_avg = topic_cluster(processed_articles)

    sorted_topic = sorted(
        topic_articles.items(), key=lambda x: len(x[1]), reverse=False
    )

    for topic in sorted_topic:
        log_string = f"Topic {topic[0]}: {len(topic[1])} articles\n"
        for article in topic[1]:
            log_string += f"\t{article.source}\t{article.title}\n"
        logger.debug(log_string)

    return topic_articles, category, coherence_score, silhouette_avg


if __name__ == "__main__":
    main()
