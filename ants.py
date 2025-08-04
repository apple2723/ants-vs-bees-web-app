"""CS 88 presents Ants Vs. SomeBees."""

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
        if self.exit:
            self.exit.entrance = self
        # END Problem 2

    def add_insect(self, insect):
        """
        Asks the insect to add itself to the current place. This method exists so
            it can be enhanced in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect):
        """
        Asks the insect to remove itself from the current place. This method exists so
            it can be enhanced in subclasses.
        """
        insect.remove_from(self)

    def __str__(self):
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has health and a Place."""
    next_id = 0
    damage = 0
    is_waterproof = False
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, health, place=None):
        """Create an Insect with a health amount and a starting PLACE."""
        self.health = health
        self.place = place  # set by Place.add_insect and Place.remove_insect
        self.id = Insect.next_id         #     self.id is a _INSTANCE_ attribute
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
            self.death_callback()
            if self.place is not None:
                self.place.remove_insect(self)

    def action(self, gamestate):
        """The action performed each turn.

        gamestate -- The GameState, used to access game state information.
        """

    def death_callback(self):
        # overriden by the gui
        pass

    def add_to(self, place):
        """Add this Insect to the given Place

        By default just sets the place attribute, but this should be overriden in the subclasses
            to manipulate the relevant attributes of Place
        """
        self.place = place

    def remove_from(self, place):
        self.place = None


    def __repr__(self):
        cname = type(self).__name__
        return '{0}({1}, {2})'.format(cname, self.health, self.place)


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    is_implemented = False  # Only implemented Ant classes should be instantiated
    food_cost = 0
    is_container = False
    blocks_path = True
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, health=1, doubled=False):
        """Create an Insect with a HEALTH quantity."""
        super().__init__(health)
        self.doubled = doubled

    def can_contain(self, other):
        return False

    def store_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def remove_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def add_to(self, place):
        if place.ant is None:
            place.ant = self
            Insect.add_to(self, place) 
            #print(f"At place {place}, contains: {self}")
        else:
            # BEGIN Problem 8
            "*** YOUR CODE HERE ***"
            # CHECK VALUES OF EXISTING AND NEW ANTS 
            ant_at_place = place.ant 
            #print(f"At place {place}, contains: {ant_at_place}")

            if place.ant.can_contain(self):   # <-- if place has ant and it can contain another ant...
                # Situation 1: Already has a container ant so you can add a new ant
                #print(f"The ant: {ant_at_place} can contain {self}, so will store it inside")
                place.ant.store_ant(self)    # <-- need to store the ant at the place 
                Insect.add_to(place.ant, place)   # <-- Update the instance
                Insect.add_to(self, place)   #<-- Gives the new ant the same place
                #print(f"After storing, new value of place: {place}, place.ant: {place.ant}, place.ant.ant_contained: {place.ant.ant_contained}")

            elif self.can_contain(place.ant):  # <-- if the current Ant (i.e. self) can contain another ant...
                #Situation 2: Has an ant, but you're adding a container ant
                #print(f"The ant: {self} can contain the ant at the place {ant_at_place}, so swapping")
                # 1. save copy of the current ant at the place 
                ant_at_place = place.ant 

                # 2. reset what place.ant is (to self)
                place.ant = self 

                # 3. use the Insect.add_to() method to add the current ant (self) to place 
                Insect.add_to(self, place)     # <-- need to update what the current ant instance knows is place 

                # 4. finally, put ant that was at this place inside of the container ant (self) 
                self.store_ant(ant_at_place)

                Insect.add_to(ant_at_place, place)
    
                #print(f"After swapping, new value of place: {place}, place.ant: {place.ant}, place.ant.ant_contained: {place.ant.ant_contained}")
                
            else:
                #Situation 3: None of them are container ants
                # NEED TO THROW ASSERTION ERROR HERE...
                assert place.ant is None, 'Two ants in {0}'.format(place)
            # END Problem 8

    def remove_from(self, place):
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            assert False, '{0} is not in {1}'.format(self, place)
        else:
            place.ant.remove_ant(self)
        Insect.remove_from(self, place)

    def double(self):
        """Double this ants's damage, if it has not already been doubled."""
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        if self.doubled == False:
            self.damage *= 2
            self.doubled = True
        # END Problem 12

