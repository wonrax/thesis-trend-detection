from crawler.fast_tuoitre import FastTuoiTreCrawler
from crawler.fast_base import Category

ttcrawler = FastTuoiTreCrawler(
    category=Category.MOI_NHAT, do_crawl_comment=False, delay=None
)

articles = ttcrawler.crawl()

print("Length of articles: ", len(articles))
for article in articles:
    print(article)
    print("==================\n")