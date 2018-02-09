from functools import wraps
from urllib import parse

import requests


def parse_kwargs_for_args(arg_names, kwargs):
    """
    Parses `kwargs` for certain argument names and only
    passes the parsed keyword arguments to the function.
    """
    new_kwargs = {}
    for arg in arg_names:
        if arg in kwargs:
            new_kwargs.update({arg: kwargs.get(arg)})
    return new_kwargs


class BaseResponse:
    def __init__(self, response):
        self._raw_resp = response
        self._resp = response.json()

    def __repr__(self):
        return '<{} [{}]>'.format(
            self.__class__.__name__,
            self.status)

    @property
    def status(self):
        return self._resp.get('status')

    def get(self, key, default=None):
        return self._resp.get(key, default)

    def json(self):
        return self._raw_resp.json()


class SourceResponse(BaseResponse):
    @property
    def sources(self):
        return self._resp.get('sources')

    def urls(self):
        sources = self.sources
        return [s.get('url') for s in self.sources]


class ArticleResponse(BaseResponse):
    @property
    def articles(self):
        return self._resp.get('articles')

    @property
    def total_results(self):
        return self._total_results

    def urls(self):
        articles = self.articles
        return [a.get('url') for a in self.articles]


class NewsAPI:
    '''
    Client class for News API. Will need to add exceptions for
    error statuses (e.g. invalid API keys).
    '''
    def __init__(self, api_key):
        self.headlines_endpoint = "https://newsapi.org/v2/top-headlines"
        self.articles_endpoint = "https://newsapi.org/v2/everything"
        self.sources_endpoint = "https://newsapi.org/v2/sources"

        # Query parameters for each endpoint
        self._articles_args = ['q', 'sources', 'domains', 'from', 'to',
            'language', 'sortBy', 'pageSize', 'page']
        self._headlines_args = ['country', 'category', 'sources', 'q',
            'pageSize', 'page']
        self._sources_args = ['category', 'language', 'country']

        # Parameter options
        self._categories = ['business',
            'entertainment',
            'general',
            'health',
            'science',
            'sports',
            'technology']

        # Store api key
        self.api_key = api_key

    def _get(self, endpoint, kwargs):
        """
        Generic GET request hitting the target endpoint.
        """
        kwargs['apiKey'] = self.api_key
        resp = requests.get(endpoint, params=kwargs)
        return resp

    def _has_next(self, page, page_size, total_size):
        return (page+1) * page_size < total_size

    def _map_to_response(self, endpoint, resp):
        return response_types[endpoint](resp)

    def sources(self, **kwargs):
        """
        GET sources supported by News API.
        """
        params = parse_kwargs_for_args(self._sources_args, kwargs)
        resp = self._get(self.sources_endpoint, params)
        return SourceResponse(resp)

    def top_headlines(self, **kwargs):
        """
        GET top news headlines.
        """
        params = parse_kwargs_for_args(self._headlines_args, kwargs)
        resp = self._get(self.headlines_endpoint, params)
        return ArticleResponse(resp)

    def articles(self, **kwargs):
        """
        GET top news articles.
        """
        params = parse_kwargs_for_args(self._articles_args, kwargs)
        resp = self._get(self.articles_endpoint, params)
        return ArticleResponse(resp)

    def paginate_articles(self, page_size=20, limit=None, **kwargs):
        page = kwargs.get('page', 0)
        resp = self.articles(pageSize=page_size, **kwargs)

        if limit is None:
            total_results = resp.get('totalResults', 0)
        else:
            total_results = min(resp.get('totalResults', 0), limit)

        yield resp
        while self._has_next(page, page_size, total_results):
            page += 1
            yield self.articles(page=page,
                pageSize=page_size, **kwargs)

    def paginate_headlines(self, page_size=20, limit=None, **kwargs):
        page = kwargs.get('page', 0)
        resp = self.top_headlines(pageSize=page_size, **kwargs)

        if limit is None:
            total_results = resp.get('totalResults')
        else:
            total_results = min(resp.get('totalResults'), limit)

        yield resp
        while self._has_next(page, page_size, total_results):
            page += 1
            yield self.top_headlines(page=page,
                pageSize=page_size, **kwargs)
