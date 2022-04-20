from crawler.fast_tuoitre import FastTuoiTreCrawler
from crawler.fast_vnexpress import FastVnExpressCrawler
from crawler.fast_base import Category
import json

config = {"category": Category.SUC_KHOE, "do_crawl_comment": False, "delay": None}

ttcrawler = FastTuoiTreCrawler(**config)
vncrawler = FastVnExpressCrawler(**config)

articles = []
for crawler in [ttcrawler, vncrawler]:
    articles += crawler.crawl()

with open("./tmp/articles.json", "w", encoding="utf-8") as f:
    file_content = json.dump(
        [article.to_dict() for article in articles],
        fp=f,
        indent=2,
        default=str,
        ensure_ascii=False,
    )
