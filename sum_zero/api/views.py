"""
Views for AJAX API calls. Mostly heavy backend work
that should not block the UI.
"""

from flask import abort, Blueprint, jsonify, request
from flask_login import current_user, login_required

from sum_zero.user.models import User
from sum_zero.summary.models import Summary


mod = Blueprint('apis', __name__, url_prefix="/apis/v1")

@mod.route('/subscribe', methods=['POST'])
def subscribe():
    user_id = int(request.form['user_id'])
    source_id = int(request.form['source_id'])
    if current_user.id != user_id:
        abort(404)
    if not current_user.is_subscribed(source_id):
        current_user.subscribe(source_id)
        return jsonify(source_id=source_id, user_id=user_id)
    abort(404)

@mod.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    user_id = int(request.form['user_id'])
    source_id = int(request.form['source_id'])
    if current_user.id != user_id:
        abort(404)
    if current_user.is_subscribed(source_id):
        current_user.unsubscribe(source_id)
        return jsonify(source_id=source_id, user_id=user_id)
    abort(404)

@mod.route('/bookmark', methods=['POST'])
def bookmark():
    user_id = int(request.form['user_id'])
    summary_id = int(request.form['summary_id'])
    if current_user.id != user_id:
        abort(404)
    if not current_user.has_bookmarked(summary_id):
        current_user.bookmark(summary_id)
        return jsonify(summary_id=summary_id, user_id=user_id)
    else:
        current_user.del_bookmark(summary_id)
        return jsonify(summary_id=summary_id, user_id=user_id)
