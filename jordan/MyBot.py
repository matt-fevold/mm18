# keep these three import statements
import game_API
import fileinput
import json

# your import statements here
import random

first_line = True # DO NOT REMOVE

# global variables or other functions can go here
stances = ["Rock", "Paper", "Scissors"]

def get_winning_stance(stance):
    if stance == "Rock":
        return "Paper"
    elif stance == "Paper":
        return "Scissors"
    elif stance == "Scissors":
        return "Rock"

class Logic:
    def __init__(self):
        self.game = None

        self.flight_plan = None


    def follow(self):
        me = self.game.get_self()
        them = self.game.get_opponent()

        self.log(f"Me - Dest: {me.destination} Stance: {me.stance} Flight Plan: {self.flight_plan}")
        self.log(f"Them - Dest: {them.destination} Stance: {them.stance}")

        if self.flight_plan == None:
            # If first turn
            self.log(f"Reset Flight Plan")
            self.flight_plan = [ 0 ]
            me.destination = 0
        else:
            self.log(f"Flight Plan: {self.flight_plan}")
            if len(self.flight_plan) == 0:
                self.flight_plan = None
                self.move()

            elif len(self.flight_plan) == 1:
                if self.flight_plan[0] == me.location:
                    # we are at the goal, move again
                    self.flight_plan = None
                    self.move()
                if self.flight_plan[0] != me.location:
                    # not there yet keep going
                    me.destination = self.flight_plan[0]

            elif len(self.flight_plan) > 1:
                if self.flight_plan[0] == me.location:
                    self.flight_plan.pop(0)
                    me.destination = self.flight_plan[0]


        return me.destination, self.choose_stance()

    def move(self):
        self.log("Moving...")
        me = self.game.get_self()
        them = self.game.get_opponent()

        self.calculate_move()

    def choose_stance(self):
        them = self.game.get_opponent()
        return stances[random.choice(list(set([0, 1, 2]).difference(set([them.stance]))))]

    def log(self, msg):
        self.game.log(msg)

    def calculate_move(self):
        self.log("Decing new move target")
        me = self.game.get_self()
        them = self.game.get_opponent()

        # get monsters
        try:
            monsters = [ self.game.get_monster(i) for i in range(24) ]
        except:
            monsters = []

        # get live monsters
        live_monsters = [ m for m in monsters if not m.dead ]

        # decide on stat to improve
        # TODO

        # calculate path to



    def turn(self, game):

        self.game = game

        dest, stance = self.follow()
        #dest, stance = self.default(game)
        #game.log(f"Destination: {dest} Stance: {['rock','paper','scissors'][stance]}")
        game.log(f"Destination: {dest} Stance: {stance}")

        return dest, stance

    def default(self, game):
        me = game.get_self()

        if me.location == me.destination: # check if we have moved this turn
            # get all living monsters closest to me
            monsters = game.nearest_monsters(me.location, 1)

            # choose a monster to move to at random
            monster_to_move_to = monsters[random.randint(0, len(monsters)-1)]

            # get the set of shortest paths to that monster
            paths = game.shortest_paths(me.location, monster_to_move_to.location)
            destination_node = paths[random.randint(0, len(paths)-1)][0]
        else:
            destination_node = me.destination

        if game.has_monster(me.location):
            # if there's a monster at my location, choose the stance that damages that monster
            chosen_stance = get_winning_stance(game.get_monster(me.location).stance)
        else:
            # otherwise, pick a random stance
            chosen_stance = stances[random.randint(0, 2)]

        return destination_node, chosen_stance

logic = Logic()

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

    dest, stance = logic.turn(game)

    # submit your decision for the turn (This function should be called exactly once per turn)
    game.submit_decision(dest, stance)
    game.log("-"*30)

