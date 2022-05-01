from data.crawler.base import Category
from data.model.article import Article
from typing import List
import argparse
from logger import get_common_logger
from typing import List

# Set up logger
logger = get_common_logger()


def perform_crawl(
    category: Category, days: int = 1, source: str = "all", do_crawl_comment=True
) -> List[Article]:
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
    from crawl import crawl

    MAP_STRING_TO_SOURCE = {
        "dantri": DanTriCrawler,
        "vnexpress": VnExpressCrawler,
        "tuoitre": TuoiTreCrawler,
        "vietnamnet": VietnamnetCrawler,
        "thanhnien": ThanhNienCrawler,
        "nguoilaodong": NguoiLaoDongCrawler,
        "zingnews": ZingNewsCrawler,
    }

    if source == "all":
        crawler_engines = [
            DanTriCrawler,
            ThanhNienCrawler,
            TuoiTreCrawler,
            VietnamnetCrawler,
            VnExpressCrawler,
            NguoiLaoDongCrawler,
            ZingNewsCrawler,
        ]
    elif source in MAP_STRING_TO_SOURCE:
        crawler_engines = [MAP_STRING_TO_SOURCE[source]]
    else:
        logger.error(f"Invalid source: {source}")
        return

    categories = []
    if category == Category.MOI_NHAT:
        categories = [c for c in Category]
        categories.remove(Category.MOI_NHAT)
    else:
        categories = [category]

    articles = crawl(
        crawler_engines,
        categories,
        days=days,
        delay=0.25,
        do_crawl_comment=do_crawl_comment,
        do_db_store=True,
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
            category=str(_c.name), date__gte=start_date, date__lte=end_date
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

    logger.info(f"Saving analysis for {category.name} to database")
    category_analysis.save()


def perform_analysis(category: Category = Category.MOI_NHAT, days=1.5) -> None:
    """Perform analysis on all available categories.

    Args:
        days (float, optional): The range of articles to perform analysis on. Defaults to 1.5.
    """

    categories = [category]

    for category in categories:
        try:
            perform_analysis_on_category(category, days)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            logger.exception(f"Failed to perform analysis on {category}")


if __name__ == "__main__":
    MAP_STRING_TO_CATEGORY = {}
    for category in Category:
        MAP_STRING_TO_CATEGORY[category.name.lower()] = category

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
        parser.add_argument(
            "--category",
            type=str,
            default="all",
            help="The category to perform analysis on.",
        )
        parser.add_argument(
            "--source",
            type=str,
            default="all",
            help="The source to crawl articles from.",
        )

        args = parser.parse_args()

        if not args.crawl and not args.analysis:
            parser.print_help()
            exit(1)

        if args.category.lower() == "all":
            category = Category.MOI_NHAT
        else:
            if args.category.lower() not in MAP_STRING_TO_CATEGORY:
                logger.error(
                    f"Invalid category {args.category}. Available categories: {[c.name for c in Category]}"
                )
                exit(1)
            category = MAP_STRING_TO_CATEGORY[args.category.lower()]

        if args.analysis:
            if args.category.lower() == "all":
                categories = [c for c in Category]
                categories.remove(Category.MOI_NHAT)
            else:
                categories = [category]
            for _category in categories:
                perform_analysis(category=_category, days=args.days)
        elif args.crawl:
            perform_crawl(
                category=category,
                days=args.days,
                source=args.source,
                do_crawl_comment=True,
            )
    except:
        import sys

        logger.critical(f"Unexpected error: {sys.exc_info()}")
