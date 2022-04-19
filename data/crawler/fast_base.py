from enum import Enum
from newspaper import Article as NewspaperArticle
from model.article import Article, Comment
import time
from typing import List


class Category(Enum):
    SUC_KHOE = 1
    MOI_NHAT = 2
    THE_GIOI = 3
    THOI_SU = 4
    VAN_HOA = 5
    CONG_NGHE = 6
    THE_THAO = 7
    GIAO_DUC = 8


class FastCrawler:
    """
    Doesn't crawl faster, just easier to implement for new news sources.
    This crawler only crawls today and yesterday news.
    """

    def __init__(
        self,
        category: Category,
        do_crawl_comment: bool,
        delay: float = None,
    ):

        self.category = category
        self.do_crawl_comment = do_crawl_comment

        # Amount of delay in seconds after each request
        # (to avoid overloading the server).
        self.delay = delay

        self.timeout = 60

    def crawl_urls(self) -> "List[str]":
        """
        Crawl urls of today and yesterday news urls.
        Return a list of urls.
        """
        raise NotImplementedError

    def extract_comments(self, url) -> "List[Comment]":
        """
        Crawl comments of the article given its url.
        """
        raise NotImplementedError

    def extract_article(self, url) -> Article:
        article = NewspaperArticle(url)
        article.download()
        article.parse()
        # TODO convert to Article object
        return article

    def crawl(self) -> "List[Article]":
        """
        Crawl today and yesterday news.
        Return a list of articles.
        """

        urls = self.crawl_urls()
        articles = []
        for url in urls:
            article = self.extract_article(url)
            if self.do_crawl_comment:
                comments = self.crawl_comments(url)
                article.comments = comments
            if self.delay is not None:
                time.sleep(self.delay)

        return articles