class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    is_implemented = True
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE

    def action(self, gamestate):
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        # BEGIN Problem 1
        "*** YOUR CODE HERE ***"
        gamestate.food += 1
        # END Problem 1


class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name = 'Thrower'
    is_implemented = True
    damage = 1
    food_cost = 3

    # BEGIN Problem 4
    # default range: any bee in front 
    "*** YOUR CODE HERE***"
    min_range = 0
    max_range = float('inf')
    # END Problem 4 
    # ADD/OVERRIDE CLASS ATTRIBUTES HERE

    def nearest_bee(self):
        """Return the nearest Bee in a Place (that is not the hive) connected to
        the ThrowerAnt's Place by following entrances.

        This method returns None if there is no such Bee (or none in range).
        """
        # BEGIN Problem 3 and 4
        "*** YOUR CODE HERE***"
        import pdb
        # HINT: self.place is 1 instance of Place and is your starting place to search. 
        # For the while loop, start with something equal to self.place, check, 
        # and then update that thing to be the next place...
        location = self.place
        #pdb.set_trace()
        distance = 0 
        
        while location is not None:
            if location.is_hive == False:
                if self.min_range <= distance <= self.max_range:
                    if len(location.bees) >= 1:
                        return random_bee(location.bees)
                location = location.entrance
                distance += 1
            else:
                break
          
        return None    
            
        # END Problem 3 and 4

    def throw_at(self, target):
        """Throw a leaf at the target Bee, reducing its health."""
        if target is not None:
            target.reduce_health(self.damage)

    def action(self, gamestate):
        """Throw a leaf at the nearest Bee in range."""
        self.throw_at(self.nearest_bee())

class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    "*** YOUR CODE HERE ***"
    is_implemented = True
    min_range = 0
    max_range = 3
    # END Problem 4 

class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    "*** YOUR CODE HERE***"
    is_implemented = True
    min_range = 5
    max_range = float('inf')
    # END Problem 4 

