from flask import Blueprint, render_template

from sum_zero import app, db
from sum_zero.summary.models import Source


mod = Blueprint('base', __name__, url_prefix='')

@mod.route('/')
def landing():
    return render_template('landing.html')

@mod.route('/home')
def index():
    # Return a dictionary of recent summaries for each source
    # These can only be done in separate queries
    sources = Source.query.all()
    summaries = {}
    for source in sources:
        source_summaries = source.summaries.limit(4).all()
        summaries[source.id] = source_summaries
    return render_template('home.html', sources=sources,
        summaries=summaries)
