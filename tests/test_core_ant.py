from ants import Place, Insect, Ant, Bee, HarvesterAnt, FireAnt, LongThrower, ThrowerAnt, GameState
import pytest

class ToyGameState:
    """A minimal toy version of the actual GameState class. This just has a .time and .food value (attributes)."""
    def __init__ (self, time=0, food=0):
        self.time = time
        self.food = food

def test_places_and_add_insect():
    """
    This test creates 4 place instances, connects the places, creates two ants, and runs the add_insect() once
    per ant
    """
    tunnel0_0 = Place("tunnel0_0")
    tunnel0_1 = Place("tunnel0_1", tunnel0_0)
    tunnel0_2 = Place("tunnel0_2", tunnel0_1)
    tunnel0_3 = Place("tunnel0_3", tunnel0_2)
    ant0_0 = HarvesterAnt()
    ant0_2 = HarvesterAnt()
    tunnel0_0.add_insect(ant0_0)
    tunnel0_2.add_insect(ant0_2)

    assert ant0_0.place is tunnel0_0, f"ant0_0.place should have been = tunnel0_0, but it is {ant0_0.place}"
    assert ant0_2.place is tunnel0_2, f"ant0_2.place should have been = tunnel0_2, but it is {ant0_2.place}"
    
    # Checks .exit values of each Place instance: 
    assert tunnel0_3.exit is tunnel0_2, f"tunnel0_3.exit should have been = tunnel0_2, but it is {tunnel0_3.exit}"
    assert tunnel0_2.exit is tunnel0_1, f"tunnel0_2.exit should have been = tunnel0_1, but it is {tunnel0_2.exit}"
    assert tunnel0_1.exit is tunnel0_0, f"tunnel0_1.exit should have been = tunnel0_0, but it is {tunnel0_1.exit}"
    assert tunnel0_0.exit is None, f"tunnel0_0.exit should have been = None, but it is {tunnel0_0.exit}"

    # Checks .entrance values of each Place instance: 
    assert tunnel0_0.entrance is tunnel0_1
    assert tunnel0_1.entrance is tunnel0_2
    assert tunnel0_2.entrance is tunnel0_3
    assert tunnel0_3.entrance is None 


def test_remove_insect_from_place():
    """
    This tests the remove_insect function from the Place class. 
    It creates an ant in a place, and then removes the ant.
    """
    tunnel1_0 = Place("tunnel1_0")
    ant1_0 = HarvesterAnt()
    tunnel1_0.add_insect(ant1_0)
    assert ant1_0.place is tunnel1_0, f"ant1_0.place should have been = tunnel1_0, but it is {ant1_0.place}"
    tunnel1_0.remove_insect(ant1_0)
    assert ant1_0.place is None, f"ant1_0.place should have been = None, but it is {ant1_0.place}"


def test_damage_being_applied_to_Ant():
    """
    This tests that damage towards an Ant causes it to reduce its health.
    """
    tunnel1_1 = Place("tunnel1_1")
    ant1_1 = HarvesterAnt()
    tunnel1_1.add_insect(ant1_1)
    assert ant1_1.place is tunnel1_1, f"ant1_1.place should have been = tunnel1_1, but it is {ant1_1.place}"
    ant1_1.reduce_health(ant1_1.health)
    assert ant1_1.place is None, f"ant1_1.place should have been = None, but it is {ant1_1.place}"


def test_damage_being_applied_to_Ant_by_Bee():
    """
    This tests that if a bee stings an ant, the ant's health gets reduced.
    """
    tunnel0_5 = Place("tunnel0_5")
    ant0_5 = HarvesterAnt()
    tunnel0_5.add_insect(ant0_5)
    bee0_5_1 = Bee(4)
    bee0_5_2 = Bee(4)
    tunnel0_5.add_insect(bee0_5_1)
    tunnel0_5.add_insect(bee0_5_2)
    bee0_5_1.sting(ant0_5)
    bee0_5_2.sting(ant0_5)
    assert bee0_5_1.place is bee0_5_2.place, f"Both bees should be in same place, instead {bee0_5_1.place} != {bee0_5_2.place})"
    if ant0_5.health < 0:
        assert ant0_5.place is None, f"ant0_5.place should have been = None, but it is {ant0_5.place}"
    else:
        assert ant0_5.place is tunnel0_5, f"ant0_5.place should have been = tunnel0_5, but it is {ant0_5.place}"


