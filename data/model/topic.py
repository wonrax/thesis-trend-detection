from mongoengine import *
from .article import Article
from datetime import datetime


class CommentAnalysis(EmbeddedDocument):
    """Document that contains analysis on a comment."""

    comment_id = ObjectIdField(required=True, null=False)
    sentiment = StringField(
        null=True, choices=("NEGATIVE", "POSITIVE", "NEUTRAL", "UNSURE")
    )
    replies = ListField(ReferenceField("self"), null=True)


class ArticleAnalysis(EmbeddedDocument):
    """Document that contains analysis on an article."""

    original_article = ReferenceField(Article, required=True, null=False)
    comments_negative_rate = FloatField(null=True)
    comments_positive_rate = FloatField(null=True)
    comments_neutral_rate = FloatField(null=True)
    keywords = ListField(StringField(), null=True)
    comments = ListField(EmbeddedDocumentField(CommentAnalysis), null=True)


class TopicAnalysis(EmbeddedDocument):
    """Document that contains analysis on a topic."""

    articles = ListField(EmbeddedDocumentField(ArticleAnalysis), required=True)
    keywords = ListField(StringField(), null=True)
    average_negative_rate = FloatField(null=True)
    average_positive_rate = FloatField(null=True)
    average_neutral_rate = FloatField(null=True)


class Metrics(EmbeddedDocument):
    """Document that contains metrics."""

    silhouette_coefficient = FloatField(null=True)
    topic_coherence = FloatField(null=True)


class CategoryAnalysis(Document):
    """Document that contains analysed topics of a category (e.g. SUC_KHOE, PHAP_LUAT)."""

    topics = ListField(EmbeddedDocumentField(TopicAnalysis), required=True)
    category = StringField(required=True, null=False)
    creation_date = DateTimeField(required=True, default=datetime.utcnow)
    metrics = EmbeddedDocumentField(Metrics, null=True)
