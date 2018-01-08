from config import DB_URI, NEWS_API_KEY, SOURCE_LIST
from news_api_crawler import get_news
from scrapers import download_article_html, parse_text_from_html

from storage import Storage

from datetime import datetime, timedelta


DB_NAME = "sumzero"
ARTICLE_COLLECTION = "articles"
SUMMARY_COLLECTION = "summaries"
TIME_COLLECTION = "times"

def articles_handler(event, context, test=False):
    store = Storage(DB_URI)
    store.connect_db(DB_NAME)

    # Retrieve and the last scrape time and scrape articles from then
    store.set_collection(TIME_COLLECTION)
    from_time = store.find().sort({'scrape_time': -1}).limit(1)
    from_time = from_time.get('scrape_time')
    to_time = datetime.time().isoformat()

    news_meta = get_news(
        SOURCE_LIST, NEWS_API_KEY,
        from_date=from_time, to_date=to_time
    )
    new_scrape_event = {'scrape_time': to_time}
    store.insert(new_scrape_event) # Persist most recent scrape time record

    articles_meta = news_meta['articles']
    if test:
        articles_meta = articles_meta[:20]

    # Extract the urls from the article meta information
    # Download the full article html from the original source
    urls = [a.get('url') for a in articles_meta]
    articles = download_article_html(urls)
    parse_text_from_html(articles) # Parse out article text from html
    for i, a in enumerate(articles):
        articles_meta[i]['text'] = a.text

    store.set_collection(ARTICLE_COLLECTION)

    store.insert(articles_meta)
    return articles_meta

def gen_summaries(event, context):
    store = Storage(DB_URI)
    store.connect_db(DB_NAME)
    store.set_collection(ARTICLE_COLLECTION)

    articles = store.find_all({})
