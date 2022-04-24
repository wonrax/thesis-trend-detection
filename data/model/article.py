import datetime
from typing import List


class Comment:
    """
    User comment in an article.
    """

    def __init__(
        self, id, author=None, content=None, date=None, replies=[], likes=None
    ):
        self.id = id
        self.author = author
        self.content = content
        self.date = date
        self.replies = replies  # list of Comment objects
        self.likes = likes

    def __str__(self):
        return (
            "ID: {}\nAuthor: {}\nContent: {}\nLikes: {}\nDate: {}\nReplies: {}".format(
                self.id,
                self.author,
                self.content,
                self.likes,
                self.date,
                len(self.replies),
            )
        )

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id

    def __getitem__(self, key):
        return self.replies[key]

    def to_dict(self):

        replies = [reply.to_dict() for reply in self.replies]

        date = self.date.isoformat() if self.date else None

        _dict = self.__dict__.copy()

        _dict.update(date=date, replies=replies)

        return _dict


class Article:
    def __init__(
        self,
        id: str,
        source: str,
        title: str = None,
        date: datetime.datetime = None,
        tags: List[str] = [],
        author: List[str] = None,
        excerpt: str = None,
        content: str = None,
        url: str = None,
        img_url: str = None,
        comments: List[Comment] = [],
        category=None,
        likes: int = None,
        comment_negative_rate: float = None,
        comment_positive_rate: float = None,
        comment_neutral_rate: float = None,
    ):

        self.id = id
        self.title = title
        self.date = date
        self.source = source
        self.author = author
        self.excerpt = excerpt
        self.content = content
        self.url = url
        self.img_url = img_url
        self.comments = comments  # List of Comment objects
        self.tags = tags
        self.category = category
        self.likes = likes  # Like count
        self.comment_negative_rate = comment_negative_rate
        self.comment_positive_rate = comment_positive_rate
        self.comment_neutral_rate = comment_neutral_rate

    def __str__(self):
        return (
            "ID: {}\nTitle: {}\nExcerpt: {}\nDate: {}\nAuthor: {}\n"
            + "Source: {}\nCategory: {}\nURL: {}\nImage: {}\nTags: {}\n"
            + "Likes: {}\nComments: {}\n-----\n{}"
        ).format(
            self.id,
            self.title,
            self.excerpt,
            self.date,
            self.author,
            self.source,
            self.category,
            self.url,
            self.img_url,
            self.tags,
            self.likes,
            len(self.comments),
            self.content,
        )

    def __hash__(self):
        return hash(self.source + self.id)

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id and self.source == __o.source

    def to_dict(self):

        date = self.date.isoformat() if self.date else None

        comments = [comment.to_dict() for comment in self.comments]

        _dict = self.__dict__.copy()

        _dict.update(date=date, comments=comments)

        return _dict
