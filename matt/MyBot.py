# keep these three import statements
import game_API
import fileinput
import json


# your import statements here
import random

first_line = True  # DO NOT REMOVE

# global variables or other functions can go here
stances = ["Rock", "Paper", "Scissors"]


class MattBot:
    def __init__(self):
        self.priority = -1

    def duel_mode(self):
        return game.get_self().location, self.duel_stance()

    def duel_stance(self):
        return get_winning_stance(game.get_opponent().stance)

    # Basic Strategy - shipped with code
    def default_strategy(self, game):
        me = game.get_self()
        # TODO
        if me.location == me.destination:  # check if we have moved this turn
            # get all living monsters closest to me
            monsters = game.nearest_monsters(me.location, 1)

            # choose a monster to move to at random
            monster_to_move_to = monsters[random.randint(0, len(monsters) - 1)]

            # get the set of shortest paths to that monster
            paths = game.shortest_paths(me.location, monster_to_move_to.location)
            destination_node = paths[random.randint(0, len(paths) - 1)][0]
        else:
            destination_node = me.destination

        # if game.has_monster(me.location):
        #     # if there's a monster at my location, choose the stance that damages that monster
        #     chosen_stance = get_winning_stance(game.get_monster(me.location).stance)
        # else:
        #     # otherwise, pick a random stance
        #     chosen_stance = stances[random.randint(0, 2)]

        return destination_node

    def mid_game_priority(self, game):
        return 0

    def early_game_priority(self, game):
        game.log("IN SET PRIO")
        # Speed guy @3
        if game.get_self().health < 50:
            return 3

        if game.get_self().speed >=1:
            return self.mid_game_priority(game)

        if not game.get_monster(3).dead:  # 3 is available - go to it.
            return 3

        # HP - TODO better way
        if not game.get_monster(0).dead:
            return 0

        if not game.get_monster(1).dead:
            return 1

        # yolo
        closest_monster = game.nearest_monsters(game.get_self().location, 1)[0]
        game.log(f"Going to: {closest_monster.location}")
        return closest_monster

    # Dont want to move if in combat.
    def in_combat(self, game):
        current_location = game.get_self().location
        if not game.get_monster(current_location).dead:
            game.log(f"Still fighting")
            return True
        return False

    # Speed -> Health -> ?
    def speed_strategy(self, game):
        current_location = game.get_self().location

        # No priority set
        if self.priority == -1:
            self.priority = self.early_game_priority(game)

        # Go to priority
        #    if in combat do nothing - finish the fight
        # if self.in_combat(game):
        #     return current_location

        # if mission accomplished reset
        if current_location == self.priority:
            if game.has_monster(current_location):
                if game.get_monster(current_location).dead:
                    # FUCK IT
                    closest_monster = game.nearest_monsters(current_location, 1)[0]
                    self.priority = closest_monster.location


        # do the thing
        path = game.shortest_paths(current_location, self.priority)
        return path[0][0]

    def turn(self, game):

        if game.turn_number > 299:
            game.log("Its time to d-d-d-d-d-d-d-d-d-duel")
            return self.duel_mode()

        # destination = self.default_strategy(game)

        # have to rerun this a lot without recursion - laziest way
        destination = self.speed_strategy(game)

        # while destination == -1:
        destination = self.speed_strategy(game)

        game.log(f"@@@@@@@@@@@@ {destination}")
        # stance of monster in location
        if game.has_monster(game.get_self().location):
            stance = get_winning_stance(game.get_monster(game.get_self().location).stance)
        else:
            stance = get_winning_stance(game.get_opponent().stance)

        return destination, stance


def get_winning_stance(stance):
    if stance == "Rock":
        return "Paper"
    elif stance == "Paper":
        return "Scissors"
    elif stance == "Scissors":
        return "Rock"


def enhanced_logging(player):
    game.log(f"Rock: {player.rock} Paper: {player.paper} Scissors: {player.scissors}")
    game.log(f"SPEED: {player.speed})")
    game.log(f" HP: {player.health} \n STANCE: ***{player.stance}***")
    game.log(f"move in: {player.movement_counter} TO {player.destination}")
    game.log(f"@{player.location}")


matt_bot = MattBot()

# main player script logic
# DO NOT CHANGE BELOW ----------------------------
for line in fileinput.input():
    if first_line:
        game = game_API.Game(json.loads(line))
        first_line = False
        continue
    game.update(json.loads(line))
# DO NOT CHANGE ABOVE ---------------------------

    # code in this block will be executed each turn of the game

    me = game.get_self()
    game.log(f"HP: {me.health}")
    # game.log(20*"-")
    # enhanced_logging(me)

    destination_node, chosen_stance = matt_bot.turn(game)

    game.log(f"{game.turn_number}: {destination_node}, {chosen_stance}")
    game.submit_decision(destination_node, chosen_stance)

