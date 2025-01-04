"""CS 61A presents Ants Vs. SomeBees."""

import random
from ucb import main, interact, trace
from collections import OrderedDict

################
# Core Classes #
################


class Place:
    """A Place holds insects and has an exit to another Place."""
    is_hive = False

    def __init__(self, name, exit=None):
        """Create a Place with the given NAME and EXIT.

        name -- A string; the name of this Place.
        exit -- The Place reached by exiting this Place (may be None).
        """
        self.name = name
        self.exit = exit
        self.bees = []        # A list of Bees
        self.ant = None       # An Ant
        self.entrance = None  # A Place
        # Phase 1: Add an entrance to the exit
        # BEGIN Problem 2
        "*** YOUR CODE HERE ***"
        # exit | place | entrance
        # needs to keep track of only 1 entrance a.k.a the most recently constructed exit

        # when entrance is constructed p.entrance is set to a non-None value
        # when place is constructed p.exit is set to a non-None value
        
        # if place1.exit != None
        if self.exit != None:
            # place0.entrance = place1
            exit.entrance = self
        # END Problem 2


    def add_insect(self, insect):
        """Asks the insect to add itself to this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect):
        """Asks the insect to remove itself from this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.remove_from(self)

    def __str__(self):
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has health and a Place."""

    next_id = 0  # Every insect gets a unique id number
    damage = 0
    # ADD CLASS ATTRIBUTES HERE
    is_waterproof = False

    def __init__(self, health, place=None):
        """Create an Insect with a health amount and a starting PLACE."""
        self.health = health
        self.place = place

        # assign a unique ID to every insect
        self.id = Insect.next_id
        Insect.next_id += 1

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and remove the insect from its place if it
        has no health remaining.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_health(2)
        >>> test_insect.health
        3
        """
        self.health -= amount
        if self.health <= 0:
            self.zero_health_callback()
            self.place.remove_insect(self)


    def action(self, gamestate):
        """The action performed each turn."""

    def zero_health_callback(self):
        """Called when health reaches 0 or below."""

    def add_to(self, place):
        self.place = place

    def remove_from(self, place):
        self.place = None

    def __repr__(self):
        cname = type(self).__name__
        return '{0}({1}, {2})'.format(cname, self.health, self.place)


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    implemented = False  # Only implemented Ant classes should be instantiated
    food_cost = 0
    is_container = False
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, health=1): 
        super().__init__(health)
        self.double_damage_multiplier_bool = False
        self.has_been_doubled = False


    def double(self):
        """Double this ants's damage, if it has not already been doubled."""
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        if self.double_damage_multiplier_bool == True and self.has_been_doubled == False:
            self.damage = 2 * self.damage
            self.has_been_doubled = True
            return self.damage
        # END Problem 12

    def can_contain(self, other):
        return False

    def store_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def remove_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def add_to(self, place):
        if place.ant is None:
            place.ant = self
        else:
            # BEGIN Problem 8b
            #print("DEBUG:", "--beginning -- place.ant--", place.ant)
            #print("DEBUG:", "--beginning -- self--", self)
            if place.ant.is_container: # check if og ant is a container ant
                if place.ant.can_contain(self): # check if og ant can contain new ant
                    place.ant.store_ant(self) # store new ant
                    place.ant.place = place # update the place's ant attribute to refer to the container ant
                    #print("DEBUG:", "place.ant.place=", place.ant.place)
                else: # else if og ant is full give error
                    assert place.ant is None, 'Too many ants in {0}'.format(place)
            elif self.is_container: # check if new ant is a container ant
                if self.can_contain(place.ant): # check if new ant is full
                    # if ant being added can contain original ant, swap roles
                    #print("DEBUG:", "--b4 swap -- place.ant--", place.ant)
                    #print("DEBUG:", "--b4 swap -- self--", self)
                    place.ant, self = self, place.ant # swap roles
                    #print("DEBUG:", "--after swap -- place.ant--", place.ant)
                    #print("DEBUG:", "--after swap -- self--", self)
                    place.ant.store_ant(self) # repeat
                    place.ant.place = place # update the place's ant attribute to refer to the container ant
                    #print("DEBUG:", "place.ant.place=", place.ant.place)
                else: # else if full give error
                    assert place.ant is None, 'Too many ants in {0}'.format(place)
            # END Problem 8b
        Insect.add_to(self, place)

    def remove_from(self, place):
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            assert False, '{0} is not in {1}'.format(self, place)
        else:
            place.ant.remove_ant(self)
        Insect.remove_from(self, place)



