from models.sentiment import get_sentiment
from data.model.article import Article, Comment
from mongoengine import connect
from common.constants import DATABASE_URL
from typing import List
import random
import pandas as pd
from data.preprocess import Preprocess

if __name__ == "__main__":
    connect(host=DATABASE_URL)

    NUM_COMMENTS = 300
    comments: List[Comment] = []

    for article in Article.objects:
        if len(comments) > NUM_COMMENTS:
            break
        if article.comments:
            if random.random() < 0.50:
                continue
            comments.append(article.comments[0])
            print(f"+{1}", end=" ")

    sentiments = []

    for comment in comments:
        comment_content_segmented = Preprocess.segmentize(
            text=comment.content, do_teen_code=True, do_sentences=True
        )["sentences"]
        sentiments.append(
            (
                get_sentiment(comment_content_segmented, threshold=0.9).name,
                get_sentiment(comment_content_segmented, threshold=0.8).name,
                comment.content,
            )
        )

    # convert to pandas dataframe
    df = pd.DataFrame(sentiments, columns=["> 0.9", "> 0.8", "content"])

    # sort by sentiment
    df = df.sort_values(by=["> 0.9", "> 0.8"], ascending=False)

    # save to csv
    df.to_csv("examples/sentiments.csv", encoding="utf-8-sig", index=False)
