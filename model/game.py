from base import Base, Mafia_Model_Mixin
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from model.db_session import DB_Session_Factory

game_state_enum = Enum('NOT_STARTED', 'NIGHT', 'DAWN', 'DAY', 'DUSK', 'MAFIA_WIN', 'CITIZENS_WIN')

class Game(Base, Mafia_Model_Mixin):
    __tablename__ = 'game'
    
    game_id = Column('game_id', Integer, primary_key = True)
    game_state = Column('game_state', game_state_enum, server_default = 'NOT_STARTED', index = True)
    leader_user_id = Column('leader_user_id', String(50), ForeignKey("user.user_id"), nullable = False)

    def __init__(self, leader_user_id):
        self.leader_user_id = leader_user_id