class HarvesterAnt(Ant): # damage = 0
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    implemented = True
    # OVERRIDE CLASS ATTRIBUTES HERE
    food_cost = 2 #initialize food_cost class attribute (all ants of a subclass cost the same)

    def action(self, gamestate):
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        # BEGIN Problem 1
        "*** YOUR CODE HERE ***"
        #PART B
        #add 1 unit to the gamestate.food total as its action
        gamestate.food += 1
        # END Problem 1


class ThrowerAnt(Ant): # damage = 1
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""
    name = 'Thrower'
    implemented = True
    damage = 1
    # ADD/OVERRIDE CLASS ATTRIBUTES HERE
    food_cost = 3 #initialize food_cost class attribute (all ants of a subclass cost the same)
    lower_bound = 0
    upper_bound = 1e6
    skip_4s_place = False
    place_count = 0

    def __init__(self, health=1):
        super().__init__(health)

    def nearest_bee(self):
        """Return the nearest Bee in a Place (that is not the hive) connected to
        the ThrowerAnt's Place by following entrances.

        This method returns None if there is no such Bee (or none in range).
        """
        # BEGIN Problem 3 and 4
        """
        1. Start from the current Place of the ThrowerAnt.

        2. For each place, return a random bee if there is any, and if not, 
           inspect the place in front of it (stored as the current place's entrance).

        3. If there is no bee to attack, return None.
        """
        current_place = self.place # current place is initialized to the place of the thrower ant
        while True: 
            if not current_place.is_hive: # if the current place is not the hive
                bee_is_here = random_bee(current_place.bees) # get a bee at random OR get None
                print("DEBUG: ", "current place:", current_place, "bee:", bee_is_here, "place count", self.place_count)
                
                if self.skip_4s_place == False:
                    if bee_is_here: # if a bee exists i.e. not None
                        if self.place_count >= self.lower_bound and self.place_count <= self.upper_bound:
                            return bee_is_here
                        else:
                            return None
                    elif not bee_is_here: # if a bee does not exist i.e. None
                        next_place = current_place.entrance # the next place to check is the entrance of the current place
                        current_place = next_place # update the place for the next loop iteration
                        self.place_count += 1

                elif self.skip_4s_place == True and self.place_count != 4:
                    if bee_is_here: # if a bee exists i.e. not None
                        if self.place_count >= self.lower_bound and self.place_count <= self.upper_bound:
                            return bee_is_here
                        else:
                            return None
                    elif not bee_is_here: # if a bee does not exist i.e. None
                        next_place = current_place.entrance # the next place to check is the entrance of the current place
                        current_place = next_place # update the place for the next loop iteration
                        self.place_count += 1

                else:
                    next_place = current_place.entrance # the next place to check is the entrance of the current place
                    current_place = next_place # update the place for the next loop iteration
                    self.place_count += 1
            else:
                return None
        # END Problem 3 and 4


    def throw_at(self, target):
        """Throw a leaf at the target Bee, reducing its health."""
        print("DEBUG:", "target:", target, "damage:", self.damage)
        if target is not None:
            target.reduce_health(self.damage)


    def action(self, gamestate):
        """Throw a leaf at the nearest Bee in range."""
        #print("DEBUG:", "throwing")
        self.throw_at(self.nearest_bee())


