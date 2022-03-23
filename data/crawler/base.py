from enum import Enum
class Category(Enum):
    SUC_KHOE = 1
    MOI_NHAT = 2
    THE_GIOI = 3
    THOI_SU = 4
    VAN_HOA = 5
    CONG_NGHE = 6
    THE_THAO = 7
    GIAO_DUC = 8

class Crawler:
    """
    Crawler base class
    """

    def __init__(
        self,
        category: Category,
        crawl_comment,
        delay,
        skip_these,
        newer_only,
        telegram_key,
    ):

        self.category = category
        self.crawl_comment = crawl_comment

        # A set of tuples (source name, article ids) to skip crawling.
        # Can be used to enlarge the existing data (skip the ones that already
        # crawled)
        self.skip_these = skip_these if skip_these else set()
        # Only get the articles newer than the existing ones in self.skip_these
        # regardless the limit.
        self.newer_only = newer_only

        # Amount of delay in seconds after each request
        # (to avoid overloading the server).
        self.delay = delay

        self.timeout = 60

        self.telegram_key = telegram_key

class EmptyPage(Exception):
    """
    Exception raised when the news page is empty, indicating we have reached
    the end of the database.
    """
    pass