def random_bee(bees):
    """Return a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), \
        "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)

class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage = 3
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 5
    "*** YOUR CODE HERE ***"
    is_implemented = True   # Change to True to view in the GUI
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
        
        list_of_bees = list(self.place.bees)
        for bee in list_of_bees:
            bee.reduce_health(amount)
            if amount >= self.health:
                #FireAnt died so extra damage is given
                bee.reduce_health(self.damage)
        #FireAnt has to attack and then die
        super().reduce_health(amount)

        # END Problem 5

# BEGIN Problem 6
"*** YOUR CODE HERE ***"
class WallAnt(Ant):
    name = 'Wall'
    food_cost = 4
    is_implemented = True

    def __init__(self, health=4):
        super().__init__(health)
# The WallAnt class
# END Problem 6

# BEGIN Problem 7
"*** YOUR CODE HERE ***"
class HungryAnt(Ant):
    name = "Hungry"
    food_cost = 4
    is_implemented = True
    chew_duration = 3

    def __init__(self, health=1):
        super().__init__(health)
        self.chew_countdown = 0
    
    def action(self, gamestate):
        if self.chew_countdown == 0:
            # HungryAnt can eat random bee at this turn
            randombee = random_bee(self.place.bees)
            if randombee is not None:
                randombee.reduce_health(randombee.health)
                self.chew_countdown = self.chew_duration
        else:
            #Hungryant has to wait to chew
            self.chew_countdown -= 1


# The HungryAnt Class
# END Problem 7

class ContainerAnt(Ant):
    """
    ContainerAnt can share a space with other ants by containing them.
    """
    is_container = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ant_contained = None

    def can_contain(self, other):
        """
        Return true if 
        - ContainerAnt does not already contain another ant 
        - other ant is not a container
        """
        # BEGIN Problem 8
        "*** YOUR CODE HERE ***"
        if self.ant_contained is None:
            if other.is_container == False:
                return True
        return False
        # END Problem 8

    def store_ant(self, ant):
        # BEGIN Problem 8
        "*** YOUR CODE HERE ***"
        self.ant_contained = ant
        # END Problem 8

    def remove_ant(self, ant):
        if self.ant_contained is not ant:
            assert False, "{} does not contain {}".format(self, ant)
        self.ant_contained = None

    def remove_from(self, place):
        # Special handling for container ants (this is optional)
        if place.ant is self:
            # Container was removed. Contained ant should remain in the game
            place.ant = place.ant.ant_contained
            Insect.remove_from(self, place)
        else:
            # default to normal behavior
            Ant.remove_from(self, place)

    def action(self, gamestate):
        # BEGIN Problem 8
        "*** YOUR CODE HERE ***"
        if self.ant_contained is not None:
            self.ant_contained.action(gamestate)
        # END Problem 8

class BodyguardAnt(ContainerAnt):
    """BodyguardAnt provides protection to other Ants."""

    name = 'Bodyguard'
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 8
    "*** YOUR CODE HERE ***"
    is_implemented = True   # Change to True to view in the GUI
    def __init__(self, health=2):
        super().__init__(health)
    # END Problem 8

# BEGIN Problem 9

"*** YOUR CODE HERE ***"
class TankAnt(ContainerAnt):
    """TankAnt provides protection to other Ants and deals damage 1 to all bees in its place."""
    name = 'Tank'
    food_cost = 6
    damage = 1
    is_implemented = True   # Change to True to view in the GUI
    def __init__(self, health=2):
        super().__init__(health)
    def action(self, gamestate):
        list_of_bees = list(self.place.bees)
        for bee in list_of_bees:
            bee.reduce_health(self.damage)
        super().action(gamestate)

    
# The TankAnt class
# END Problem 9


class Water(Place):
    """Water is a place that can only hold waterproof insects."""

    def add_insect(self, insect):
        """Add an Insect to this place. If the insect is not waterproof, reduce
        its health to 0."""
        # BEGIN Problem 10
        "*** YOUR CODE HERE ***"
        insect.add_to(self)
        if insect.is_waterproof == False:
            insect.reduce_health(insect.health)
        # END Problem 10

# BEGIN Problem 11
"*** YOUR CODE HERE ***"
# The ScubaThrower classs
class ScubaThrower(ThrowerAnt):
    name = 'Scuba'
    is_implemented = True
    damage = 1
    food_cost = 6
    is_waterproof = True
    min_range = 0
    max_range = float('inf')
# END Problem 11

# BEGIN Problem 12
"*** YOUR CODE HERE ***"
class QueenAnt(ScubaThrower):  # You should change this line
# END Problem 12
    """The Queen of the colony. The game is over if a bee enters her place."""

    name = 'Queen'
    food_cost = 7
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 12
    "*** YOUR CODE HERE ***"
    is_implemented = True   # Change to True to view in the GUI
    # END Problem 12

    def __init__(self, gamestate):
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        if gamestate.canhavequeenant == False:
            raise DuplicateQueensException()
        else:
            gamestate.canhavequeenant = False
            super().__init__()

         # END Problem 12

    def action(self, gamestate):
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.
        """
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        
        current_place = self.place
        previous_place = current_place
        while previous_place is not None:
            previous_place = current_place.exit
            #print (f"Current place: {current_place}, previous place: {previous_place}")
            # Logic to tell the ant to double its damage & determine if ant's damage should be doubled
            if previous_place is None:
                break
            if previous_place.ant is not None:
                #print (f"Previous place ant: {previous_place.ant}, Ant.name: {previous_place.ant.name}")
                if previous_place.ant.is_container == True:
                    #print (f"Previous place ant before double: {previous_place.ant.ant_contained}, damage: {previous_place.ant.ant_contained.damage}")
                    previous_place.ant.ant_contained.double()
                    previous_place.ant.ant_contained.doubled = True
                    #print (f"Previous place ant after double: {previous_place.ant.ant_contained}, damage: {previous_place.ant.ant_contained.damage}")
                else:
                    #print (f"Previous place ant before double: {previous_place.ant}, damage: {previous_place.ant.damage}")
                    previous_place.ant.double()
                    previous_place.ant.doubled = True
                    #print (f"Previous place ant after double: {previous_place.ant}, damage: {previous_place.ant.damage}")

            current_place = previous_place


        # END Problem 12

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and if the QueenAnt has no health
        remaining, signal the end of the game.
        """
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        if (amount == self.health):
            ants_lose()
        super().reduce_health(amount)
        # END Problem 12
    
    def remove_from(self, place):
        pass



class AntRemover(Ant):
    """Allows the player to remove ants from the board in the GUI."""

    name = 'Remover'
    is_implemented = False

    def __init__(self):
        super().__init__(0)



class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_waterproof = True    # class attribute: bees are waterproof 
    def __init__(self, health=3):
        super().__init__(health)
        self.slow_turns = 0    # number of turns bee has left to be slow over
        self.is_scared = False
        self.scared_turns = 0 #number of turns bee has left to be scared for

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
        "*** YOUR CODE HERE ***"
        # END Problem EC 3
        if self.place.ant is not None:
            if self.place.ant.blocks_path == True:
                return True
        return False

    def action(self, gamestate):
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.

        gamestate -- The GameState, used to access game state information.
        """
        #print ("----")
        destination = self.place.exit

        if self.slow_turns > 0: #slow
            #print (f"{self.id}-{self.name} is slow, slow_turns = {self.slow_turns}")

            if gamestate.time % 2 != 0: #gametime is odd
                self.slow_turns -= 1
                #print (f"Time is odd: {gamestate.time} and slow_turns {self.slow_turns}")
                if self.scared_turns > 0: #is scared if 0<scaredturns <2
                    self.scared_turns -= 1
                return

            else:
                #print (f"Time is even: {gamestate.time} and slow_turns {self.slow_turns}")
                self.slow_turns -= 1

        if self.blocked():
            # If an ant dies, subtract 7 points
            if self.damage >= self.place.ant.health:
                gamestate.points -=7
            self.sting(self.place.ant)
        
        elif self.scared_turns > 0:
            self.scared_turns -= 1
            if self.place.entrance == self.place.is_hive:
                return
            self.move_to(self.place.entrance)
            return

        elif self.health > 0 and destination is not None:
            #print (f"Destination: {destination} for bee {self.id}-{self.name}")
            self.move_to(destination)

    def add_to(self, place):
        place.bees.append(self)
        super().add_to( place)

    def remove_from(self, place):
        place.bees.remove(self)
        super().remove_from(place)

    def slow(self, num_turns):
        """
        If this Bee has been slowed, add num_turns to the counter 
        for how long it needs to be slowed for
        """
        # BEGIN Problem EC 1
        "*** YOUR CODE HERE ***"
        self.slow_turns += num_turns
        # END Problem EC 1

    def scare(self, length):
        """
        If this Bee has not been scared before, cause it to attempt to
        go backwards LENGTH times.
         -> 1. If bee is next to hive (self.place.entrance == is_hive), does not move (place is same)
         -> 2. if they get scared, try to back away twice (done)
         -> 3. if self.slow_turns > 0 && gamestate.time %2 != 0, cannot back away (done)
         -> 4. if it's scared once, can't be scared again (done)
        """
        # BEGIN Problem EC 2
        "*** YOUR CODE HERE ***"
        if self.is_scared == False:
            self.scared_turns = length
            self.is_scared = True
            
        # END Problem EC 2




