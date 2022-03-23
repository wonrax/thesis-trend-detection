class Article:
    def __init__(
        self,
        id,
        source,
        title=None,
        date=None,
        tags=[],
        author=None,
        excerpt=None,
        content=None,
        url=None,
        comments=[],
        category=None,
        likes=None,
    ):

        self.id = id
        self.title = title
        self.date = date
        self.source = source
        self.author = author
        self.excerpt = excerpt
        self.content = content
        self.url = url
        self.comments = comments  # List of Comment objects
        self.tags = tags
        self.category = category
        self.likes = likes  # Like count

    def __str__(self):
        return (
            "ID: {}\nTitle: {}\nExcerpt: {}\nDate: {}\nAuthor: {}\n"
            + "Source: {}\nCategory: {}\nURL: {}\nTags: {}\n"
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

    def __getitem__(self, key):
        return self.replies[key]

    def to_dict(self):

        replies = [reply.to_dict() for reply in self.replies]

        date = self.date.isoformat() if self.date else None

        _dict = self.__dict__.copy()

        _dict.update(date=date, replies=replies)

        return _dict
