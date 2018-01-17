from flask import abort, Blueprint, render_template
from flask_login import current_user

from sum_zero.summary.models import Source, Summary, Tag


mod = Blueprint('summary', __name__, url_prefix='/summary')

@mod.route('/<summary_id>/')
def get_summary(summary_id=None):
    if summary_id is None:
        abort(404)
    summary = Summary.query.get_or_404(summary_id)
    return render_template('summary/summary.html', summary=summary)

@mod.route('/source/<source_id>')
def get_source(source_id=None):
    if source_id is None:
        abort(404)
    source = Source.query.get_or_404(source_id)
    paginate = source.summaries.paginate()
    return render_template('summary/source.html', source=source, paginate=paginate)

@mod.route('/tag/<tag_id>')
def get_tag(tag_id=None):
    if tag_id is None:
        abort(404)
    tag = Tag.query.get_or_404(tag_id)
    paginate = tag.summaries.paginate()
    return render_template('summary/tag.html', tag=tag, paginate=paginate)
