from logger import get_common_logger
from preprocess import PreprocessedArticle
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
import math
from data.preprocess import Preprocess
from models.sentiment import Sentiment, get_sentiment
from bson.objectid import ObjectId

# Set up logger
logger = get_common_logger()


def find_comment_by_id(id: ObjectId, comments: List[Comment]) -> Comment:
    for comment in comments:
        if comment.oid == id:
            return comment
        if comment.replies:
            found = find_comment_by_id(id, comment.replies)
            if found:
                return found


def analyse_comment(comment: Comment) -> CommentAnalysis:
    """Analysis a comment.

    Args:
        comment (Comment): Comment to analyse.

    Returns:
        CommentAnalysis: Analysed comment.
    """

    comment_content_segmented = Preprocess.segmentize(
        text=comment.content, do_teen_code=True, do_sentences=True
    )["sentences"]

    sentiment = get_sentiment(comment_content_segmented)

    replies = None
    # TODO currently only support one level of replies
    # if comment.replies:
    #     replies = [analyse_comment(reply) for reply in comment.replies]

    return CommentAnalysis(
        comment_id=comment.oid,
        sentiment=sentiment.name,
        replies=replies,
    )


def analyse_article(article: PreprocessedArticle) -> ArticleAnalysis:
    """Analysis an article.

    Args:
        article (PreprocessedArticle): Preprocess article.

    Returns:
        ArticleAnalysis: Analysed article.
    """

    original_article: Article = Article.objects.get(id=article.id_mongo)

    comments = []
    comments_positive_rate = None
    comments_neutral_rate = None
    comments_negative_rate = None
    keywords = []

    if original_article.comments and len(original_article.comments) > 5:
        # The number of comments also needs to be above 5 to be considered "statistically significant"
        comments = [analyse_comment(comment) for comment in original_article.comments]
        ratings: List[tuple[str, int]] = []  # [(sentiment, count)]
        for comment in comments:
            original_comment: Comment = find_comment_by_id(
                comment.comment_id, original_article.comments
            )
            if original_comment:
                weight = original_comment.likes if original_comment.likes else 1
            else:
                weight = 1
            ratings.append((comment.sentiment, weight))

        # Compute the sentiment rate for this article
        total = sum(weight for _, weight in ratings)
        comments_negative_rate = (
            sum(
                weight
                for sentiment, weight in ratings
                if sentiment == Sentiment.NEGATIVE.name
            )
            / total
        )
        comments_positive_rate = (
            sum(
                weight
                for sentiment, weight in ratings
                if sentiment == Sentiment.POSITIVE.name
            )
            / total
        )
        comments_neutral_rate = (
            sum(
                weight
                for sentiment, weight in ratings
                if sentiment == Sentiment.NEUTRAL.name
            )
            / total
        )

    if article.excerpt_segmented_sentences:
        for n in range(1, 4):
            kw_extractor = KeywordExtractor(lan="vi", n=n, windowsSize=1, top=3)
            _keywords = kw_extractor.extract_keywords(
                article.excerpt_segmented_sentences
            )
            _keywords.sort(key=lambda s: s[1], reverse=False)
            keywords += [k for k, _ in _keywords]

    return ArticleAnalysis(
        original_article=original_article,
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
    # This is the representation of a topic on frontend
    topic_keywords = []

    # List of the most popular keywords in all grams
    # This will be used for calculating the relevance score for each article
    relevance_keywords = []

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

        if len(sorted_keywords) >= 3:
            relevance_keywords += [k for k, _ in sorted_keywords[:3]]
        else:
            relevance_keywords += [k for k, _ in sorted_keywords]

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
            score += likes * 20
        if num_comments:
            score += num_comments * 30
        if date:
            relative_hours: float = ((now - date).total_seconds() / 60 + 1) / 60
            score += min(math.sinh(1 / relative_hours) * 500, 200) * 2
        if article.keywords:
            for keyword in article.keywords:
                if keyword in relevance_keywords:
                    score += 1000
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
    
    total_num_articles = 0
    for topic in topic_articles:
        total_num_articles += len(topic_articles[topic])

    TOPIC_ARTICLES_THRESHOLD = (
        round(math.log(x=total_num_articles, base=3))
        # the minimum number of articles for a topic to be considered qualified
    )

    filtered_topics = {
        topic_id: topic_articles[topic_id]
        for topic_id in topic_articles.keys()
        if len(topic_articles[topic_id]) >= TOPIC_ARTICLES_THRESHOLD
    }

    if len(filtered_topics) == 0:
        logger.warning(f"No qualified topics for category {category.name}")
        return None

    logger.info(f"Analyzing {len(filtered_topics)} topics in {category.name}")
    analysed_topics = []

    for key in filtered_topics:
        articles_of_a_topic = filtered_topics[key]
        analysed_topics.append(analyse_topic(articles_of_a_topic))
        if (
            int(len(filtered_topics) / 10) == 0
            or len(analysed_topics) % int(len(filtered_topics) / 10) == 0
        ):
            logger.info(
                f"{len(analysed_topics)}/{len(filtered_topics)} topics analysed"
            )

    # TODO find another, smarter way to sort the topics by relevance
    # TODO DO NOT sort if only one topic
    now = datetime.datetime.utcnow()
    topic_scores: List[tuple[TopicAnalysis, int]] = []
    for topic in analysed_topics:
        score: float = 0

        score += len(topic.articles) * 5

        # Calculate the average time of the articles
        datetimes = [article.original_article.date for article in topic.articles]
        avg_time = datetime.datetime.fromtimestamp(
            sum(map(datetime.datetime.timestamp, datetimes)) / len(datetimes)
        )

        relative_hours: float = ((now - avg_time).total_seconds() / 60 + 1) / 60
        time_score = math.sinh(1 / relative_hours) * 500
        time_score = min(time_score, 200)

        score += math.sqrt(len(topic.articles)) * time_score

        topic_scores.append((topic, score))

    topic_scores.sort(key=lambda x: x[1], reverse=True)

    return CategoryAnalysis(
        topics=[topic for topic, _ in topic_scores],
        category=category.name,
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