def random_bee(bees):
    """Return a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), \
        "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)

##############
# Extensions #
##############

class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    implemented = True   # Change to True to view in the GUI
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    lower_bound = 1
    upper_bound = 3
    skip_4s_place = True
    # END Problem 4


class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    implemented = True   # Change to True to view in the GUI
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    lower_bound = 5
    upper_bound = 100
    skip_4s_place = True

    def __init__(self, health=1):
        super().__init__(health)
    # END Problem 4


class FireAnt(Ant): # damage = 3
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage = 3
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 5
    implemented = True   # Change to True to view in the GUI

    # END Problem 5

    def __init__(self, health=3):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and remove the FireAnt from its place if it
        has no health remaining.

        Make sure to reduce the health of each bee in the current place, and apply
        the additional damage if the fire ant dies.
        """
        # BEGIN Problem 5
        "*** YOUR CODE HERE ***"
        damage_to_reflect = amount
        curr_place = self.place # FireAnt's place

        bees_in_curr_place = curr_place.bees # list of bees in FireAnt's place to iterate over
        working_bees_in_curr_place = bees_in_curr_place[:] # copy of list to mutate and return

        super().reduce_health(amount) # reduce the current FireAnt instance's health

        if self.place is not curr_place: # if FireAnt has died and been removed
            damage_to_reflect += self.damage

            for i in range(len(bees_in_curr_place)):
                bee = working_bees_in_curr_place[i]
                #print("DEBUG:", "--BEE(a>=sh)--", bee)
                bee.health -= damage_to_reflect
                #print("DEBUG:", "--BEE.HEALTH(a>=sh)--", bee)

                if bee.health <= 0:
                    bee.zero_health_callback()
                    bee.place.remove_insect(bee)
        else:
            for i in range(len(bees_in_curr_place)):
                bee = working_bees_in_curr_place[i]
                #print("DEBUG:", "--BEE(else)--", bee)
                bee.health -= damage_to_reflect
                #print("DEBUG:", "--BEE.HEALTH(else)--", bee)


                if bee.health <= 0:
                    bee.zero_health_callback()
                    bee.place.remove_insect(bee)

        # END Problem 5


# BEGIN Problem 6
# The WallAnt class
class WallAnt(Ant): # damage = 0
    name = "Wall"
    damage = 0
    food_cost = 4
    implemented = True

    def __init__(self, health=4): # wall ant w/ health of 4
        super().__init__(health)
# END Problem 6


# BEGIN Problem 7
# The HungryAnt Class
class HungryAnt(Ant): # damage = 0
    name = "Hungry"
    damage = 0 # damage is equal to target bee's health
    food_cost = 4
    implemented = True
    chew_cooldown = 3 # class attribute that stores the number of turns that it will take a HungryAnt to chew (set to 3)

    def __init__(self, health=1):
        super().__init__(health)
        self.cooldown = 0 # counts the number of turns it has left to chew, initialized to 0
    
    # Implement the action method of the HungryAnt
        # First, check if it is chewing; if so, decrement its cooldown
        # Otherwise, eat a random Bee in its place by reducing the Bee's health to 0.
        # -- set the cooldown when a Bee is eaten!
    

    def action(self, gamestate):
        curr_place = self.place

        if self.cooldown == 0:
            target = random_bee(curr_place.bees)

            if target == None:
                pass
            else:
                self.damage = target.health
                target.reduce_health(self.damage)
                self.cooldown = self.chew_cooldown
        elif self.cooldown != 0:
            self.cooldown -= 1

    def random_bee(bees):
        """Return a random bee from a list of bees, or return None if bees is empty."""
        assert isinstance(bees, list), \
            "random_bee's argument should be a list but was a %s" % type(bees).__name__
        if bees:
            return random.choice(bees)
# END Problem 7


class ContainerAnt(Ant): # damage = 0
    """
    ContainerAnt can share a space with other ants by containing them.
    """
    is_container = True

    def __init__(self, health):
        super().__init__(health)
        self.ant_contained = None

    def can_contain(self, other):
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        if self.ant_contained == None and other.is_container == False:
            return True
        else:
            return False
        # END Problem 8a

    def store_ant(self, ant):
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        if self.ant_contained == None:
            self.ant_contained = ant
        # END Problem 8a

    def remove_ant(self, ant):
        if self.ant_contained is not ant:
            assert False, "{} does not contain {}".format(self, ant)
        self.ant_contained = None

    def remove_from(self, place):
        # Special handling for container ants
        if place.ant is self:
            # Container was removed. Contained ant should remain in the game
            place.ant = place.ant.ant_contained
            Insect.remove_from(self, place)
        else:
            # default to normal behavior
            Ant.remove_from(self, place)

    def action(self, gamestate):
        # BEGIN Problem 8a
        "*** YOUR CODE HERE ***"
        """This method will ensure that if our ContainerAnt currently 
        contains an ant, ant_contained's action is performed."""
        if self.ant_contained != None:
            self.ant_contained.action(gamestate)
        # END Problem 8a


