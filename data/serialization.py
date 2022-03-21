import json
from datetime import datetime
import csv
from model.article import Article, Comment


class ArticleSerialization:
    """
    Serialize and deserialize Article object.
    """

    @staticmethod
    def serialize(obj):
        """
        Transform an object to a serializable dictionary.
        Return a dictionary.
        """

        article_dict = obj.to_dict()

        # Store the comments and tags as JSON objects
        article_dict["comments"] = json.dumps(
            [x.to_dict() for x in obj.comments], ensure_ascii=False
        )

        article_dict["tags"] = json.dumps(obj.tags, ensure_ascii=False)

        return article_dict

    def json_to_comment(json_comment: dict):
        comment_dict = json_comment.copy()

        replies = []
        if len(json_comment["replies"]) > 0:
            replies = [
                ArticleSerialization.json_to_comment(reply)
                for reply in comment_dict["replies"]
            ]

        comment_dict["replies"] = replies
        comment_dict["likes"] = int(comment_dict["likes"])

        # 2021-11-08T18:18:45
        comment_dict["date"] = datetime.strptime(
            comment_dict["date"], "%Y-%m-%dT%H:%M:%S"
        )
        return Comment(**comment_dict)

    @staticmethod
    def deserialize(_dict):
        """
        Deserialize an object from a dictionary.
        Return an Article object.
        """

        obj_dict = _dict.copy()

        comments = [
            ArticleSerialization.json_to_comment(comment)
            for comment in json.loads(obj_dict["comments"])
        ]

        tags = json.loads(obj_dict["tags"])

        # 2021-11-08T18:18:45+07:00
        date = datetime.strptime(obj_dict["date"], "%Y-%m-%dT%H:%M:%S%z")

        likes = int(obj_dict["likes"]) if obj_dict["likes"] != "" else None

        obj_dict.pop("comments", None)
        obj_dict.pop("tags", None)
        obj_dict.pop("date", None)
        obj_dict.pop("likes", None)

        return Article(**obj_dict, comments=comments, tags=tags, date=date, likes=likes)


class FileStorage:
    """
    Store and retrieve objects to/from a file.
    """

    ENCODING = "utf-8-sig"
    NEW_LINE = ""

    @staticmethod
    def store(objects, file_path, mode="w", sort=True):
        """
        Store Article objects to a file.
        Return the file path.
        """
        sorted_objects = objects

        if sort:
            sorted_objects = sorted(objects, key=lambda o: o.date)

        with open(
            file_path, mode, newline=FileStorage.NEW_LINE, encoding=FileStorage.ENCODING
        ) as f:

            writer = csv.DictWriter(f, fieldnames=sorted_objects[0].to_dict().keys())

            if "a" not in mode:
                writer.writeheader()

            for obj in sorted_objects:
                writer.writerow(ArticleSerialization.serialize(obj))

        return file_path

    @staticmethod
    def load(file_path):
        """
        Load Article objects from a file.
        Return a list of object.
        """

        objects = []

        with open(
            file_path, "r", newline=FileStorage.NEW_LINE, encoding=FileStorage.ENCODING
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:
                objects.append(ArticleSerialization.deserialize(row))

        return objects
