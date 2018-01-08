"""
Abstractions for text processing and NLP all belong in here.
"""
import spacy


def fit_nlp_to_articles(articles):
    nlp = spacy.load('en')
    return [nlp(a.get('text')) for a in articles]

def parse_to_tree(articles):
    pass

def tokenize(articles):
    pass

def tag_pos(articles):
    pass

def extract_entities(articles):
    pass

def score_phrases(articles):
    pass
