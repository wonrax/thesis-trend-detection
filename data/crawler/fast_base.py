from enum import Enum
from newspaper import Article as NewspaperArticle
from model.article import Article, Comment
import time
from typing import List
import unicodedata
from dateutil.parser import parse
import datetime
from zoneinfo import ZoneInfo


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

    def get_id_by_url(self, url):
        """
        Get the id of the article given its url.
        """
        raise NotImplementedError

    def extract_article(self, url) -> Article:
        article = NewspaperArticle(url)
        article.download()
        article.parse()

        pub_date = article.publish_date
        if isinstance(pub_date, str):
            pub_date = parse(pub_date)

        return Article(
            id=self.get_id_by_url(url),
            source=self.SOURCE_NAME,
            title=article.title,
            date=pub_date,
            tags=list(article.tags),
            author=article.authors,
            excerpt=article.meta_description,
            content=article.text,
            url=url,
            img_url=article.top_img,
            comments=[],
            category=self.category,
            likes=None,
        )

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

            articles.append(article)

            if self.delay is not None:
                time.sleep(self.delay)

        return articles

    def get_datetime_today_yesterday(self):
        """
        Get today and yesterday datetime.
        """
        today = datetime.datetime.now(ZoneInfo("Asia/Jakarta"))
        yesterday = today - datetime.timedelta(days=1)
        return today, yesterday

    def normalize_unicode(self, unicode_str):
        """
        Normalize unicode string (e.g. remove \xa0 characters).
        """
        return unicodedata.normalize("NFKC", unicode_str)