############
# Optional #
############

class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place.
    This class is optional.
    """

    name = 'Ninja'
    damage = 1
    food_cost = 5
    blocks_path = False
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem Optional 1
    "*** YOUR CODE HERE ***"
    is_implemented = True   # Change to True to view in the GUI
    # END Problem Optional 1

    def action(self, gamestate):
        # BEGIN Problem Optional 1
        "*** YOUR CODE HERE ***"
        list_of_bees = list(self.place.bees)
        for bee in list_of_bees:
            bee.reduce_health(self.damage)
        # END Problem Optional 1

############
# Statuses #
############

class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""

    name = 'Slow'
    food_cost = 4
    slow_amount = 3
    # BEGIN Problem EC
    "*** YOUR CODE HERE ***"
    is_implemented = True   # Change to True to view in the GUI
    def throw_at(self, target):
        if target is not None:
            target.slow(SlowThrower.slow_amount)
            #print (f"Target: {target.id} becomes slow")
    # END Problem EC

class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""

    name = 'Scary'
    food_cost = 6
    scare_length = 2
    # BEGIN Problem EC
    "*** YOUR CODE HERE ***"
    is_implemented = True   # Change to True to view in the GUI
    # END Problem EC
    
    def throw_at(self, target):
        # BEGIN Problem EC
        "*** YOUR CODE HERE ***"
        if target is not None:
            target.scare(ScaryThrower.scare_length)
        # END Problem EC

class LaserAnt(ThrowerAnt):
    # This class is optional. Only one test is provided for this class.

    name = 'Laser'
    food_cost = 10
    damage = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem Optional 2
    "*** YOUR CODE HERE ***"
    is_implemented = True   # Change to True to view in the GUI
    # END Problem Optional 2

    def __init__(self, health=1):
        super().__init__(health)
        self.insects_shot = 0

    def insects_in_front(self):
        # BEGIN Problem Optional 2
        "*** YOUR CODE HERE ***"
        front_insects ={}
        distance = 0
        next_place = self.place.entrance
        if self.place.ant.is_container == True:
            front_insects[self.place.ant] = distance
        while next_place.is_hive == False:
            distance += 1
            if next_place.ant is not None:
                front_insects[next_place.ant] = distance
            list_of_bees = list(next_place.bees)
            for bee in list_of_bees:
                front_insects[bee] = distance
            next_place = next_place.entrance
        return front_insects
        # END Problem Optional 2

    def calculate_damage(self, distance):
        # BEGIN Problem Optional 2
        "*** YOUR CODE HERE ***"
        """
        1. damage -0.25 every distance +
        2. laser hits an insect -> damage -0.0625
        3. damage <0 -> damage = 0

        pseudocode: 
        1. damage = damage - distance(0.25)
        2. self.this_damage = self.this_damage - self.insects_shot(0.0625)
        3. if self.damage < 0:
            self.damage = 0
        """
        this_damage = LaserAnt.damage - (distance*0.25) - (self.insects_shot*0.0625)
        if this_damage < 0:
            this_damage = 0
        return this_damage
        # END Problem Optional 2

    def action(self, gamestate):
        insects_and_distances = self.insects_in_front()
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            print (f"Gamestate time & damage: {gamestate.time} & {damage}")
            print (f"Insect {insect.name}-{insect.id}'s health before laser: {insect.health}")
            insect.reduce_health(damage)
            print (f"Insect {insect.name}-{insect.id}'s health after laser: {insect.health}")
            if damage:
                self.insects_shot += 1



##################
# Bees Extension #
##################

class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name = 'Wasp'
    damage = 2

class Hornet(Bee):
    """Class of bee that is capable of taking two actions per turn, although
    its overall damage output is lower. Immune to statuses.
    """
    name = 'Hornet'
    damage = 0.25

    def action(self, gamestate):
        for i in range(2):
            if self.health > 0:
                super().action(gamestate)

    def __setattr__(self, name, value):
        if name != 'action':
            object.__setattr__(self, name, value)

class NinjaBee(Bee):
    """A Bee that cannot be blocked. Is capable of moving past all defenses to
    assassinate the Queen.
    """
    name = 'NinjaBee'

    def blocked(self):
        return False

class Boss(Wasp, Hornet):
    """The leader of the bees. Combines the high damage of the Wasp along with
    status immunity of Hornets. Damage to the boss is capped up to 8
    damage by a single attack.
    """
    name = 'Boss'
    damage_cap = 8
    action = Wasp.action

    def reduce_health(self, amount):
        super().reduce_health(self.damage_modifier(amount))

    def damage_modifier(self, amount):
        return amount * self.damage_cap/(self.damage_cap + amount)

class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """
    is_hive = True

    def __init__(self, assault_plan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees = []
        for bee in assault_plan.all_bees:
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


class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    """

    def __init__(self, strategy, beehive, ant_types, create_places, dimensions, food=2, canhavequeenant=True, points=50):
        """Create an GameState for simulating a game.

        Arguments:
        strategy -- a function to deploy ants to places
        beehive -- a Hive full of bees
        ant_types -- a list of ant classes
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time = 0
        self.food = food
        self.strategy = strategy
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees = []
        self.configure(beehive, create_places)
        self.canhavequeenant = canhavequeenant
        self.points = points

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
        create_places(self.base, register_place, self.dimensions[0], self.dimensions[1])

    def simulate(self):
        """Simulate an attack on the ant colony (i.e., play the game)."""
        num_bees = len(self.bees)
        try:
            while True:
                print(f"[ants.py] simulate function Time: {self.time}, Points: {self.points}, Food: {self.food}")
                self.beehive.strategy(self)         # Bees invade
                self.strategy(self)                 # Ants deploy
                for ant in self.ants:               # Ants take actions
                    if ant.health > 0:
                        ant.action(self)
                for bee in self.active_bees[:]:     # Bees take actions
                    if bee.health > 0:
                        bee.action(self)
                    if bee.health <= 0:
                        num_bees -= 1
                        self.active_bees.remove(bee)
                        #Destroying a bee gives 5 points
                        self.points +=5
                if num_bees == 0:
                    raise AntsWinException()
                self.time += 1
                # Points decrease by 1 when time goes up by 1
                self.points -= 1
        except AntsWinException:
            print(f'All bees are vanquished. Your score: {self.points}. You win!')
            return True
        except AntsLoseException:
            print('The ant queen has perished. Please try again.')
            return False

    def deploy_ant(self, place_name, ant_type_name):
        """Place an ant if enough food is available.

        This method is called by the current strategy to deploy ants.
        """
        constructor = self.ant_types[ant_type_name]
        if self.food < constructor.food_cost:
            print('Not enough food remains to place ' + ant_type_name)
            raise NotEnoughFoodException()
        if constructor.__name__ == 'QueenAnt':
            try:
                ant = constructor(self)
            except DuplicateQueensException:
                print("you cannot create a second QueenAnt")
        else:
            ant = constructor()

        if ant:
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name):
        """Remove an Ant from the game."""
        #print (f"[ants.py] remove_ant function, Ant dies, point -7 :{self.points}")
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
    """AntHomeBase at the end of the tunnel, where the queen resides."""

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
    return [t for t in all_ant_types if t.is_implemented]

class GameOverException(Exception):
    """Base game over Exception."""
    pass

class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""
    pass

class AntsLoseException(GameOverException):
    """Exception to signal that the ants lose."""
    pass

class DuplicateQueensException(Exception):
    """Occurs when more than one queen gets created."""
    pass

class NotEnoughFoodException(Exception):
    """Occurs when there is not enough food to create an Ant."""
    pass

def interactive_strategy(gamestate):
    """A strategy that starts an interactive session and lets the user make
    changes to the gamestate.

    For example, one might deploy a ThrowerAnt to the first tunnel by invoking
    gamestate.deploy_ant('tunnel_0_0', 'Thrower')
    """
    print('gamestate: ' + str(gamestate))
    msg = '<Control>-D (<Control>-Z <Enter> on Windows) completes a turn.\n'
    interact(msg)

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

    @property
    def all_bees(self):
        """Place all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]
