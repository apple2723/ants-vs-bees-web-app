from ants import *
import pytest

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_get_state_route(client):
    #Look for status, time, points, and food values
    api_resp = client.get("/api/state")
    api_dict = api_resp.get_json()
    assert api_dict["points"] == 50, f"Api_dict points is not initialized correctly, is: {api_dict.points}"
    assert api_dict["time"] == 0, f"Api_dict time is not initialized correctly, is: {api_dict.time}"
    assert api_dict["food"] == 4, f"Api_dict food is not initialized correctly, is: {api_dict.food}"
    assert api_dict["points"] == gs.points, f"Api route points: {api_dict.points} is not equal to gamestate points: {gs.points}"
    assert api_dict["time"] == gs.time, f"Api route time: {api_dict.time} is not equal to gamestate time: {gs.time}"
    assert api_dict["food"] == gs.food, f"Api route food: {api_dict.food} is not equal to gamestate food: {gs.food}"

def test_post_time_step_route(client):
    #Look for an increase in time by +1
    time = gs.time
    api_resp = client.post("/api/time-step", json = {})
    api_dict = api_resp.get_json()
    assert time == api_dict["time"] - 1, f"Time, which is {gs.time}, did not increase by 1"