from base import Base, Mafia_Model_Mixin
from sqlalchemy import Column, String, Enum, ForeignKey, Integer

class Player(Base, Mafia_Model_Mixin):
    __tablename__ = 'player'

    player_id = Column('player_id', Integer, primary_key = True)
    user_id = Column('user_id', String(50), ForeignKey("user.user_id"), nullable = False, index = True)
    game_id = Column('game_id', Integer, ForeignKey("game.game_id"), nullable = False, index = True)
    role = Column('role', Enum('CITIZEN', 'MAFIA'), nullable = False, server_default = 'CITIZEN')
    status = Column('state', Enum('INVITED', 'ALIVE', 'DEAD'), nullable = False, server_default = 'INVITED')
    current_vote = Column('current_vote', Integer, ForeignKey("player.player_id"), nullable = True)

    def __init__(self, user_id, game_id, status = None):
        self.user_id = user_id
        self.game_id = game_id
        if status is not None:
            self.status = status

    def for_api(self, asking_player):
        all_columns = super(Player, self).for_api()
        if asking_player.player_id != all_columns['player_id'] and not(asking_player.role == 'MAFIA' and self.role == 'MAFIA'):
            all_columns.pop('role', None)
        game_state = self.game.game_state
        if game_state == 'DAWN' or game_state == 'NIGHT':
            if asking_player.role != 'MAFIA':
                all_columns.pop('current_vote')
        return all_columns
