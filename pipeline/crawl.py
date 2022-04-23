import sys

sys.path.append(".")

from data.crawler.tuoitre import TuoiTreCrawler
from data.crawler.vnexpress import VnExpressCrawler
from data.crawler.dantri import DanTriCrawler
from data.crawler.vietnamnet import VietnamnetCrawler
from data.crawler.thanhnien import ThanhNienCrawler
from data.crawler.base import Category
import json
import datetime
from zoneinfo import ZoneInfo
import threading
from queue import Queue, Empty
import time
import logging

BASE_PATH = "pipeline"
STORAGE_PATH = BASE_PATH + "/tmp"
import os

assert os.path.isdir(STORAGE_PATH)

LOG_LEVEL = logging.DEBUG
log_filename = f"{BASE_PATH}/logs/{__name__}.log"
os.makedirs(os.path.dirname(log_filename), exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
file_handler = logging.FileHandler(log_filename, encoding="utf-8")
stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
stream_handler.setLevel(LOG_LEVEL)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Date range to crawl
end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
start_date = end_date - datetime.timedelta(days=2)
start_date = end_date


def start_crawl_thread(crawler, queue):
    logger.info(f"Started crawling articles from {crawler.SOURCE_NAME}")
    _articles = []
    try:
        # Crawl all urls first
        urls = []
        for category in Category:
            if category is Category.MOI_NHAT:
                continue
            config = {
                "category": category,
                "do_crawl_comment": False,
                "delay": 0.5,
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

        # Crawl articles
        _articles = _crawler.crawl_articles(urls)

    except Exception as e:
        logger.exception(f"Error when crawling {crawler}, skipping...")

    queue.put(_articles)


crawler_engines = [
    DanTriCrawler,
    ThanhNienCrawler,
    TuoiTreCrawler,
    VietnamnetCrawler,
    VnExpressCrawler,
]

crawler_result_queue = Queue(len(crawler_engines))

t1 = time.time()

for crawler in crawler_engines:
    threading.Thread(
        target=start_crawl_thread, args=(crawler, crawler_result_queue)
    ).start()

articles = []

for _ in crawler_engines:
    try:
        articles += crawler_result_queue.get(timeout=15 * 60)
    except Empty:
        logger.exception(f"Timeout for {crawler.SOURCE_NAME}")

logger.info(f"Crawling took {time.time() - t1} seconds.")
logger.info(f"Got a total of {len(articles)} articles.")

# remove articles that have None date
articles = [article for article in articles if article.date is not None]
logger.info(f"Usable amount: {len(articles)} articles (date not null).")

# sort articles by date
articles.sort(key=lambda x: x.date)

with open(STORAGE_PATH + "/articles.json", "w", encoding="utf-8") as f:
    file_content = json.dump(
        [article.to_dict() for article in articles],
        fp=f,
        indent=2,
        default=str,
        ensure_ascii=False,
    )
