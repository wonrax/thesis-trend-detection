from mongoengine import *


class Comment(EmbeddedDocument):
    """
    User comment in an article.
    """

    # ID got from news source
    id_source = StringField(required=True, null=False)
    author = StringField(null=True)
    content = StringField(null=False)
    date = DateTimeField()
    replies = ListField(EmbeddedDocumentField("self"), null=True)
    likes = IntField(null=True)

    def __str__(self):
        return (
            "ID: {}\nAuthor: {}\nContent: {}\nLikes: {}\nDate: {}\nReplies: {}".format(
                self.id_source,
                self.author,
                self.content,
                self.likes,
                self.date,
                len(self.replies),
            )
        )

    def __hash__(self):
        return hash(self.id_source)

    def __eq__(self, __o: object) -> bool:
        return self.id_source == __o.id

    def __getitem__(self, key):
        return self.replies[key]

    def to_dict(self):

        replies = [reply.to_dict() for reply in self.replies]

        date = self.date.isoformat() if self.date else None

        _dict = self.__dict__.copy()

        _dict.update(date=date, replies=replies)

        return _dict


class Article(Document):

    # ID got from news source
    id_source = StringField(required=True, unique_with="source")
    source = StringField(required=True, null=False)
    title = StringField(required=True, null=False)
    date = DateTimeField()
    authors = ListField(StringField(), null=True)
    excerpt = StringField(null=True)
    content = StringField(null=True)
    url = StringField(null=False)
    img_url = StringField(null=False)
    comments = ListField(EmbeddedDocumentField(Comment), null=True)
    tags = ListField(StringField(), null=True)
    category = StringField(null=True)
    likes = IntField(null=True)

    def __str__(self):
        return (
            "ID: {}\nTitle: {}\nExcerpt: {}\nDate: {}\nAuthor: {}\n"
            + "Source: {}\nCategory: {}\nURL: {}\nImage: {}\nTags: {}\n"
            + "Likes: {}\nComments: {}\n-----\n{}"
        ).format(
            self.id_source,
            self.title,
            self.excerpt,
            self.date,
            self.authors,
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
        return hash(self.source + self.id_source)

    def __eq__(self, __o: object) -> bool:
        return self.id_source == __o.id and self.source == __o.source

    def to_dict(self):

        date = self.date.isoformat() if self.date else None

        comments = [comment.to_dict() for comment in self.comments]

        _dict = self.__dict__.copy()

        _dict.update(date=date, comments=comments)

        return _dict
