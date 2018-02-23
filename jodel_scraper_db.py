from pathlib import Path
from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Boolean, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Jodel(Base):

    __tablename__ = 'jodels'

    id = Column(Integer, primary_key=True)
    added_to_db = Column(BigInteger)
    channel = Column(String)
    child_count = Column(Integer)
    children = Column(String)
    color = Column(String)
    created_at = Column(String)
    discovered_by = Column(Integer)
    distance = Column(Integer)
    from_home = Column(Boolean)
    got_thanks = Column(Boolean)
    image_approved = Column(Boolean)
    image_url = Column(String)
    location_accuracy = Column(Integer)
    location_city = Column(String)
    location_country = Column(String)
    location_lat = Column(Float)
    location_lng = Column(Float)
    location_name = Column(String)
    message = Column(String)
    notifications_enabled = Column(Boolean)
    oj_replied = Column(Boolean)
    pin_count = Column(Integer)
    post_id = Column(String)
    post_own = Column(String)
    replier = Column(Integer)
    share_count = Column(Integer)
    thumbnail_url = Column(String)
    updated_at = Column(String)
    user_handle = Column(String)
    view_count = Column(Integer)
    vote_count = Column(Integer)

    def __repr__(self):
        return self.post_id


class Reply(Base):

    __tablename__ = 'replies'

    id = Column(Integer, primary_key=True)
    added_to_db = Column(BigInteger)
    channel = Column(String)
    child_count = Column(Integer)
    children = Column(String)
    color = Column(String)
    created_at = Column(String)
    discovered_by = Column(Integer)
    distance = Column(Integer)
    from_home = Column(Boolean)
    got_thanks = Column(Boolean)
    image_approved = Column(Boolean)
    image_url = Column(String)
    jodel_db_id = Column(Integer, ForeignKey('jodels.id'))
    location_accuracy = Column(Integer)
    location_city = Column(String)
    location_country = Column(String)
    location_lat = Column(Float)
    location_lng = Column(Float)
    location_name = Column(String)
    message = Column(String)
    notifications_enabled = Column(Boolean)
    oj_replied = Column(Boolean)
    parent_id = Column(String)
    pin_count = Column(Integer)
    post_id = Column(String)
    post_own = Column(String)
    replier = Column(Integer)
    reply_timestamp = Column(Integer)
    thumbnail_url = Column(String)
    updated_at = Column(String)
    user_handle = Column(String)
    vote_count = Column(Integer)

    def __repr__(self):
        return self.post_id


def get_engine():
    """Creates and populates a new SQLite database and returns the engine."""
    if not Path('jodel_scraper.db').is_file():
        engine = create_engine('sqlite:///jodel_scraper.db', echo=False)
        Base.metadata.create_all(engine)
    else:
        engine = create_engine('sqlite:///jodel_scraper.db', echo=False)

    return engine
