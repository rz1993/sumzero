from datetime import datetime, timedelta
from airflow import DAG
from airflow.hooks import PostgresHook
from airflow.models import BaseOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.decorators import apply_defaults

from config import SOURCE_LIST
from crawler import crawl_batch
from news_api import NewsAPI
from newspaper import Article

import os

'''
Constants
'''
CREATE_TABLE_QUERY = """
    CREATE TABLE news_meta1 (
        id SERIAL PRIMARY KEY,
        title TEXT,
        description TEXT,
        url VARCHAR(255),
        published_on TIMESTAMP with TIME ZONE
    );

    CREATE TABLE crawl_meta1 (
        id INT,
        crawl_time TIMESTAMP with TIME ZONE
    );
"""

'''
Python Callables
'''
def create_tables():
    conn = PostgresHook(postgres_conn_id='sumzero')
    conn.run(CREATE_TABLE_QUERY)

def convert_time(time):
    '''
    Normalize datetime objects and timestamps to format
    accepted by News API.
    '''
    if isinstance(time, datetime):
        return time.isoformat()

def meta_to_row(metadata):
    '''
    Transform metadata json response to a tuple.
    We encode to utf-8 so that non-ascii symbols
    are converted to their byte rep and can be stored in postgres.
    These can later be decoded (via .decode('utf-8')) to get
    back the original symbol.

    For `publishedAt` the time format returned by News API is isoformat
    with date, so postgres field must be TIMESTAMP with time zone.
    '''
    return (metadata['title'].encode('utf-8'),
            metadata['description'].encode('utf-8'),
            metadata['url'].encode('utf-8'),
            metadata['publishedAt'][:-1])

def get_news_meta(**kwargs):
    '''
    Retrieve metadata for news articles published on our set
    of sources during the time period between our last crawl
    and the current execution time.
    '''
    exec_date = kwargs.get('ds') or datetime.now()
    start_date = exec_date - timedelta(hours=3)

    api_key = kwargs.get('api_key')
    api = NewsAPI(api_key)

    query_args = {
        'sources': SOURCE_LIST,
        'page_size': 100,
        'from': convert_time(start_date),
        'to': convert_time(exec_date),
        'language': 'en'
    }

    pg_hook = PostgresHook(postgres_conn_id='sumzero')
    pagination = api.paginate_articles(**query_args)

    for resp in pagination:
        meta_list = resp.articles
        if meta_list:
            rows = (meta_to_row(d) for d in meta_list)
            pg_hook.insert_rows('news_meta1',
                rows=rows,
                target_fields=('title',
                    'description',
                    'url',
                    'published_on'
                ),
                commit_every=1000)

    return meta_list

def get_news_articles(**kwargs):
    '''
    Query db for urls that have not been scraped and then scrape them.

    Store articles in some kind of store...
    '''
    urls = []
    for url in urls:
        loader = Article(url)
        loader.download()
        loader.parse()

'''
DAGS
'''
default_args = {}

dag_crawl = DAG(dag_id="crawl_news",
                description="Crawl news articles from various sources.",
                start_date=datetime(2017, 12, 31),
                interval="0 3 * * *",
                default_args=default_args)

get_news_meta_task = PythonOperator(task_id='get_news_meta',
        provide_context=True,
        python_callable=get_news_meta,
        dag=dag_crawl)

get_news_dag = PythonOperator(task_id='get_news_articles',
        provide_context=True,
        python_callable=get_news_articles,
        dag=None)

'''
dag_summarize = DAG(dag_id="summarize",
                description="Pipeline for summarizing newly scraped articles.",
                start_date=datetime(2017, 12, 31),
                interval="0 1 * * *",
                default_args=default_args)
'''
