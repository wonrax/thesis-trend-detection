"""This script samples random articles from all categories and saves them to a json file.
For testing, model evaluation purposes etc.
"""

from mongoengine import connect
from common.constants import DATABASE_URL
from data.model.article import Article
from data.model.category import Category
from typing import List
import random
from bson import json_util
import json

NUM_ARTICLES_PER_CATEGORY = 100

if __name__ == "__main__":
    connect(host=DATABASE_URL)

    categories = [c for c in Category]
    categories.remove(Category.MOI_NHAT)
    articles: List[Article] = []
    for _c in categories:
        category_articles = []
        for article in Article.objects.filter(category=str(_c.name)):
            if len(category_articles) >= NUM_ARTICLES_PER_CATEGORY:
                break
            if random.random() < 0.5:
                continue
            category_articles.append(article)
        articles += category_articles
        print(f"{_c.name}: {len(category_articles)}")

    print(articles[0].title)
    articles = [a.to_json() for a in articles]
    articles = [json.loads(a) for a in articles]

    json_serialized_string = json.dumps(
        articles, default=json_util.default, ensure_ascii=False
    )

    # save to json
    with open("examples/sample_articles.json", "w", encoding="utf-8") as f:
        f.write(json_serialized_string)
