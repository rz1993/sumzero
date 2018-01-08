from sum_zero import db
from sum_zero.user.models import UserAuth

# Initialize database
db.create_all()

# Populate with test users
users = []
