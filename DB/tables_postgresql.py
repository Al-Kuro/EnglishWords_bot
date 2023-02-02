from sqlalchemy import Column, Integer, Float, BigInteger, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from utils import a1, a2, b1, b2, c

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    id_telegram = Column(BigInteger)
    user_name = Column(String)
    is_premium = Column(Boolean, default=False)
    user_state = Column(Integer, default=0)
    is_resubscribe = Column(Boolean, default=False)
    join_date = Column(DateTime, default=datetime.utcnow())
    words_count_learn = Column(Integer, default=0)
    level_english_user = Column(String, default='')
    is_table_rating = Column(Boolean, default=False)
    score_table_rating = Column(Float, default=0.0)
    today_words_str = Column(String, default=datetime.now().strftime("%Y-%m-%d"))
    today_words_str_state = Column(Integer, default=0)
    current_words_to_learn = Column(JSON, default={})
    current_words_to_learn_check = Column(JSON, default={})
    current_4lst_check = Column(JSON, default={'current_4lst_check': [], 'current_word': []})
    start_msg = Column(BigInteger)
    A1_words = Column(JSON, default=a1)
    A2_words = Column(JSON, default=a2)
    B1_words = Column(JSON, default=b1)
    B2_words = Column(JSON, default=b2)
    C_words = Column(JSON, default=c)

    def __init__(self, user_name, id_telegram):
        self.id_telegram = id_telegram
        self.user_name = user_name

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.user_name, self.id_telegram)
