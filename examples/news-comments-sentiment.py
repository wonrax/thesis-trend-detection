from models.sentiment import get_sentiment
from data.model.article import Article, Comment
from mongoengine import connect
from common.constants import DATABASE_URL
from typing import List
import random
import pandas as pd

if __name__ == "__main__":
    connect(host=DATABASE_URL)

    NUM_COMMENTS = 30
    comments: List[Comment] = []

    for article in Article.objects:
        if len(comments) > NUM_COMMENTS:
            break
        if random.random() < 0.90:
            continue
        if article.comments:
            comments += article.comments
            print(f"+{len(article.comments)}", end=" ")

    sentiments = []

    for comment in comments:
        sentiments.append((get_sentiment(comment.content).name, comment.content))

    # convert to pandas dataframe
    df = pd.DataFrame(sentiments, columns=["sentiment", "content"])
    
    # sort by sentiment
    df = df.sort_values("sentiment", ascending=False)

    # save to csv
    df.to_csv("examples/sentiments.csv", encoding="utf-8-sig", index=False)
