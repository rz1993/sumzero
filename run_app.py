"""
Application: SumZero
Author: Roland Zhou

This is the top level script to run the Flask app so that all imports
are global from the top `sum_zero` module. If the app is run from
within the sum_zero/__init__.py, Python will not detect sum_zero as
a package.

The `config.py` module must also be in the root directory since the
app is imported to the root level.
"""

from sum_zero import app, manager


if __name__ == "__main__":
    print("Running sum_zero app...")
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    app.run(port=8000)
