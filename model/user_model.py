from base import Base, Mafia_Model_Mixin
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, String
from model.db_session import DB_Session_Factory
from model.player import Player

class User(Base, Mafia_Model_Mixin):
    __tablename__ = 'user'

    user_id = Column('user_id', String(50), nullable = False, primary_key = True)
    first_name = Column('first_name', String(100), nullable = True)
    last_name = Column('last_name', String(100), nullable = True)
    access_token = Column('access_token', String(300), nullable = True, unique = True)

    def __init__(self, user_id, access_token, first_name, last_name):
        self.user_id = user_id
        self.access_token = access_token
        self.first_name = first_name
        self.last_name = last_name

    def is_authorized_to_access_game(self, game_id):
        db_session = DB_Session_Factory.get_db_session()
        player = db_session.query(Player).filter(Player.game_id == game_id, Player.user_id == self.user_id).first()
        ret_value = True
        if player is None:
            ret_value = False
        return ret_value

    @staticmethod
    def get_access_token(fb_access_token):
        return fb_access_token

    @staticmethod
    def get_by_fb_access_token(fb_access_token):
        db_session = DB_Session_Factory.get_db_session()
        return db_session.query(User).filter(User.access_token == User.get_access_token(fb_access_token)).first()
