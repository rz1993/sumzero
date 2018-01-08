# News API crawler to retrieve news article meta data from sources
import requests

from datetime import datetime, timedelta


NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

def get_news(sources, api_key, from_date=None, to_date=None, language="en", sort_by="publishedAt", pages="all"):
    if from_date is None:
        from_date = (datetime.today() - timedelta(days=1)).isoformat()
    if to_date is None:
        to = datetime.today().isoformat()

    # Build parameters for news api
    params = {
        "sources": ",".join(sources),
        "apiKey": api_key,
        "from": from_date,
        "to": to_date,
        "language": language,
        "sortBy": sort_by
    }

    # Get the first page of results
    results = requests.get(NEWS_ENDPOINT, params=params)
    results_json = results.json()

    # If we want all pages, then paginate through all the results
    if pages == "all":
        page_size = len(results_json['articles'])
        total_results = results_json['totalResults']

        num_pages = total_results // page_size
        if total_results - num_pages * page_size:
            num_pages += 1

        for p in range(2, num_pages + 1):
            params.update(dict(page=p))
            r = requests.get(NEWS_ENDPOINT, params=params)
            r_json = r.json()
            results_json['articles'] += r_json['articles']

    return results_json
