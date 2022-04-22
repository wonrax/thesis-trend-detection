import sys

sys.path.append("./data")

from crawler.tuoitre import TuoiTreCrawler
from crawler.vnexpress import VnExpressCrawler
from crawler.dantri import DanTriCrawler
from crawler.vietnamnet import VietnamnetCrawler
from crawler.base import Category
import json
import datetime
from zoneinfo import ZoneInfo
import threading
from queue import Queue, Empty
import time

BASE_PATH = "pipeline/tmp"
import os

assert os.path.isdir(BASE_PATH)

config = {"category": Category.THOI_SU, "do_crawl_comment": False, "delay": 0.5}

ttcrawler = TuoiTreCrawler(**config)
vncrawler = VnExpressCrawler(**config)
dtcrawler = DanTriCrawler(**config)
vnncrawler = VietnamnetCrawler(**config)

crawler_engines = [ttcrawler, vncrawler, dtcrawler, vnncrawler]

# Date range to crawl
end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
start_date = end_date - datetime.timedelta(days=2)
# start_date = end_date


def start_crawl_thread(crawler, queue):
    _articles = []
    try:
        _articles = crawler.crawl(start_date, end_date)
    except Exception as e:
        print(f"Error when crawling {crawler.SOURCE_NAME}, skipping...: {e}")
    queue.put(_articles)


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
        print(f"Timeout for {crawler.SOURCE_NAME}")

print(f"Got a total of {len(articles)} articles.")
print(f"Crawling took {time.time() - t1} seconds.")

# remove articles that have None date
articles = [article for article in articles if article.date is not None]
print(f"Usable amount: {len(articles)} articles (date not null).")

# sort articles by date
articles.sort(key=lambda x: x.date)

with open(BASE_PATH + "/articles.json", "w", encoding="utf-8") as f:
    file_content = json.dump(
        [article.to_dict() for article in articles],
        fp=f,
        indent=2,
        default=str,
        ensure_ascii=False,
    )
