if __name__ == "__main__":
    import sys

    sys.path.append(".")

from data.crawler.base import Category
from data.model.article import Article
from typing import List
import argparse
from pipeline.logger import get_common_logger

# Set up logger
logger = get_common_logger()


def perform_crawl(days: int = 1) -> List[Article]:
    """Crawl articles from the past days and store to the database

    Args:
        days (int, optional): Days to crawl. Defaults to 1.

    Returns:
        List[Article]: List of crawled articles
    """

    logger.info(f"Started crawling session for all crawlers, {days}-day range")

    from data.crawler.tuoitre import TuoiTreCrawler
    from data.crawler.vnexpress import VnExpressCrawler
    from data.crawler.dantri import DanTriCrawler
    from data.crawler.vietnamnet import VietnamnetCrawler
    from data.crawler.thanhnien import ThanhNienCrawler
    from data.crawler.nguoilaodong import NguoiLaoDongCrawler
    from data.crawler.zingnews import ZingNewsCrawler
    from pipeline.crawl import crawl

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

    articles = crawl(
        crawler_engines,
        categories,
        days=days,
        delay=0.25,
        do_crawl_comment=False,
        do_db_store=True,
        queue_timeout=None,
    )

    return articles


def perform_analysis_on_category(category: Category, days=1.5) -> None:
    """Perform analysis on crawled articles of a category and store to the database

    Args:
        days (float, optional): The range of articles to perform analysis on. Defaults to 1.5.

    Returns:
        Nothing
    """

    logger.info(f"Started analysis for {category.name}, {days}-day range")

    from common.constants import DATABASE_URL
    from mongoengine import connect
    from zoneinfo import ZoneInfo
    import datetime
    from pipeline.preprocess import preprocess_articles
    from pipeline.topic_cluster import topic_cluster
    from pipeline.topic_analysis import analyse_category
    from data.model.topic import Metrics

    assert DATABASE_URL
    connect(host=DATABASE_URL)

    if category == Category.MOI_NHAT:
        categories = [c for c in Category]
        categories.remove(Category.MOI_NHAT)
    else:
        categories = [category]

    # Get a list of chosen articles to analyze
    articles: List[Article] = []
    end_date = datetime.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    start_date = end_date - datetime.timedelta(days=days)
    for _c in categories:
        articles += Article.objects.filter(
            category=str(_c), date__gte=start_date, date__lte=end_date
        )

    # Perform preprocessing on articles
    processed_articles = preprocess_articles(articles)

    if len(processed_articles) < 10:
        logger.warning("Not enough articles to perform analysis")
        return

    topic_articles, coherence_score, silhouette_avg = topic_cluster(processed_articles)

    category_analysis = analyse_category(category, topic_articles)

    metrics = Metrics(
        silhouette_coefficient=silhouette_avg,
        topic_coherence=coherence_score,
    )
    category_analysis.metrics = metrics
    category_analysis.save()


def perform_analysis(days=1.5, do_crawl_beforehand=False) -> None:
    """Perform analysis on all available categories.

    Args:
        days (float, optional): The range of articles to perform analysis on. Defaults to 1.5.
    """

    if do_crawl_beforehand:
        import math

        perform_crawl(math.ceil(days))

    for category in Category:
        try:
            perform_analysis_on_category(category, days)
        except:
            logger.error(f"Failed to perform analysis on {category}")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser("Trending analysis pipeline.")

        parser.add_argument(
            "--days",
            type=float,
            default=1.5,
            help="The range of articles to perform analysis on.",
        )
        parser.add_argument(
            "--crawl", action="store_true", help="Crawl articles from the past days."
        )
        parser.add_argument(
            "--analysis",
            action="store_true",
            help="Perform analysis on all categories.",
        )

        args = parser.parse_args()

        if not args.crawl and not args.analysis:
            parser.print_help()
            exit(1)

        if args.analysis:
            perform_analysis(args.days, do_crawl_beforehand=args.crawl)
        else:
            perform_crawl(args.days)
    except:
        logger.critical(f"Unexpected error: {sys.exc_info()}")
