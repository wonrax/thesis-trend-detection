from common.constants import DATABASE_URL
from mongoengine import connect

assert DATABASE_URL
connect(host=DATABASE_URL)

from flask import Flask, request
from flask_restful import Resource, Api
from data.model.category import Category
from data.model.topic import CategoryAnalysis
import dataclasses
from dataclasses import dataclass
from typing import List
from flask_cors import CORS
from datetime import timezone
import datetime


DB_CATEGORY_TO_URL = {}  # e.g. {"moi_nhat": "moi-nhat"}
for category in Category:
    key = category.name
    DB_CATEGORY_TO_URL[key] = category.name.lower().replace("_", "-")

URL_TO_DB_CATEGORY = {v: k for k, v in DB_CATEGORY_TO_URL.items()}

CATEGORY_TO_HUMAN_READABLE = {
    "suc-khoe": "Sức khỏe",
    "moi-nhat": "Mới nhất",
    "the-gioi": "Thế giới",
    "thoi-su": "Thời sự",
    "van-hoa": "Văn hóa",
    "cong-nghe": "Công nghệ",
    "the-thao": "Thể thao",
    "giao-duc": "Giáo dục",
    "giai-tri": "Giải trí",
    "kinh-doanh": "Kinh doanh",
    "phap-luat": "Pháp luật",
}

# Used to display on the frontend
CATEGORY_ORDER = [
    "moi-nhat",
    "the-gioi",
    "thoi-su",
    "van-hoa",
    "cong-nghe",
    "the-thao",
    "giao-duc",
    "giai-tri",
    "kinh-doanh",
    "phap-luat",
    "suc-khoe",
]

app = Flask(__name__)
api = Api(app)
cors = CORS(app)


@dataclass()
class RestfulArticle:
    id: str
    thumbnailUrl: str
    title: str
    articleUrl: str
    description: str
    publishDate: str
    sourceName: str
    sourceLogoUrl: str
    positiveRate: float
    negativeRate: float
    neutralRate: float


@dataclass()
class RestfulTopic:
    articles: List[RestfulArticle]
    keywords: List[str]
    averagePositiveRate: float
    averageNegativeRate: float
    averageNeutralRate: float
    totalNumberOfArticles: int
    hasMoreArticles: bool


@dataclass()
class RestfulTrend:
    id: str
    topics: List[RestfulTopic]
    creationDate: str
    categoryName: str
    availableCategories: dict[str, str]  # e.g. {suc-khoe: "Sức khỏe"}
    hasMoreTopics: bool


def capitalize_first_letter(string) -> str:
    return string[0].upper() + string[1:]


def serialize_trend_analysis(
    category_analysis: CategoryAnalysis, page: int, page_size: int
) -> RestfulTrend:
    topics: List[RestfulTopic] = []
    filtered_topics = category_analysis.topics[
        page * page_size : (page + 1) * page_size
    ]
    for topic in filtered_topics:
        articles = []
        filtered_articles = topic.articles[:3]
        for article in filtered_articles:
            original_article = article.original_article
            articles.append(
                RestfulArticle(
                    id=str(original_article.id),
                    thumbnailUrl=original_article.img_url,
                    articleUrl=original_article.url,
                    description=original_article.excerpt,
                    negativeRate=article.comments_negative_rate,
                    positiveRate=article.comments_positive_rate,
                    neutralRate=article.comments_neutral_rate,
                    publishDate=original_article.date.replace(
                        tzinfo=timezone.utc
                    ).isoformat(),
                    sourceLogoUrl=None,  # TODO: get source logo url
                    sourceName=original_article.source,
                    title=original_article.title,
                )
            )

        keywords = [
            capitalize_first_letter(k).replace("_", " ") for k in topic.keywords
        ]

        topics.append(
            RestfulTopic(
                articles=articles,
                keywords=keywords,
                averagePositiveRate=topic.average_positive_rate,
                averageNegativeRate=topic.average_negative_rate,
                averageNeutralRate=topic.average_neutral_rate,
                totalNumberOfArticles=len(topic.articles),
                hasMoreArticles=len(topic.articles) > len(articles),
            )
        )

    two_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=2)
    categories = CategoryAnalysis.objects.filter(
        creation_date__gte=two_days_ago
    ).distinct(field="category")
    categories = [DB_CATEGORY_TO_URL[c] for c in categories]
    categories.sort(key=lambda x: CATEGORY_ORDER.index(x))
    availableCategories = {}
    for c in categories:
        availableCategories[c] = CATEGORY_TO_HUMAN_READABLE[c]

    result = RestfulTrend(
        id=str(category_analysis.id),
        topics=topics,
        creationDate=category_analysis.creation_date.isoformat(),
        categoryName=CATEGORY_TO_HUMAN_READABLE[
            DB_CATEGORY_TO_URL[category_analysis.category]
        ],
        availableCategories=availableCategories,
        hasMoreTopics=len(category_analysis.topics) > (page + 1) * page_size,
    )

    return dataclasses.asdict(result)


class NewestTrendAnalysis(Resource):
    def get(self, category):
        db_category_name = URL_TO_DB_CATEGORY[category]
        category_analysis = (
            CategoryAnalysis.objects.filter(category=db_category_name)
            .order_by("-creation_date")
            .first()
        )

        if not category_analysis:
            return {"error": "No trending data available"}, 404

        return serialize_trend_analysis(category_analysis, 0, 10)


class GetTrendAnalysis(Resource):
    def get(self):
        trend_id = request.args.get("trend_id", default=None)
        if not trend_id:
            return {"error": "trend_id is required"}, 400
        page = request.args.get("page", default=0, type=int)
        page_size = request.args.get("page_size", default=10, type=int)

        category_analysis = CategoryAnalysis.objects.get(id=trend_id)

        if not category_analysis:
            return {"error": "No trending data available"}, 404

        return serialize_trend_analysis(category_analysis, page, page_size)


class TopicDetail(Resource):
    def get(self, id, index):
        ca = CategoryAnalysis.objects.get(id=id)
        topic = ca.topics[index]
        articles = []
        for article in topic.articles:
            original_article = article.original_article
            articles.append(
                RestfulArticle(
                    id=str(original_article.id),
                    thumbnailUrl=original_article.img_url,
                    articleUrl=original_article.url,
                    description=original_article.excerpt,
                    negativeRate=article.comments_negative_rate,
                    positiveRate=article.comments_positive_rate,
                    neutralRate=article.comments_neutral_rate,
                    publishDate=original_article.date.replace(
                        tzinfo=timezone.utc
                    ).isoformat(),
                    sourceLogoUrl=None,  # TODO: get source logo url
                    sourceName=original_article.source,
                    title=original_article.title,
                )
            )

        keywords = [
            capitalize_first_letter(k).replace("_", " ") for k in topic.keywords
        ]

        result = RestfulTopic(
            articles=articles,
            keywords=keywords,
            averagePositiveRate=topic.average_positive_rate,
            averageNegativeRate=topic.average_negative_rate,
            averageNeutralRate=topic.average_neutral_rate,
            totalNumberOfArticles=len(topic.articles),
            hasMoreArticles=len(topic.articles) > len(articles),
        )

        return dataclasses.asdict(result)


api.add_resource(NewestTrendAnalysis, "/trending/category/<string:category>")
api.add_resource(GetTrendAnalysis, "/trending/byid")
api.add_resource(TopicDetail, "/topic/<string:id>/<int:index>")

if __name__ == "__main__":

    app.run(debug=True)
