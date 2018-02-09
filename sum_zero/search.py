from sum_zero import db
from sum_zero.summary.models import Summary

from collections import Counter


def most_common_tags(summaries, top_n=10):
    """
    Count and sort tags given a list of summaries
    """
    tag_counts = Counter()
    for s in summaries:
        tag_counts.update(s.tags)

    return [tag for tag, count in tag_counts.most_common(top_n)]

def search_db(query, order_by='published_on', search_title=True,
              search_body=True, limit=100):
    """
    Summary search using basic query text matching
    """
    if query is None:
        return []

    # Create a basic `like` query
    query = query.strip()
    base_query = '%{}%'.format(query)

    base_queryset = Summary.query

    title_clause = Summary.title.like(base_query)
    body_clause = Summary.body.like(base_query)

    # Create the filter clause depending on what we want to match
    if search_title and search_body:
        clause = db.or_(title_clause, body_clause)
    elif search_title:
        clause = title_clause
    else:
        clause = body_clause

    queryset = base_queryset.filter(clause)

    if order_by == 'published_on':
        queryset.order_by(db.desc(Summary.published_date))
    else:
        queryset.order_by(Summary.title)

    return queryset.limit(limit)
