import newspaper
import time

from newspaper import Article, Source
from newspaper import mthreading, network


REQUEST_INTERVAL = 1
THREAD_QUEUE_TIMEOUT = 5

def _throttle_download(article, interval=REQUEST_INTERVAL, **kwargs):
    """Throttle the http requests so we don't get blacklisted"""
    start = time.time()
    article.download(**kwargs)
    duration = time.time() - start
    if interval > duration:
        time.sleep(interval - duration)

def download_article_html(urls, num_threads=1, verbose=True):
    """Download the articles using multiple threads if specified"""
    articles = [Article(url) for url in urls]
    if num_threads > 1:
        tpool = mthreading.ThreadPool(num_threads, THREAD_QUEUE_TIMEOUT)
        for i, a in enumerate(articles):
            tpool.add_task(_throttle_download, a)
        tpool.wait_completion()
    else:
        for i, a in enumerate(articles):
            if verbose:
                print("Downloading article {}".format(i))
            _throttle_download(a)

    return articles

def parse_text_from_html(articles, num_threads=1, verbose=True):
    if num_threads > 1:
        tpool = mthread.ThreadPool(num_threads, THREAD_QUEUE_TIMEOUT)
        for a in articles:
            tpool.add_task(a.parse)

        tpool.wait_completion()
    else:
        for i, a in enumerate(articles):
            if verbose:
                print("Parsing article {}".format(i))
            a.parse()
