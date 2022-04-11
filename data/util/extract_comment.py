import sys, os
# get absolute path of root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

sys.path.append(root_dir)

from serialization import FileStorage

articles = FileStorage.load("data/suc-khoe-articles-truncated.csv")

comments = []
for a in articles:
    for comment in a.comments:
        comments.append(comment.content)

print(len(comments))
print(comments[:10])

pd.DataFrame(comments).to_csv("data/suc-khoe-comments-truncated.csv", index=False, encoding="utf-8-sig")

# load comments from csv using pandas