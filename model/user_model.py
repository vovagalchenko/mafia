from base import Base, Mafia_Model_Mixin
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, backref
from model.db_session import DB_Session_Factory
from model.player import Player
from model.game import Game

class User(Base, Mafia_Model_Mixin):
    __tablename__ = 'user'

    user_id = Column('user_id', String(50), nullable = False, primary_key = True)
    first_name = Column('first_name', String(100), nullable = True)
    last_name = Column('last_name', String(100), nullable = True)
    access_token = Column('access_token', String(300), nullable = True, unique = True)
    players = relationship("Player", backref = "user")


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

    def for_api(self, authenticated_user):
        user_dict = {
            'user_id' : self.user_id,
            'first_name' : self.first_name,
            'last_name' : self.last_name,
        }
        db_session = DB_Session_Factory.get_db_session()
        my_identities_in_games = db_session.query(Player).filter(Player.user_id == self.user_id).all()
        games_dict = {
            'num_games' : len(my_identities_in_games),
        }
        if self.user_id == authenticated_user.user_id:
            games = []
            for player in my_identities_in_games:
                games.append(player.game.for_api(player))
            games_dict['games_list'] = games
        user_dict['games'] = games_dict
        return user_dict

    @staticmethod
    def get_access_token(fb_access_token):
        return fb_access_token

    @staticmethod
    def get_by_fb_access_token(fb_access_token):
        db_session = DB_Session_Factory.get_db_session()
        return db_session.query(User).filter(User.access_token == User.get_access_token(fb_access_token)).first()