class BodyguardAnt(ContainerAnt): # damage = 0
    """BodyguardAnt provides protection to other Ants."""

    name = 'Bodyguard'
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 8c
    implemented = True   # Change to True to view in the GUI
    def __init__(self, health=2): # initial health = 2
        super().__init__(health)
    # END Problem 8c

# BEGIN Problem 9
# The TankAnt class
class TankAnt(ContainerAnt): # damage = 1
    name = "Tank"
    food_cost = 6
    damage = 1
    implemented = True
    
    def __init__(self, health=2):
        super().__init__(health)
    
    # deals 1 damage to all bees in its place each turn.
    def action(self, gamestate):
        curr_place = self.place

        bees_in_curr_place = curr_place.bees # list of bees in FireAnt's place to iterate over
        working_bees_in_curr_place = bees_in_curr_place[:] # copy of list to mutate and return

        if self.place is curr_place:
            for i in range(len(bees_in_curr_place)):
                bee = working_bees_in_curr_place[i]
                bee.health -= self.damage
                if bee.health <= 0:
                    bee.zero_health_callback()
                    bee.place.remove_insect(bee)

        return super().action(gamestate) # allows ant inside TankAnt to still act
# END Problem 9


class Water(Place):
    """Water is a place that can only hold waterproof insects."""

    def add_insect(self, insect):
        """Add an Insect to this place. If the insect is not waterproof, reduce
        its health to 0."""
        # BEGIN Problem 10
        "*** YOUR CODE HERE ***"
        # First, add the insect to the place regardless of whether it is waterproof. 
        Place.add_insect(self, insect)
        # Then, if the insect is not waterproof, reduce the insect's health to 0.
        if insect.is_waterproof is not True:
            insect.reduce_health(insect.health)
        # END Problem 10


# BEGIN Problem 11
# The ScubaThrower class
class ScubaThrower(ThrowerAnt): # damage = ThrowerAnt
    name = "Scuba"
    food_cost = 6
    is_waterproof = True
    implemented = True

    def __init__(self, health=1):
        super().__init__(health)
# END Problem 11


class QueenAnt(ThrowerAnt): # damage = idk
    """QueenAnt boosts the damage of all ants behind her."""

    name = 'Queen'
    food_cost = 7
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 12
    implemented = True   # Change to True to view in the GUI

    def __init__(self, health=1):
        super().__init__(health)

    # END Problem 12

    def action(self, gamestate):
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.
        """
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***" 
        queens_place = self.place
        #print("DEBUG: queen's place", queens_place)
        curr_place = queens_place
        #print("DEBUG: current place", curr_place)
        curr_entrance = curr_place.exit
        #print("DEBUG: current entrance", curr_entrance)
        curr_exit = curr_entrance.exit
        #print("DEBUG: current exit", curr_exit)
        

        # iterate through spots behind queen ant
        while curr_exit is not None:
            # check if an ant is persent at place
            print("DEBUG: ANT", curr_entrance.ant)
            if curr_entrance.ant is not None:
                # check if ant double_damage is False
                temp_ant = curr_entrance.ant

                if temp_ant.is_container and temp_ant.ant_contained:
                    if temp_ant.double_damage_multiplier_bool is False:
                        temp_ant.double_damage_multiplier_bool = True # if False turn to True
                        temp_ant.double()
                    temp_ant = temp_ant.ant_contained

                print("DEBUG:", "DAMAGE", temp_ant.damage, "BOOL", temp_ant.double_damage_multiplier_bool)
                if temp_ant.double_damage_multiplier_bool is False:
                    temp_ant.double_damage_multiplier_bool = True # if False turn to True
                    temp_ant.double()
                    print("DEBUG:", "2xDAMAGE", temp_ant.damage, "BOOL", temp_ant.double_damage_multiplier_bool)


            # move to next place
            curr_place = curr_entrance
            #print("DEBUG: NEW current place", curr_place)
            curr_entrance = curr_place.exit
            #print("DEBUG: NEW current exit", curr_entrance)
            curr_exit = curr_entrance.exit
            #print("DEBUG: NEW current entrance", curr_exit)

        return super().action(gamestate)    
        # END Problem 12

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and if the QueenAnt has no health
        remaining, signal the end of the game.
        """
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        curr_place = self.place

        super().reduce_health(amount)

        if self.place is not curr_place:
            return ants_lose()
        # END Problem 12


