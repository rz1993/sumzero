"""
Views for AJAX API calls. Mostly heavy backend work
that should not block the UI.
"""

from flask import abort, Blueprint, jsonify, request, url_for
from flask_login import current_user, login_required

from sum_zero.api import constants as API_CONSTANTS
from sum_zero.user.models import User
from sum_zero.summary.models import Comment, Summary


mod = Blueprint('apis', __name__, url_prefix="/apis/v1")

@mod.route('/source/subscribe', methods=['POST'])
def subscribe():
    user_id = int(request.form['user_id'])
    source_id = int(request.form['source_id'])
    if current_user.id != user_id:
        abort(404)
    if not current_user.is_subscribed(source_id):
        current_user.subscribe(source_id)
        return jsonify(source_id=source_id, user_id=user_id)
    abort(404)

@mod.route('/source/unsubscribe', methods=['POST'])
def unsubscribe():
    user_id = int(request.form['user_id'])
    source_id = int(request.form['source_id'])
    if current_user.id != user_id:
        abort(404)
    if current_user.is_subscribed(source_id):
        current_user.unsubscribe(source_id)
        return jsonify(source_id=source_id, user_id=user_id)
    abort(404)

@mod.route('/summary/bookmark', methods=['POST'])
def bookmark():
    user_id = current_user.id
    summary_id = int(request.form['summary_id'])
    if not current_user.has_bookmarked(summary_id):
        current_user.bookmark(summary_id)
        return jsonify(summary_id=summary_id, user_id=user_id)
    else:
        current_user.del_bookmark(summary_id)
        return jsonify(summary_id=summary_id, user_id=user_id)

@mod.route('/summary/add_comment', methods=['POST'])
def add_comment():
    user_id = current_user.id
    summary_id = int(request.form['summary_id'])
    body = request.form['body']
    parent_id = request.form['parent_id']
    if parent_id == '':
        parent_id = None
    else:
        parent_id = int(parent_id)

    summary = Summary.query.get_or_404(summary_id)
    comment = summary.add_comment(body, user_id, parent_id=parent_id)
    full_name = current_user.first_name + " " + current_user.last_name
    avatar_url = current_user.get_avatar_url()
    return jsonify(comment_id=comment.id, body=comment.body,
        margin=comment.get_margin(), name=full_name,
        created_on=comment.pretty_date(), user_avatar_url=avatar_url)

@mod.route('/user/view_comments', methods=['GET'])
def get_comments():
    user_id = int(request.args.get('user_id'))
    page = int(request.args.get('page', 1))

    pagination = Comment.query.filter_by(user_id=user_id).paginate(
        page, per_page=API_CONSTANTS.COMMENTS_PER_PAGE)
    prev_url = ''
    if pagination.has_prev:
        prev_url = url_for('apis.get_comments', user_id=user_id,
                            page=pagination.prev_num)

    next_url = ''
    if pagination.has_next:
        next_url = url_for('apis.get_comments', user_id=user_id,
                            page=pagination.next_num)
                            
    json_comments = [c.to_json() for c in pagination.items]
    return jsonify(comments=json_comments, prev_url=prev_url,
        next_url=next_url)
