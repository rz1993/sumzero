from flask import abort, Blueprint, render_template, request
from flask_login import current_user

from sum_zero.summary import constants as CONSTANTS
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
    page = request.args.get('page', 1, type=int)
    source = Source.query.get_or_404(source_id)
    pagination = source.summaries.paginate(
        page, per_page=CONSTANTS.SUMMARIES_PER_SOURCE_PAGE,
        error_out=False)
    return render_template('summary/source.html',
        source=source, pagination=pagination)

@mod.route('/tag/<tag_id>')
def get_tag(tag_id=None):
    if tag_id is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.get_or_404(tag_id)
    pagination = tag.summaries.paginate(
        page, per_page=CONSTANTS.SUMMARIES_PER_TAG_PAGE,
        error_out=False)
    return render_template('summary/tag.html',
        tag=tag, pagination=pagination)