def test_gamestate_with_food_demands():
    """
    This tests that the food variable in gamestate works.
    Also that you can't create an insect with a higher food cost than your current food
    """
    tunnel0_6 = Place("tunnel0_6")
    tunnel0_7 = Place("tunnel0_7")
    gamestate1 = ToyGameState(0, 2)
    th_ant0_6 = ThrowerAnt()
    assert th_ant0_6.food_cost > gamestate1.food, "Gamestate not supposed to have this much food"
    ant0_6 = HarvesterAnt()
    gamestate1.food -= ant0_6.food_cost
    assert gamestate1.food == 0, f"Food should be 0 but is actually: {gamestate1.food}"
    ant0_6.action(gamestate1)
    gamestate1.time +=1
    assert gamestate1.food == 1, f"Food should be 1 but is actually: {gamestate1.food}"
    ant0_6.action(gamestate1)
    gamestate1.time +=1
    ant0_6.action(gamestate1)
    gamestate1.time +=1
    ant0_6.action(gamestate1)
    gamestate1.time +=1
    ant0_6.action(gamestate1)
    gamestate1.time +=1
    ant0_6.action(gamestate1)
    gamestate1.time +=1
    assert gamestate1.food == 6, f"Food should be 6 but is actually: {gamestate1.food}"
    assert gamestate1.time == 6, f"Time should be 6 but is actually: {gamestate1.food}"
    

def test_LongThrower_distances():
    """
    This tests that a LongThrower can only hit ants 5+ places away.
    """
    place_1 = Place("place1")
    place_2 = Place("place2", place_1)
    place_3 = Place("place3", place_2)
    place_4 = Place("place4", place_3)
    place_5 = Place("place5", place_4)
    place_6 = Place("place6", place_5)
    thrower = LongThrower()
    place_1.add_insect(thrower)
    bee_out_of_range = Bee(4)
    bee_in_range = Bee(4)
    place_3.add_insect(bee_out_of_range)
    place_6.add_insect(bee_in_range)
    assert thrower.nearest_bee() is bee_in_range, f"Should be hitting bee in range, not out of range, is hitting {thrower.nearest_bee()}"
    

def test_FireAnt_damage_to_multiple_bees():
    """
    This tests that a FireAnt reflects the damage its being given
    and that it gives extra damage to all bees in its place if it dies
    """
    place_1 = Place("place1")
    fireant = FireAnt()
    place_1.add_insect(fireant)
    bee_1 = Bee(4)
    bee_2 = Bee(4)
    bee_3 = Bee(4)
    place_1.add_insect(bee_1)
    place_1.add_insect(bee_2)
    place_1.add_insect(bee_3)
    bee_1.sting(fireant)
    assert fireant.health == 2, f"Fire ant health should be 2 but is {fireant.health}"
    assert bee_1.health == 3, f"Bee_1 health should be 3 but is {bee_1.health}"
    assert bee_2.health == 3, f"Bee_2 health should be 3 but is {bee_2.health}"
    assert bee_3.health == 3, f"Bee_3 health should be 3 but is {bee_3.health}"
    bee_2.sting(fireant)
    assert fireant.health == 1, f"Fire ant health should be 2 but is {fireant.health}"
    assert bee_1.health == 2, f"Bee_1 health should be 2 but is {bee_1.health}"
    assert bee_2.health == 2, f"Bee_2 health should be 2 but is {bee_2.health}"
    assert bee_3.health == 2, f"Bee_3 health should be 2 but is {bee_3.health}"
    assert fireant.place is place_1, f"Fireant place should be place1 but is {fireant.place}"
    bee_3.sting(fireant)
    assert fireant.health == 0, f"Fire ant health should be 0 but is {fireant.health}"
    assert fireant.place is None, f"Fire ant place should be None but is {fireant.place}"
    assert bee_1.health <= 0, f"Bee_1 health should be 0 but is {bee_1.health}"
    assert bee_2.health <= 0, f"Bee_2 health should be 0 but is {bee_2.health}"
    assert bee_3.health <= 0, f"Bee_3 health should be 0 but is {bee_3.health}"
    assert bee_1.place is None, f"Bee_1 place should be None but is {bee_1.place}"
    assert bee_2.place is None, f"Bee_2 place should be None but is {bee_2.place}"
    assert bee_3.place is None, f"Bee_3 place should be None but is {bee_3.place}"
