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

class Pathing:
    LEAST_MONSTERS = 0
    MOST_MONSTERS = 1

class KillMode:
    KILL_ALL = 0
    KILL_TARGET = 1


class Logic:
    def __init__(self):
        self.game = None

        self.flight_plan = None

        self.monster_filter = None
        self.pathing_method = Pathing.LEAST_MONSTERS

        self.phase = 0
        self.phase_0_queue = [ 3, 1, 0,  21 , 20, 13, 12, 0 ]
        self.kill_mode = KillMode.KILL_TARGET


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
                self.move()

            elif len(self.flight_plan) == 1:
                if self.flight_plan[0] == me.location:

                    move = True

                    if self.kill_mode == KillMode.KILL_TARGET:
                        # if kill_mode is kill target
                        if self.game.has_monster(me.location):
                            m = self.game.get_monster(me.location)
                        else:
                            m = None

                        move = ( m is None or (m is not None and m.dead))

                    if move:
                        # we are at the goal, move again
                        self.move()
                        if self.flight_plan != None:
                            me.destination = self.flight_plan[0]

                elif self.flight_plan[0] != me.location:
                    # not there yet keep going, unless we are in kill all mode

                    if self.kill_mode == KillMode.KILL_ALL and self.game.has_monster(me.location) and not self.game.get_monster(me.location).dead:
                        me.location = me.destination

                    else:
                        me.destination = self.flight_plan[0]



            elif len(self.flight_plan) > 1:
                if self.flight_plan[0] == me.location:
                    self.flight_plan.pop(0)
                    me.destination = self.flight_plan[0]


        a = self.choose_stance()
        self.log(a)

        return me.destination, a

    def move(self):
        self.log("Moving...")
        me = self.game.get_self()
        them = self.game.get_opponent()

        self.calculate_move()

    def choose_stance(self):
        me = self.game.get_self()
        them = self.game.get_opponent()

        try:
            local_m = self.game.get_monster(me.location)
        except:
            local_m = None

        # if we are about to move, change stance to monster at location
        if me.speed == me.movement_counter-1 and me.location != me.destination:
            if self.game.has_monster(me.destination) and not self.game.get_monster(me.destination).dead:
                self.log("Attack, monster at future location")
                m = self.game.get_monster(me.destination)
                return get_winning_stance(m.stance)
            else:
                # no monster at future location,
                # set to winning hand against opponent
                self.log(f"Opponent in stance {them.stance}")
                if them.stance in stances:
                    return get_winning_stance(them.stance)
                return random.choice(stances)

        elif local_m is not None and not local_m.dead:
            return get_winning_stance(local_m.stance)

        elif them.stance in stances:
            return get_winning_stance(them.stance)

        return random.choice(stances)


    def log(self, msg):
        self.game.log(str(msg))

    def calculate_move(self):
        self.log("Decing new move target")
        me = self.game.get_self()
        them = self.game.get_opponent()

        health_mon = self.game.get_monster(0)

        self.log(f"Respawn f{health_mon.respawn_counter}")
        if me.location == 0 and (not health_mon.dead or (health_mon.dead and health_mon.respawn_counter < (10-me.speed))):
            # don't leave if health alive
            me.destination = me.location
            return


        # loop through targets to move to
        if self.phase == 0:
            if len(self.phase_0_queue) > 0:
                target_node = self.phase_0_queue.pop(0)

                if len(self.phase_0_queue) == 0:
                    self.phase += 1
        else:
            self.kill_mode = KillMode.KILL_ALL
            health_m = self.game.get_monster(0)
            if not health_m.dead:
                target_node = health_m.location
            else:

                # try to find nodes near me and the health that are alive
                near_me = self.game.nearest_monsters(me.location, 1)
                near_health = self.game.nearest_monsters(0, 1)

                overlap = set(near_me).intersection(set(near_health))

                if len(overlap) > 0:
                    # try to move to monster with lowest health near me and health
                    lowest_health = sorted(overlap, key=lambda m:m.health)[0]
                    target_node = lowest_health.location
                elif len(near_health) > 0:
                    # move towards monster around health
                    lowest_health = sorted(near_health, key=lambda m:m.health)[0]
                    target_node = lowest_health.location
                else:
                    valid = []
                    for n in [14, 9,8, 7]:
                        if self.game.has_monster(n):
                            m = self.game.get_monster(n)
                            if not m.dead:
                                valid.append(m)

                    if len(valid) != 0:
                        target_node = random.choice(valid).location
                    else:
                        # use secondary valid
                        valid = []
                        for n in [17, 15, 13]:
                            if self.game.has_monster(n):
                                m = self.game.get_monster(n)
                                if not m.dead:
                                    valid.append(m)
                        if len(valid) != 0:
                            target_node = random.choice(valid).location
                        else:
                            target_node = 0


        # calculate path to
        self.log(f"Calculating path to {target_node}")
        shortest_paths = self.game.shortest_paths(me.location, target_node)

        # pick path to use
        if self.pathing_method == Pathing.LEAST_MONSTERS:
            self._pick_least_monsters(shortest_paths)
        elif self.pathing_method == Pathing.MOST_MONSTERS:
            self._pick_most_monsters(shortest_paths)

        self.monster_filter = None



    def _pick_least_monsters(self, paths):
        best = paths[0]
        best_count = 100
        least_health = 0

        if not self.monster_filter:
            monster_filter = lambda x:True
        else:
            monter_filter = self.monster_filter


        if len(paths) > 0:
            for path in paths:
                this_mon_count = 0
                mon_health = 0
                for node in path:
                    if self.game.has_monster(node):
                        m = self.game.get_monster(node)
                        if monster_filter(m) and not m.dead:
                            this_mon_count += 1
                            mon_health += m.health



                if (this_mon_count < best_count) or (this_mon_count == best_count and mon_health < least_health):
                    best = path
                    best_count = this_mon_count
                    least_health = mon_health


        self.flight_plan = best


    def _pick_most_monsters(self, paths):
        best = paths[0]
        best_count = -1

        if not self.monster_filter:
            monster_filter = lambda x:True
        else:
            monter_filter = self.monster_filter

        if len(paths) > 0:
            for path in paths:
                this_mon_count = 0
                for node in path:
                    if self.game.has_monster(node):
                        m = self.game.get_monster(node)
                        if monster_filter(m):
                            this_mon_count += 1


                if this_mon_count > best_count:
                    best = path
                    best_count = this_mon_count

        self.flight_plan = best






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

