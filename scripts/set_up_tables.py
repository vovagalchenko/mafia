import sys, os
from time import sleep

sys.path.append(os.path.dirname(__file__) + "/../")

from model.db_session import DB_Session_Factory
from model.user_model import User
from model.game import Game
from model.player import Player
from model.game_event import Game_Event
from sqlalchemy.schema import CreateTable

db_session = DB_Session_Factory.get_db_session()
db_session.execute(CreateTable(User.__table__))
db_session.execute(CreateTable(Game.__table__))
db_session.execute(CreateTable(Player.__table__))
db_session.execute(CreateTable(Game_Event.__table__))
