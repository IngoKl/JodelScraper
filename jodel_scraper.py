from pathlib import Path
from sqlalchemy import exists
from sqlalchemy.orm import sessionmaker
import jodel_api
import jodel_scraper_db
import json
import logging
import pickle
import sqlite3
import time
import sys


def account_exists(account_id='jodel_account'):
    """Checks whether an account has already been created."""
    if Path('./' + account_id + '.pkl').is_file():
        return True
    else:
        return False


def create_new_account(account_id='jodel_account'):
    """Creates a new Jodel account.""" 
    lat, lng, city = 48.148434, 11.567867, "Munich"
    j = jodel_api.JodelAccount(lat=lat, lng=lng, city=city)
    j_account_data = j.get_account_data()

    pickle.dump(j_account_data, open(account_id + '.pkl', 'wb'))


def login(lat, lng, city, account_id='jodel_account', update_location=True):
    """"Login to Jodel based on a pickled account file."""
    j_account_data = pickle.load(open(account_id + '.pkl', 'rb'))

    return jodel_api.JodelAccount(lat=lat, lng=lng, city=city,
                                  access_token=j_account_data['access_token'],
                                  expiration_date=j_account_data['expiration_date'],
                                  refresh_token=j_account_data['refresh_token'],
                                  distinct_id=j_account_data['distinct_id'],
                                  device_uid=j_account_data['device_uid'],
                                  is_legacy=True, update_location=update_location)


def refresh_account(lat, lng, city, account_id='jodel_account'):
    """Refreshes (tokens) an old Jodel account."""
    j = login(lat=lat, lng=lng, city=city, account_id=account_id, update_location=False)
    j.refresh_access_token()
    j_account_data = j.get_account_data()
    pickle.dump(j_account_data, open(account_id + '.pkl', 'wb'))


def add_jodel(session, post):
    """Adds a Jodel to the database. If the Jodel aready exists, it'll be updated."""
    # Modify the post dictionary (espc. location)
    location = post['location']
    post['location_name'] = location['name']
    post['location_city'] = location['city']
    post['location_lat'] = location['loc_coordinates']['lat']
    post['location_lat'] = location['loc_coordinates']['lng']
    post['location_accuracy'] = location['loc_accuracy']
    post['location_country'] = location['country']
    post['children'] = ','.join(post['children'])
    post['added_to_db'] = time.time()
    post.pop('location', None)

    if session.query(exists().where(jodel_scraper_db.Jodel.post_id==post['post_id'])).scalar():
        oj = session.query(jodel_scraper_db.Jodel).filter_by(post_id=post['post_id']).first() 

        for key, value in post.items():
            setattr(oj, key, value)
    else:
        oj = jodel_scraper_db.Jodel(**post)
        session.add(oj)

    session.flush()
    oj_id = oj.id
    session.commit()

    return oj_id


def add_reply(session, post, parent_jodel_db_id):
    """Adds a reply to a Jodel to the database. If the reply aready exists, it'll be updated."""
    # Modify the post dictionary (espc. location)
    location = post['location']
    post['location_name'] = location['name']
    post['location_city'] = location['city']
    post['location_lat'] = location['loc_coordinates']['lat']
    post['location_lat'] = location['loc_coordinates']['lng']
    post['location_accuracy'] = location['loc_accuracy']
    post['location_country'] = location['country']

    logger.debug(f'Lat = {location["loc_coordinates"]["lat"]}, Lng = {location["loc_coordinates"]["lng"]}')

    try:
        post['children'] = ','.join(post['children'])
    except KeyError:
        post['children'] = None

    post['added_to_db'] = time.time()
    post['jodel_db_id'] = parent_jodel_db_id
    post.pop('location', None)

    if session.query(exists().where(jodel_scraper_db.Reply.post_id == post['post_id'])).scalar():
        reply = session.query(jodel_scraper_db.Reply).filter_by(post_id=post['post_id']).first() 

        for key, value in post.items():
            setattr(reply, key, value)
    else:
        reply = jodel_scraper_db.Reply(**post)
        session.add(reply)

    session.flush()
    reply_id = reply.id
    session.commit()

    return reply_id



if __name__ == "__main__":

    # Very Simple CLI
    try:
        if sys.argv[1] not in ['recent', 'popular', 'discussed']:
            print ('python jodel_scraper.py recent/popular/discussed')
            sys.exit()
        else:
            scrape_type = sys.argv[1]
    except IndexError:
        print ('python jodel_scraper.py recent/popular/discussed')
        sys.exit()


    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    engine = jodel_scraper_db.get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    if not account_exists():
        create_new_account()

    # 10 largest cities in Germany + Heidelberg, Mannheim, Nuremburg
    cities = [[48.148434, 11.567867, 'Munich'], 
              [52.514036, 13.395883, 'Berlin'], 
              [53.514826, 10.012963, 'Hamburg'],
              [50.945074, 6.965260, 'Cologne'],
              [50.113203, 8.648234, 'Frankfurt'],
              [48.790335, 9.196438, 'Stuttgart'],
              [51.240521, 6.832887, 'Dusseldorf'],
              [51.516348, 7.474380, 'Dortmund'],
              [51.448099, 7.017389, 'Essen'],
              [51.350277, 12.381273, 'Leipzig'],
              [49.402516, 8.686358, 'Heidelberg'],
              [49.488653, 8.472227, 'Mannheim'],
              [49.444046, 11.083596, 'Nuremburg']]


    for city in cities:
        # Loop trough the cities
        lat, lng, city = city

        logger.info(f'Scraping: {city}')

        try:
            j = login(lat=lat, lng=lng, city=city)
        except:
            # If the login fails, we need to refresh our access_token
            refresh_account(lat=lat, lng=lng, city=city)
            j = login(lat=lat, lng=lng, city=city)


        if scrape_type == 'recent':
            jodels = j.get_posts_recent(limit=100)[1]['posts']
        elif scrape_type == 'discussed':
            jodels = j.get_posts_discussed(limit=100)[1]['posts']
        elif scrape_type == 'popular':
            jodels = j.get_posts_popular(limit=100)[1]['posts']


        for jodel in jodels:
            more = True
            skip = 0
            replies_counter = 0

            logger.info(f'Added/Updated Jodel from {city}: {jodel["post_id"]} [{jodel["child_count"]} Children]')

            while more:
                # Replies; There seem to be some issues with the "skip" attribute not working properly
                details = j.get_post_details_v3(post_id=jodel['post_id'], skip=skip)
                try:
                    replies = details[1]['replies']
                    post = details[1]['details']

                    oj_db_id = add_jodel(session, post)

                    for reply in replies:
                        add_reply(session, reply, oj_db_id)
                        replies_counter += 1

                    # We need to paginate trough the results
                    logger.debug(f'Skip = {skip}, len(replies) = {len(replies)}')
                    if replies_counter >= jodel['child_count']:
                        more = False
                    else:
                        # see https://github.com/nborrmann/jodel_api/issues/54
                        try:
                            skip = details[1]['next']
                        except KeyError:
                            # We proably reached the limit
                            more = False
                except KeyError:
                    # There are no replies
                    more = False
                except TypeError:
                    # usually refers to details[1][...]
                    more = False

                logger.info(f'Added/Updated {len(replies)} replies to {jodel["post_id"]}')
