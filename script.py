"""
Command line script for generating fake data for sum_zero.
"""


from sum_zero import db
from sum_zero.user.models import User, UserAuth
from sum_zero.summary.models import Source, Summary, Tag

from faker import Faker

import random


fake = Faker()

def drop_tables(db):
    db.drop_all()

def initialize_tables(db):
    db.create_all()

def create_fake_users(db):
    print("Creating fake users...")
    users = []
    for i in range(10):
        email = fake.email()
        password = 'test'
        first_name, last_name = fake.name().split()[:2]
        bio = fake.paragraph(nb_sentences=1, variable_nb_sentences=True, ext_word_list=None)

        user_auth = {'username': email, 'password': password}
        user_profile = {'email': email, 'first_name': first_name,
            'last_name': last_name, 'bio': bio
        }
        user = UserAuth.create_user(user_auth, user_profile)
        users.append(user)
    print("Added {} fake users to the database.".format(len(users)))
    db.session.commit()

def create_fake_tags(db):
    print("Creating fake tags...")
    tags = ['money', 'tech', 'love', 'design', '2018']
    for tag_name in tags:
        tag = Tag(tag=tag_name)
        db.session.add(tag)
    print("Finished adding {} tags to the database.".format(len(tags)))
    db.session.commit()

def create_fake_sources(db):
    print("Creating fake sources...")
    sources = []
    for i in range(5):
        source = Source(name=fake.company())
        db.session.add(source)
        sources.append(source)
    print("Finished added {} sources to the database.".format(len(sources)))
    db.session.commit()

def create_fake_summaries(db):
    all_users = User.query.all()
    all_tags = Tag.query.all()
    all_sources = Source.query.all()

    if len(all_users) < 1:
        create_fake_users(db)
    if len(all_tags) < 1:
        create_fake_tags(db)
    if len(all_sources) < 1:
        create_fake_sources(db)

    print("Creating fake summaries...")
    for source in all_sources:
        num_subscribers = random.randint(1, len(all_users))
        subscribers = random.sample(all_users, num_subscribers)
        for user in subscribers:
            user.subscribe(source)

        for _ in range(10):
            summary = Summary(title=fake.catch_phrase(),
                              body=fake.text(),
                              published_date=fake.past_date(start_date='-30d'),
                              source_id=source.id,
                              link='http://www.cnn.com')
            db.session.add(summary)

            tags = random.sample(all_tags, 3)
            summary.set_tags(tags)
    print("Finished generating summaries...")
    db.session.commit()

if __name__ == '__main__':
    funcs = {'users': create_fake_users,
             'sources': create_fake_sources,
             'tags': create_fake_tags,
             'all': create_fake_summaries}

    import sys

    try:
        if sys.argv[1] == 'gen':
            initialize_tables(db)
            if len(sys.argv) < 3:
                funcs['all'](db)
            else:
                funcs[sys.argv[2]](db)
        elif sys.argv[1] == 'drop':
            drop_tables(db)
        else:
            print("Argument not recognized. Please use `gen` or `drop`.")
    except Exception as e:
        print("Whoops. Rolling back...")
        db.session.rollback()
        raise e
