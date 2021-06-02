from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date, DateTime, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('sqlite:///telegrambot.db') # , connect_args={'check_same_thread': False}


engine = create_engine('sqlite:///telegrambot.db')
Base = declarative_base()
class Users(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_dates_name = Column(String)
    user_dates_date = Column(String)
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
    def __repr__(self):
        template = f"{self.user_id}, {self.user_dates_name}, "\
                   f"{self.user_dates_date}, {self.notification_time}, "\
                   f"{self.before_day_value}, {self.language}"
        return template



Base.metadata.create_all(engine)
users_table = Users.__table__
metadata = Base.metadata

def insert_into(kwargs):
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    # TODO: сделать запись и соответственно поиск по user id, подставив под него chat id
    #  заранее проверив и его уникальность для всех пользователей, и изменчивость при перезапуске в боте
    user_id = kwargs['user_id']
    if is_query_username_bd(user_id):
        exist_user = str(session.query(Users).filter_by(user_id='{}'.format(user_id)).first()).split(',')
        overwrite_exist_data(exist_user, kwargs)

    else:
        print(f"ПОЛЬЗОВАТЕЛЯ НЕТ В БАЗЕ ДАННЫХ.\nПОЛЬЗОВЕТЕЛЬ {user_id} ДОБАВЛЕН В БАЗУ ДАННЫХ")
        ins = Users(**kwargs)
        session.add(ins)
        session.commit()



def is_query_username_bd(user_id, first_time=False):
    select = f"SELECT user_id FROM users WHERE user_id='{user_id}'"
    conn = engine.connect()
    result = conn.execute(select)
    return result.fetchall()




def overwrite_exist_data(exist_data, new_data):
    print("ОБНОВЛЕНИЕ СТАРЫХ ЗНАЧЕНИЙ\n")
    conn = engine.connect()
    user_id = exist_data[0]
    for (key,new_v),exist_v in zip(new_data.items(), exist_data):
        if str(new_v).strip() != str(exist_v).strip():
            update = f"UPDATE users SET {key}='{new_v}' WHERE user_id='{user_id}'"
            conn.execute(update)
            print(f'ЗНАЧЕНИЕ {exist_v} ПЕРЕЗАПИСАНО НА {new_v} С USER_NAME {user_id}')


def get_user_data(user_id):
    select = f"SELECT * FROM users WHERE user_id='{user_id}'"
    conn = engine.connect()
    result = conn.execute(select)
    results = result.fetchall()[0]
    if results:
        return results













kwargs = {'user_name': 'ValiaBlack', 'chat_id': 1490014759,
          'user_dates_name': 'Новый Год', 'user_dates_date': '01 01',
          'notification_time': '10', 'before_day_value': 1, 'language': 'Inglish'}


# insert_into(kwargs)
# is_query_username_bd(kwargs)

