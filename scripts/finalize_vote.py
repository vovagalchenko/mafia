from getopt import getopt, GetoptError
from sys import stderr, argv, exit
from lib.time_utils import timestamp_to_dt
from model.game import Game_Event, Game
from model.player import Player
from model.user_model import User
from model.db_session import DB_Session_Factory
import operator

def exit_with_msg(msg):
    print >> stderr, msg
    exit(2)

def main(argv):
    try:
        opts, args = getopt(argv, "d:g:")
    except GetoptError:
        exit_with_msg("You can only provide -d and -g options")
    game_id = None
    last_vote_time = None
    for (opt_name, opt_value) in opts:
        if opt_name == '-g':
            game_id = int(opt_value)
        elif opt_name == '-d':
            last_vote_time = timestamp_to_dt(opt_value)
    if game_id is None:
        exit_with_msg("Must provide game_id using -g")
    if last_vote_time is None:
        exit_with_msg("Must provide last vote time using -d")
    print "Game id: " + str(game_id)
    print "Last vote time: " + str(last_vote_time)
    db_session = DB_Session_Factory.get_db_session()
    game = db_session.query(Game).get(game_id)
    if game is None:
        exit_with_msg("Invalid game id")

    voting_player_conditions = [Player.game_id == game_id]
    if game.game_state == 'DUSK':
        voting_player_conditions.append(Player.role != 'GHOST')
    elif game.game_state == 'DAWN':
        voting_player_conditions.append(Player.role == 'MAFIA')
    else:
        exit_with_msg("There is no vote to finalize.")

    last_vote = db_session.query(Game_Event).filter(Game_Event.game_id == game_id, Game_Event.vote != None).order_by(Game_Event.created.desc()).first()
    if last_vote.created > last_vote_time:
        print "There has been a vote since. Nothing to do."
        exit(0)

    voting_players = db_session.query(Player).filter(*voting_player_conditions).all()
    votes = {}
    for player in voting_players:
        if player.current_vote is None:
            exit_with_msg("INCONSISTENCY: Player %d didn't vote!" % (player.player_id))
        vote = player.current_vote
        if votes.get(vote, None) is None:
            votes[vote] = 1
        else:
            votes[vote] = votes[vote] + 1
    sorted_votes = sorted(votes.iteritems(), key = operator.itemgetter(1), reverse = True)
    killed_player_id = sorted_votes[0][0]
    killed_player = db_session.query(Player).get(killed_player_id)
    print "Killed: <%d>" % (killed_player_id)
    
    num_mafia = 0
    num_non_mafia = 0
    all_players = db_session.query(Player).filter(Player.game_id == game_id).all()
    for player in all_players:
        player.current_vote = None
        if player.player_id == killed_player_id:
            player.role = 'GHOST'
        elif player.role == 'MAFIA':
            num_mafia += 1
        elif player.role != 'GHOST':
            num_non_mafia += 1
        db_session.add(player)
    game_event_msg = ""
    killed_user = db_session.query(User).get(killed_player.user_id)
    killed_user_name = killed_user.first_name + " " + killed_user.last_name
    if game.game_state == 'DUSK':
        game_event_msg = "Tonight citizens lynched " + killed_user_name + "."
    elif game.game_state == 'DAWN':
        game_event_msg = killed_user_name + " was found dead after what appears to have been a mafia hit."
    db_session.add(Game_Event(game_id, game.game_state, None, game_event_msg, None, None))

    new_game_state = None
    if num_mafia == 0:
        new_game_state = 'CITIZENS_WIN'
    elif num_mafia > num_non_mafia or (num_mafia == 1 and num_non_mafia == 1):
        new_game_state = 'MAFIA_WIN'
    elif game.game_state == 'DUSK':
        new_game_state = 'NIGHT'
    elif game.game_state == 'DAWN':
        new_game_state = 'DAY'
    game.game_state = new_game_state
    db_session.add(game)
    db_session.commit()


if __name__ == "__main__":
    main(argv[1:])
