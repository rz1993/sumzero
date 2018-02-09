from newspaper import Article, ArticleException

import time


def crawl_article_from_meta(metadata, throttle=True, seconds=1):
    '''
    From a single News API meta dictionary, crawl the main article.
    '''
    start_time = time.time()
    loader = Article(metadata.get('url'))
    loader.download()
    loader.parse()

    if throttle:
        time.sleep(max(seconds - time.time() + start_time, 0))

    return loader

def to_json(article, metadata):
    '''
    Schema function for merging a loaded article and its metadata.
    '''
    return {
        'description': metadata.get('description'),
        'published_date': metadata.get('publishedAt'),
        'source_id': metadata.get('source').get('id'),
        'text': article.text,
        'title': article.title,
        'url': metadata.get('url')}

def crawl_batch(meta_batch):
    '''
    Crawl a batch of news articles from an array of News API metadata,
    appending successful and failed crawls to different arrays.
    Batches are ultimately persisted onto disk in separate files and
    later have summaries dumped into a database store.
    '''
    crawled_articles = []
    failed_articles = []

    for metadata in meta_batch:
        try:
            article = crawl_article_from_meta(metadata)
            json_article = to_json(article, metadata)
            crawled_articles.append(json_article)
        except ArticleException as exception:
            failed_articles.append(metadata)

    return crawled_articles, failed_articles
