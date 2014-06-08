from base import Base, Mafia_Model_Mixin
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, String, Integer, Enum, ForeignKey, not_, and_
from sqlalchemy.orm import relationship, backref
from model.db_session import DB_Session_Factory
from model.player import Player
import calendar

game_state_enum = Enum('NOT_STARTED', 'NIGHT', 'DAWN', 'DAY', 'DUSK', 'MAFIA_WIN', 'CITIZENS_WIN')

class Game(Base, Mafia_Model_Mixin):
    __tablename__ = 'game'
    
    game_id = Column('game_id', Integer, primary_key = True)
    game_state = Column('game_state', game_state_enum, server_default = 'NOT_STARTED', index = True)
    leader_user_id = Column('leader_user_id', String(50), ForeignKey("user.user_id"), nullable = False)
    players = relationship("Player", backref = "game", lazy="dynamic")

    def __init__(self, leader_user_id):
        self.leader_user_id = leader_user_id

    def for_api(self, asking_player, min_time = None):
        all_columns = super(Game, self).for_api()
        db_session = DB_Session_Factory.get_db_session()
        all_columns['players'] = []
        mafia_player_ids = []
        for player in self.players.all():
            all_columns['players'].append(player.for_api(asking_player))
            if (player.role == 'MAFIA'):
                mafia_player_ids.append(player.player_id)
        num_events_limit = 20
        conditions = [Game_Event.game_id == self.game_id]
        if asking_player.role != 'MAFIA' and len(mafia_player_ids) > 0:
            conditions.append(not_(and_(Game_Event.game_state == 'NIGHT', Game_Event.from_player_id.in_(mafia_player_ids))))
        if min_time is not None:
            conditions.append(Game_Event.created > min_time)
        game_events = map(lambda game_event: game_event.for_api(), db_session.query(Game_Event).filter(*conditions).order_by(Game_Event.created.asc()).limit(num_events_limit).all())
        all_columns['game_events'] = {
            'limit' : num_events_limit,
            'min_time' : min_time,
            'events' : game_events
        }
        return all_columns

class Game_Event(Base, Mafia_Model_Mixin):
    __tablename__ = 'game_event'

    game_event_id = Column('game_event_id', Integer, primary_key = True)
    from_player_id = Column('from_player_id', Integer, ForeignKey("player.player_id"), nullable = True, index = True, server_default = None) 
    to_player_id = Column('to_player_id', Integer, ForeignKey("player.player_id"), nullable = True, index = True, server_default = None)
    game_id = Column('game_id', Integer, ForeignKey("game.game_id"), nullable = False, index = True)
    game_state = Column('game_state', game_state_enum, nullable = False)
    vote = Column('vote', Integer, ForeignKey("player.player_id"), nullable = True, index = True, server_default = None)
    comment = Column('comment', mysql.LONGBLOB, nullable = True, server_default = None)

    def __init__(self, game_id, game_state, vote, comment, from_player_id = None, to_player_id = None):
        self.game_id = game_id
        self.game_state = game_state
        self.vote = vote
        self.comment = comment 
        self.from_player_id = from_player_id
        self.to_player_id = to_player_id
