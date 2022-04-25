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
)
from data.model.article import Article, Comment
from typing import List
import datetime

# Set up logger
logger = get_common_logger(__name__)


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
        comment_id=comment.id,
        id_source=comment.id_source,
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
        # TODO extract keywords
        pass

    return ArticleAnalysis(
        original_article=articleObject,
        id_source=articleObject.id_source,
        source=articleObject.source,
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
    article_scores: List[tuple[ArticleAnalysis, int]] = []

    # TODO choose the most popular keywords from the articles' keywords
    keywords = None

    # TODO compute average sentiment rate for this topic
    average_negative_rate = None
    average_neutral_rate = None
    average_positive_rate = None

    # TODO add distance to centroid as a factor
    # TODO DO NOT sort if only one article
    for article in analysed_articles:
        score = 0
        articleObject: Article = article.original_article
        likes = articleObject.likes
        date = articleObject.date
        num_comments = len(articleObject.comments) if articleObject.comments else 0
        if likes:
            score += likes
        if num_comments:
            score += num_comments * 2
        if date:
            relative_minutes: int = int((now - date).seconds / 60) + 1
            score += int(10000 / relative_minutes)
        article_scores.append((article, score))

    # sort by score
    article_scores.sort(key=lambda x: x[1], reverse=True)

    return TopicAnalysis(
        articles=[article for article, _ in article_scores],
        keywords=keywords,
        average_negative_rate=average_negative_rate,
        average_neutral_rate=average_neutral_rate,
        average_positive_rate=average_positive_rate,
    )


def analyse_category(
    category: Category, topic_articles: dict[int, List[PreprocessedArticle]]
) -> CategoryAnalysis:
    analysed_topics = []
    for key in topic_articles:
        articles_of_a_topic = topic_articles[key]
        analysed_topics.append(analyse_topic(articles_of_a_topic))

    # TODO find another, smarter way to sort the topics by relevance
    # TODO DO NOT sort if only one topic
    topic_scores: List[tuple[TopicAnalysis, int]] = []
    for topic in analysed_topics:
        topic_scores.append((topic, len(topic.articles)))

    topic_scores.sort(key=lambda x: x[1], reverse=True)

    return CategoryAnalysis(
        topics=[topic for topic, _ in topic_scores],
        category=str(category),
    )


def main():
    from pipeline.topic_cluster import main as topic_cluster_main

    topic_articles, category = topic_cluster_main()
    category_analysis = analyse_category(category, topic_articles)

    category_analysis.save()


if __name__ == "__main__":
    main()
