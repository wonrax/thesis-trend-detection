if __name__ == "__main__":
    import sys

    sys.path.append(".")

from pipeline.logger import get_common_logger
from pipeline.preprocess import PreprocessedArticle
from data.model.category import Category
from data.model.topic import (
    CategoryAnalysis,
    TopicAnalysis,
    ArticleAnalysis,
    CommentAnalysis,
    Metrics,
)
from data.model.article import Article, Comment
from typing import List
import datetime
from yake import KeywordExtractor

# Set up logger
logger = get_common_logger()


def analyse_comment(comment: Comment) -> CommentAnalysis:
    """Analysis a comment.

    Args:
        comment (Comment): Comment to analyse.

    Returns:
        CommentAnalysis: Analysed comment.
    """
    # TODO
    # Preprocess the comment
    # Do sentiment analysis
    # Repeat for the replies
    # Return the result

    replies = [analyse_comment(reply) for reply in comment.replies]

    return CommentAnalysis(
        original_comment=comment,
        sentiment=None,
        replies=replies,
    )


def analyse_article(article: PreprocessedArticle) -> ArticleAnalysis:
    """Analysis an article.

    Args:
        article (PreprocessedArticle): Preprocess article.

    Returns:
        ArticleAnalysis: Analysed article.
    """

    articleObject: Article = Article.objects.get(id=article.id_mongo)

    comments = []
    comments_positive_rate = None
    comments_neutral_rate = None
    comments_negative_rate = None
    keywords = []

    if articleObject.comments:
        comments = [analyse_comment(comment) for comment in articleObject.comments]
        # TODO: calculate sentiment rate for this post

    if article.content_segmented_sentences:
        for n in range(1, 4):
            kw_extractor = KeywordExtractor(lan="vi", n=n, windowsSize=3, top=3)
            _keywords = kw_extractor.extract_keywords(
                article.content_segmented_sentences
            )
            _keywords.sort(key=lambda s: s[1], reverse=False)
            keywords += [k for k, _ in _keywords]

    return ArticleAnalysis(
        original_article=articleObject,
        comments_negative_rate=comments_negative_rate,
        comments_neutral_rate=comments_neutral_rate,
        comments_positive_rate=comments_positive_rate,
        keywords=keywords,
        comments=comments,
    )


def analyse_topic(articles: List[PreprocessedArticle]) -> TopicAnalysis:
    """Sort articles by a heuristic algorithm (i.e. relevant score).

    Args:
        articles (List[PreprocessedArticle]): List of articles to sort.

    Returns:
        List[ArticleAnalysis]: Sorted list of articles.
    """

    now = datetime.datetime.utcnow()

    analysed_articles = [analyse_article(article) for article in articles]
    article_scores: List[tuple[ArticleAnalysis, float]] = []

    # Choose the most popular keyword for each n_gram from the articles' keywords
    topic_keywords = []
    n_gram_keywords: dict[int, dict[str, int]] = {}  # {n_gram: {keyword: count}}
    for article in analysed_articles:
        for keyword in article.keywords:
            n_gram = len(keyword.split())
            if (n_gram) not in n_gram_keywords:
                n_gram_keywords[n_gram] = {}
            if keyword not in n_gram_keywords[n_gram]:
                n_gram_keywords[n_gram][keyword] = 0
            n_gram_keywords[n_gram][keyword] += 1
    for n_gram in n_gram_keywords:
        sorted_keywords = sorted(
            n_gram_keywords[n_gram].items(), key=lambda x: x[1], reverse=True
        )
        topic_keywords.append(
            sorted_keywords[0][0]
        )  # Get the most popular keyword for each n_gram

    # List of the most popular keywords in 2_grams
    # This will be used for calculating the relevance score for each article
    if 2 in n_gram_keywords:
        two_grams_keywords = sorted(
            n_gram_keywords[2].items(), key=lambda x: x[1], reverse=True
        )
        two_grams_keywords = [k for k, _ in two_grams_keywords][:6]
    else:
        two_grams_keywords = topic_keywords

    # TODO compute average sentiment rate for this topic
    average_negative_rate = None
    average_neutral_rate = None
    average_positive_rate = None

    # TODO add distance to centroid as a factor
    # TODO DO NOT sort if only one article
    for article in analysed_articles:
        score: float = 0
        articleObject: Article = article.original_article
        likes = articleObject.likes
        date = articleObject.date
        num_comments = len(articleObject.comments) if articleObject.comments else 0
        if likes:
            score += likes
        if num_comments:
            score += num_comments * 2
        if date:
            relative_minutes: float = (now - date).seconds / 60 + 1
            score += 10000 / relative_minutes
        if article.keywords:
            for keyword in article.keywords:
                if keyword in two_grams_keywords:
                    score += 3000
        article_scores.append((article, score))

    # sort by score
    article_scores.sort(key=lambda x: x[1], reverse=True)

    return TopicAnalysis(
        articles=[article for article, _ in article_scores],
        keywords=topic_keywords,
        average_negative_rate=average_negative_rate,
        average_neutral_rate=average_neutral_rate,
        average_positive_rate=average_positive_rate,
    )


def analyse_category(
    category: Category, topic_articles: dict[int, List[PreprocessedArticle]]
) -> CategoryAnalysis:

    logger.info(f"Analyzing {len(topic_articles)} topics in {category}")
    analysed_topics = []

    for key in topic_articles:
        articles_of_a_topic = topic_articles[key]
        analysed_topics.append(analyse_topic(articles_of_a_topic))
        if len(analysed_topics) % int(len(topic_articles) / 10) == 0:
            logger.info(f"{len(analysed_topics)}/{len(topic_articles)} topics analysed")

    # TODO find another, smarter way to sort the topics by relevance
    # TODO DO NOT sort if only one topic
    now = datetime.datetime.utcnow()
    topic_scores: List[tuple[TopicAnalysis, int]] = []
    for topic in analysed_topics:
        score: float = 0

        # get datetime median of topic.articles
        datetimes = [article.original_article.date for article in topic.articles]
        datetimes.sort()
        delta = datetimes[-1] - datetimes[0]
        median_datetime = datetimes[0] + delta / 2

        relative_minutes: float = (now - median_datetime).seconds / 60 + 1
        score += 1000 / relative_minutes
        score += len(topic.articles) * 100

        topic_scores.append((topic, score))

    topic_scores.sort(key=lambda x: x[1], reverse=True)

    return CategoryAnalysis(
        topics=[topic for topic, _ in topic_scores],
        category=str(category),
    )


def main():
    from pipeline.topic_cluster import main as topic_cluster_main

    topic_articles, category, coherence_score, silhouette_avg = topic_cluster_main()
    category_analysis = analyse_category(category, topic_articles)

    metrics = Metrics(
        silhouette_coefficient=silhouette_avg,
        topic_coherence=coherence_score,
    )
    category_analysis.metrics = metrics
    category_analysis.save()


if __name__ == "__main__":
    main()
