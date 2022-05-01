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
import time
from logger import get_common_logger


# Set up logger
logger = get_common_logger("crawler")


def crawl(
    crawler_engines,
    categories,
    days=1,
    delay=1,
    do_crawl_comment=False,
    do_db_store=False,
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

    def start_crawl_thread(crawler):
        total_crawled = 0
        try:
            for category in categories:
                config = {
                    "category": category,
                    "do_crawl_comment": do_crawl_comment,
                    "delay": delay,
                    "logger": logger,
                }
                _crawler = crawler(**config)
                logger.info(
                    f"Started crawling articles from ({_crawler.SOURCE_NAME}/{category.name})"
                )
                try:
                    urls = _crawler.crawl_urls(start_date, end_date)
                    urls = list(set(urls))
                    logger.info(
                        f"Extracting {len(urls)} articles from ({_crawler.SOURCE_NAME}/{category.name})..."
                    )
                    _articles = _crawler.crawl_articles(urls)
                    total_crawled += len(_articles)

                    if do_db_store:
                        logger.info(
                            f"Storing {len(_articles)} articles to database ({_crawler.SOURCE_NAME}/{category.name})..."
                        )
                        for article in _articles:
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
                                logger.exception(
                                    f"Couldn't save article to database: {article.url}"
                                )

                except:
                    logger.exception(
                        f"Error when crawling ({_crawler.SOURCE_NAME}/{_crawler.category.name}), skipping..."
                    )

        except Exception:
            logger.exception(f"Error when crawling {crawler}, skipping...")

    t1 = time.time()

    threads = []
    for crawler in crawler_engines:
        _t = threading.Thread(target=start_crawl_thread, args=(crawler,))
        threads.append(_t)
        _t.start()
    for _t in threads:
        _t.join()

    logger.info(f"Crawling took {time.time() - t1} seconds.")


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
