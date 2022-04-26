if __name__ == "__main__":
    import sys

    sys.path.append(".")

from data.crawler.tuoitre import TuoiTreCrawler
from data.crawler.vnexpress import VnExpressCrawler
from data.crawler.dantri import DanTriCrawler
from data.crawler.vietnamnet import VietnamnetCrawler
from data.crawler.thanhnien import ThanhNienCrawler
from data.crawler.nguoilaodong import NguoiLaoDongCrawler
from data.crawler.zingnews import ZingNewsCrawler
from data.crawler.base import Category
from data.model.article import Article
import datetime
from zoneinfo import ZoneInfo
import threading
from queue import Queue, Empty
import time
from pipeline.logger import get_common_logger


# Set up logger
logger = get_common_logger("crawler")


def crawl(
    crawler_engines,
    categories,
    days=1,
    delay=1,
    do_crawl_comment=False,
    do_db_store=False,
    queue_timeout=30 * 60,  # 15 minutes
):

    # Date range to crawl
    assert days > 0
    end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    start_date = end_date - datetime.timedelta(days=days - 1)

    # Check database connection
    if do_db_store:
        from mongoengine import connect
        from common.constants import DATABASE_URL

        assert DATABASE_URL
        connect(host=DATABASE_URL)

    def start_crawl_thread(crawler, queue):
        _articles = []
        try:
            for category in categories:
                logger.info(f"Started crawling articles from {crawler} at {category}")
                urls = []
                config = {
                    "category": category,
                    "do_crawl_comment": do_crawl_comment,
                    "delay": delay,
                    "logger": logger,
                }
                _crawler = crawler(**config)
                try:
                    urls += _crawler.crawl_urls(start_date, end_date)
                except:
                    logger.exception(
                        f"Error when crawling {_crawler.SOURCE_NAME} with category {_crawler.category}, skipping..."
                    )
                urls = list(set(urls))

                try:
                    # Crawl articles
                    _articles += _crawler.crawl_articles(urls)
                except:
                    logger.exception(
                        f"Error when extracting articles for {categories} of {_crawler.SOURCE_NAME}"
                    )

        except Exception:
            logger.exception(f"Error when crawling {crawler}, skipping...")

        queue.put(_articles)

    crawler_result_queue = Queue(len(crawler_engines))

    t1 = time.time()

    for crawler in crawler_engines:
        t = threading.Thread(
            target=start_crawl_thread, args=(crawler, crawler_result_queue)
        ).start()

    articles = []

    for _ in crawler_engines:
        try:
            articles += crawler_result_queue.get(timeout=queue_timeout)
        except Empty:
            logger.exception(f"Timeout for {crawler.SOURCE_NAME}")

    logger.info(f"Crawling took {time.time() - t1} seconds.")
    logger.info(f"Got a total of {len(articles)} articles.")

    if do_db_store:
        logger.info("Started storing articles to database...")
        for article in articles:
            try:
                Article.objects(
                    id_source=article.id_source, source=article.source
                ).update(
                    upsert=True,
                    set__title=article.title,
                    set__date=article.date,
                    set__authors=article.authors,
                    set__excerpt=article.excerpt,
                    set__content=article.content,
                    set__url=article.url,
                    set__img_url=article.img_url,
                    set__comments=article.comments,
                    set__tags=article.tags,
                    set__category=article.category,
                )
            except:
                logger.exception(f"Couldn't save article to database: {article.url}")

    return articles


if __name__ == "__main__":
    crawler_engines = [
        DanTriCrawler,
        ThanhNienCrawler,
        TuoiTreCrawler,
        VietnamnetCrawler,
        VnExpressCrawler,
        NguoiLaoDongCrawler,
        ZingNewsCrawler,
    ]

    categories = [category for category in Category]
    categories.remove(Category.MOI_NHAT)

    crawl(
        crawler_engines,
        categories,
        days=2,
        delay=0.5,
        do_crawl_comment=False,
        do_db_store=True,
    )
