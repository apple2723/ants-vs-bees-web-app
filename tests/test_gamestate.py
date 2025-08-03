from ants import *
from ants_plans import make_test_assault_plan
from ants_gui import *
import pytest

def test_gamestate_time_and_point_update():
    """
    Testing to confrim the point attribute is updated for gamestate
    """
    beehive = Hive(make_test_assault_plan())
    dimensions = (1, 9)
    game1 = GameState(None, beehive, [], dry_layout, dimensions)
    game1.time +=1
    game1.points -=1
    assert game1.time == 1, f"Should be 1 but is: {game1.time}"
    assert game1.points == 49, f"Should be 49s but is: {game1.points}"
    
def dummy_strategy(gamestate):
    pass

def test_gamestate_ants_win_condition():
    beehive = Hive(AssaultPlan())
    dimensions = (1, 9)
    game1 = GameState(dummy_strategy, beehive, [], dry_layout, dimensions)
    assert game1.simulate() is True, f"Ants win"