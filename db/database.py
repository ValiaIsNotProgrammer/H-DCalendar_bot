from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from loggs import log_app

logger = log_app.get_logger(__name__)

engine = create_engine('sqlite:///telegrambot.db')
conn = engine.connect()
Base = declarative_base()
class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_dates_date = Column(String)
    user_dates_name = Column(String)
    notification_time = Column(String)
    before_day_value = Column(Integer)
    language = Column(String)

    def __init__(self, user_id, user_dates_name,
                 user_dates_date, notification_time,
                 before_day_value, language):
            self.user_id = user_id
            self.user_dates_name = user_dates_name
            self.user_dates_date = user_dates_date
            self.notification_time = notification_time
            self.before_day_value = before_day_value
            self.language = language
            self.members = []

    def get_params(self):
        return [self.user_id, self.user_dates_date, self.user_dates_name, self.notification_time,
                self.before_day_value, self.language]




Base.metadata.create_all(engine)
users_table = Users.__table__
metadata = Base.metadata

def insert_into(kwargs):
    kwargs = {k: ", ".join(v) if type(v) == list else v for k, v in kwargs.items()}
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    user_id = kwargs['user_id']
    if is_query_username_bd(user_id):
        old_data = session.query(Users).filter(Users.user_id == user_id).first()
        overwrite_exist_data(new_data=kwargs, old_data=old_data.get_params())

    else:
        logger.info("The user was added to the database")
        ins = Users(**kwargs)
        session.add(ins)
        session.commit()


def is_query_username_bd(user_id):
    select = f"SELECT user_id FROM users WHERE user_id='{user_id}'"
    conn = engine.connect()
    result = conn.execute(select)
    logger.info(f"SUCCESS: The user {user_id} got his data back")
    return result.fetchall()


def overwrite_exist_data(new_data: dict, old_data: list):
    conn = engine.connect()
    user_id = new_data['user_id']
    for (column, new_value), old_value  in zip(new_data.items(), old_data):
        if new_value != old_value:
            update = f'UPDATE users SET {column}="{new_value}" WHERE user_id="{user_id}"'
            logger.info(f"SUCCESS: The value of {column.upper()} -> "
                        f"{'<'+old_value+'>'} change to {'<'+new_value+'>'}")
            conn.execute(update)


def get_user_data(user_id):
    select = f"SELECT * FROM users WHERE user_id='{user_id}'"
    conn = engine.connect()
    result = conn.execute(select)
    results = result.fetchall()[0]
    logger.debug(f"User {user_id} received their data: {results}")
    if results:
        return results