################
# Extra Challenge #
################

class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""

    name = 'Slow'
    food_cost = 6
    # BEGIN Problem EC 1
    implemented = False   # Change to True to view in the GUI
    # END Problem EC 1

    def throw_at(self, target):
        # BEGIN Problem EC 1
        "*** YOUR CODE HERE ***"
        # END Problem EC 1


class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""

    name = 'Scary'
    food_cost = 6
    # BEGIN Problem EC 2
    implemented = False   # Change to True to view in the GUI
    # END Problem EC 2

    def throw_at(self, target):
        # BEGIN Problem EC 2
        "*** YOUR CODE HERE ***"
        # END Problem EC 2


class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place."""

    name = 'Ninja'
    damage = 1
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem EC 3
    implemented = False   # Change to True to view in the GUI
    # END Problem EC 3

    def action(self, gamestate):
        # BEGIN Problem EC 3
        "*** YOUR CODE HERE ***"
        # END Problem EC 3


class LaserAnt(ThrowerAnt):
    """ThrowerAnt that damages all Insects standing in its path."""

    name = 'Laser'
    food_cost = 10
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem EC 4
    implemented = False   # Change to True to view in the GUI
    # END Problem EC 4

    def __init__(self, health=1):
        super().__init__(health)
        self.insects_shot = 0

    def insects_in_front(self):
        # BEGIN Problem EC 4
        return {}
        # END Problem EC 4

    def calculate_damage(self, distance):
        # BEGIN Problem EC 4
        return 0
        # END Problem EC 4

    def action(self, gamestate):
        insects_and_distances = self.insects_in_front()
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            insect.reduce_health(damage)
            if damage:
                self.insects_shot += 1

########
# Bees #
########

class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_waterproof = True


    def sting(self, ant):
        """Attack an ANT, reducing its health by 1."""
        ant.reduce_health(self.damage)

    def move_to(self, place):
        """Move from the Bee's current Place to a new PLACE."""
        self.place.remove_insect(self)
        place.add_insect(self)

    def blocked(self):
        """Return True if this Bee cannot advance to the next Place."""
        # Special handling for NinjaAnt
        # BEGIN Problem EC 3
        return self.place.ant is not None
        # END Problem EC 3

    def action(self, gamestate):
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.

        gamestate -- The GameState, used to access game state information.
        """
        destination = self.place.exit


        if self.blocked():
            self.sting(self.place.ant)
        elif self.health > 0 and destination is not None:
            self.move_to(destination)

    def add_to(self, place):
        place.bees.append(self)
        super().add_to( place)

    def remove_from(self, place):
        place.bees.remove(self)
        super().remove_from(place)

    def scare(self, length):
        """
        If this Bee has not been scared before, cause it to attempt to
        go backwards LENGTH times.
        """
        # BEGIN Problem EC 2
        "*** YOUR CODE HERE ***"
        # END Problem EC 2


class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name = 'Wasp'
    damage = 2


class Boss(Wasp):
    """The leader of the bees. Damage to the boss by any attack is capped.
    """
    name = 'Boss'
    damage_cap = 8

    def reduce_health(self, amount):
        super().reduce_health(min(amount, self.damage_cap))


class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """
    is_hive = True

    def __init__(self, assault_plan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees = []
        for bee in assault_plan.all_bees():
            self.add_insect(bee)
        # The following attributes are always None for a Hive
        self.entrance = None
        self.ant = None
        self.exit = None

    def strategy(self, gamestate):
        exits = [p for p in gamestate.places.values() if p.entrance is self]
        for bee in self.assault_plan.get(gamestate.time, []):
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)

###################
# Game Components #
###################

class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    """

    def __init__(self, beehive, ant_types, create_places, dimensions, food=2):
        """Create an GameState for simulating a game.

        Arguments:
        beehive -- a Hive full of bees
        ant_types -- a list of ant classes
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time = 0
        self.food = food
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees = []
        self.configure(beehive, create_places)

    def configure(self, beehive, create_places):
        """Configure the places in the colony."""
        self.base = AntHomeBase('Ant Home Base')
        self.places = OrderedDict()
        self.bee_entrances = []

        def register_place(place, is_bee_entrance):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)
        register_place(self.beehive, False)
        create_places(self.base, register_place,
                      self.dimensions[0], self.dimensions[1])

    def ants_take_actions(self): # Ask ants to take actions
        for ant in self.ants:
            if ant.health > 0:
                ant.action(self)

    def bees_take_actions(self, num_bees): # Ask bees to take actions
        for bee in self.active_bees[:]:
            if bee.health > 0:
                bee.action(self)
            if bee.health <= 0:
                num_bees -= 1
                self.active_bees.remove(bee)
        if num_bees == 0: # Check if player won
            raise AntsWinException()
        return num_bees

    def simulate(self):
        """Simulate an attack on the ant colony. This is called by the GUI to play the game."""
        num_bees = len(self.bees)
        try:
            while True:
                self.beehive.strategy(self) # Bees invade from hive
                yield None # After yielding, players have time to place ants
                self.ants_take_actions()
                self.time += 1
                yield None # After yielding, wait for throw leaf animation to play, then ask bees to take action
                num_bees = self.bees_take_actions(num_bees)
        except AntsWinException:
            print('All bees are vanquished. You win!')
            yield True
        except AntsLoseException:
            print('The bees reached homebase or the queen ant queen has perished. Please try again :(')
            yield False

    def deploy_ant(self, place_name, ant_type_name):
        """Place an ant if enough food is available.

        This method is called by the current strategy to deploy ants.
        """
        ant_type = self.ant_types[ant_type_name]
        if ant_type.food_cost > self.food:
            print('Not enough food remains to place ' + ant_type.__name__)
        else:
            ant = ant_type()
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name):
        """Remove an Ant from the game."""
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status


class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen normally resides."""

    def add_insect(self, insect):
        """Add an Insect to this Place.

        Can't actually add Ants to a AntHomeBase. However, if a Bee attempts to
        enter the AntHomeBase, a AntsLoseException is raised, signaling the end
        of a game.
        """
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise AntsLoseException()


def ants_win():
    """Signal that Ants win."""
    raise AntsWinException()


def ants_lose():
    """Signal that Ants lose."""
    raise AntsLoseException()


def ant_types():
    """Return a list of all implemented Ant classes."""
    all_ant_types = []
    new_types = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]


def bee_types():
    """Return a list of all implemented Bee classes."""
    all_bee_types = []
    new_types = [Bee]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_bee_types.extend(new_types)
    return all_bee_types


class GameOverException(Exception):
    """Base game over Exception."""
    pass


class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""
    pass


class AntsLoseException(GameOverException):
    """Exception to signal that the ants lose."""
    pass

###########
# Layouts #
###########

def wet_layout(queen, register_place, tunnels=3, length=9, moat_frequency=3):
    """Register a mix of wet and and dry places."""
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)


def dry_layout(queen, register_place, tunnels=3, length=9):
    """Register dry tunnels."""
    wet_layout(queen, register_place, tunnels, length, 0)

#################
# Assault Plans #
#################

class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.

    An AssaultPlan is a dictionary from times (int) to waves (list of Bees).

    >>> AssaultPlan().add_wave(4, 2)
    {4: [Bee(3, None), Bee(3, None)]}
    """

    def add_wave(self, bee_type, bee_health, time, count):
        """Add a wave at time with count Bees that have the specified health."""
        bees = [bee_type(bee_health) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    def all_bees(self):
        """Place all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]