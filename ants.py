"""Ants Vs. Bees (extension)"""

import random
import time
from ucb import main, interact, trace
from collections import OrderedDict
#from ants_engine import *
import ants_engine      # <-- if import just file, then use file name . class or function name (e.g. ants_engine.GameState())

from flask import Flask, jsonify, request, send_from_directory

import threading     # <-- NEW Sept 2, 2025: what does threading and threading.Lock() do? 

STATE_LOCK = threading.Lock()   # <-- Apurva: try to tell Oliver what this STATE_LOCK is doing. 

GAME_SECONDS = 3
LAST_TIME_AT = 0
INCLUDE_BEES = True   # <-- NEW Sept 2, 2025: If False = no bees in game, if True = bees in game 

"""
Sept 2, 2025 Updates by Oliver: 

- "serialize_place()" function in ants.py now processes any bee at each place if there is one 
- add "threading" library as an import (above)
- added example of thread locking to route '/api/state'
- added 'INCLUDE_BEES' global variable to decide if game should or should not have bees   

Sept 2025 Tasks for Apurva: 

1. In ants_engine.py, update "step_once()" function to implement Bee behavior AFTER ant actions.
2. Also in "step_once()" function, add something to update points for every time step.
    
    HINT: What is supposed to happen to points for each +1 of time in our game? Do you remember? 
    How would you make that happen in "step_once()" function? 

3. Look at lines 12 and 14 of ants.py (above) and the comments next to those lines of code. 
    
    Answer the question and attempt to tell Oliver what STATE_LOCK is doing. 

4. Add STATE_LOCK to each function and route that changes the game's state. 
    
    HINT: What object or class controls the state of the game? 
    HINT: See how I did this change in /api/state route if you need. 

5. Add a new route endpoint: '/api/remove' that can be used to remove an ant from a specific place. 

    HINT: Does this route / function get data or does it change / update data? Which method does which? 

6. Complete the new '/api/settings' route and function that Oliver started. 

    NOTE: This route can be used 2 different ways, to get setting values 
    and also to update setting values. 

    HINT: What are these 2 different ways that a route can be used called? 

"""

def game_step(): 
    global LAST_TIME_AT
    current_time = time.monotonic()

    #If not enough time has passed, exit without doing anything
    if (current_time-LAST_TIME_AT) < GAME_SECONDS:
        return False
    #If enough time has passed, step once through the game
    gs.step_once()
    LAST_TIME_AT = current_time
    return True

#--------------------------------------------------
# Make a sample gamestate instance 
#--------------------------------------------------

gs = ants_engine.GameState(
    strategy = ants_engine.interactive_strategy,
    beehive = ants_engine.Hive(ants_engine.make_normal_assault_plan()),
    ant_types = ants_engine.ant_types(),
    create_places = ants_engine.dry_layout,
    #dimensions=(3, 9),
    dimensions = (2,9), 
    food=2
)

gs_3_x_9 = ants_engine.GameState(
    strategy = ants_engine.interactive_strategy,
    beehive = ants_engine.Hive(ants_engine.make_normal_assault_plan()),
    ant_types = ants_engine.ant_types(),
    create_places = ants_engine.dry_layout,
    dimensions=(3, 9),
    #dimensions = (1, 1), 
    food=2
)

#--------------------------------------------------
# Utility functions: serialization  
#--------------------------------------------------
INSECT_IMGS = {
       'Worker': "assets/insects/ant_harvester.gif",
       'Thrower': "assets/insects/ant_thrower.gif",
       'Long': "assets/insects/ant_longthrower.gif",
       'Short': "assets/insects/ant_shortthrower.gif",
       'Harvester': "assets/insects/ant_harvester.gif",
       'Fire': "assets/insects/ant_fire.gif",
       'Bodyguard': "assets/insects/ant_bodyguard.gif",
       'Hungry': "assets/insects/ant_hungry.gif",
       'Slow': "assets/insects/ant_slow.gif",
       'Scary': "assets/insects/ant_scary.gif",
       'Laser': "assets/insects/ant_laser.gif",
       'Ninja': "assets/insects/ant_ninja.gif",
       'Wall': "assets/insects/ant_wall.gif",
       'Scuba': "assets/insects/ant_scuba.gif",
       'Queen': "assets/insects/ant_queen.gif",
       'Tank': "assets/insects/ant_tank.gif",
       'Bee': "assets/insects/bee.gif",
       'Remover': "assets/insects/remove.png",
}

def serialize_ant_types(ant_types):
    """Turn gs.ant_types OrderedDict(name→class) into a JSON Serializable list (i.e. list of dictionaries).
    
    In other words, this function just takes the ant_types of a gamestate instance and turns them into a bunch 
    of nested dictionaries so that they are able to be turned into JSON (i.e. Serialized)."""
    out = []
    for name, AntClass in ant_types.items():
        out.append({
            "name":      name,
            "cost":      AntClass.food_cost,
            # we will include images for each Ant later:
            "img":       INSECT_IMGS.get(name,"assets/insects/ant_harvester.gif")
        })
    return out

def serialize_places(places):
    """Turn gs.places into the { row: { col: cell_dict, … }, … } structure for JSON serialization.

    This function converts the game-state `places` mapping into a nested dictionary
    keyed by numeric row and col so the front-end can easily consume it.
    """
    grid = {}  # top-level dict: row index -> { col index -> cell dict }

    # Build entries from actual place objects present in `places`
    for place_name, place in places.items():
        # skip hive-like places (we don't render them on the main grid)
        if getattr(place, "is_hive", False):
            continue

        # place_name expected format: "<kind>_<row>_<col>", split into parts
        kind, row_s, col_s = place_name.split("_", 2)

        # convert row/col strings into integers for numeric keyss
        row = int(row_s)
        col = int(col_s)

        # create the minimal cell representation the frontend expects
        cell = {
            "name":    place_name,                                   # original place name (string)
            "type":    "water" if isinstance(place, ants_engine.Water) else "tunnel",  # place type
            "water":   1 if isinstance(place, ants_engine.Water) else 0,             # int flag for convenience
            "insects": {}                                           # placeholder for insect info (filled below)
        }

        # If an ant object is present on this place, pick an image for it
        ant_obj = getattr(place, "ant", None)   # get place.ant if it exists, else None
        if ant_obj is not None:
            # get the class name of the ant, e.g. "HarvesterAnt"
            ant_name = type(ant_obj).__name__

            # Try to find a matching sprite in INSECT_IMGS robustly:
            # 1) try the exact class name key
            # 2) try stripping a trailing "Ant" if present (HarvesterAnt -> Harvester)
            # 3) fallback to the "Harvester" key (or whatever default your mapping uses)
            sprite = INSECT_IMGS.get(ant_name)                            # try exact key
            if sprite is None:
                sprite = INSECT_IMGS.get(ant_name.replace("Ant", ""))     # try without "Ant"
            if sprite is None:
                sprite = INSECT_IMGS.get("Harvester")                    # fallback default key

            # Place the chosen image path (or value) into the cell under insects.img
            # NOTE: keep the same format your front-end expects (string path or url).
            cell["insects"] = {"img": sprite}

        # count how many bees are physically present on this place at this time step:
        bee_list = getattr(place, "bees", [])

        if bee_list:
            cell["bees"] = {
                "count" : len(bee_list),
                "img": INSECT_IMGS.get("Bee")
            }

        # Insert this cell into the grid at the numeric row/col location
        # Use setdefault so the row dict exists (or is created) before assigning the column.
        grid.setdefault(row, {})[col] = cell

    # Ensure the returned grid has entries for ALL rows and cols as defined by gs.dimensions
    rows, cols = gs.dimensions
    for r in range(rows):
        # create the row dict if missing
        grid.setdefault(r, {})
        for c in range(cols):
            # for any missing cell (no actual place object), insert a default empty tunnel cell
            grid[r].setdefault(c, {
                "name":    f"tunnel_{r}_{c}",
                "type":    "tunnel",
                "water":   0,
                "insects": {}
            })

    # return the fully-populated nested dict
    return grid




#--------------------------------------------------
# Begin tiny REST api via Flask  
#--------------------------------------------------
app = Flask(__name__,
            static_url_path="/", #This makes it so that the / route will go to gui.html
            static_folder="static" #This says to serve the site from the folder called static
            )

# TASK 1: How should the following route be changed to use the gamestate instance? 
# 
@app.route('/api/state')
def api_state():
    """
    Can use this route to check values in game engine. 

    In Terminal, execute with: 

    curl localhost:5000/api/state
    """

    # If we are changing anything in the game, we need to lock it (...why??)
    with STATE_LOCK:
        # HINT: nothing else can change the values in gs until this function finishes. 

        # Print out what the results of serialize_places or serialize_ant_types is here (before and after).
        #print (f"places: {gs.places}")
        #print (f"{serialize_places(gs.places)}")
        return jsonify({
            'status' : 'ok',
            'time'   : gs.time,
            'food'   : gs.food,
            'points' : gs.points,
            'rows' : gs.dimensions[0],
            'ant_types' : serialize_ant_types(gs.ant_types),
            'places' : serialize_places(gs.places)
        })

@app.route('/api/points')
def api_points():
    """
    Can use this route to check point value in game engine. 

    In Terminal, execute with: 

    curl localhost:5000/api/points
    """
    with STATE_LOCK:
        return jsonify({
            'points' : gs.points    # Task 2: ...and this one? 
        })

# Task 3: How should this route be changed to use gamestate and correctly step through time? 
# 
@app.route('/api/time-step', methods = ["POST"])
def api_time_step():
    """
    Can use this route to make the game engine increment +1 time. 

    In Terminal, excute this route with:

    curl -XPOST localhost:5000/api/time-step 
    """
    with STATE_LOCK:
        did_game_step = game_step()
        return jsonify({
            'time' : gs.time  ,
            'did_game_step' : did_game_step
        })

@app.route('/api/food-increase', methods = ["POST"])
def api_food_increase():
    """
    Can use this route to make the game engine increment +1 food. 

    In Terminal, excute this route with:

    curl -XPOST localhost:5000/api/food-increase
    """
    with STATE_LOCK:
        gs.food += 1
        return jsonify({
            'food' : gs.food    
        })
    
@app.route('/api/remove', methods=['POST'])
def api_remove():
    """
    Removes an ant at a specific place.
    Can use this route to test game engine directly or with Flask.

    Via Terminal, call with:
    #############################################################
    curl -XPOST -H "Content-Type: application/json" \
        -d '{"place" : "tunnel_0_0", "ant" : "Thrower"}' \
        localhost:5000/api/remove
    """
    with STATE_LOCK:
        data = request.get_json()
        place_name = data['place']
        ant_type   = data['ant']
        try:
            new_ant = gs.remove_ant(place_name, ant_type)
            return jsonify({ 'status': 'ok'})
        except Exception as e:
            # If error -> below is thrown 
            return jsonify({ 'status': 'error', 'message': str(e) }), 400

@app.route('/api/deploy', methods=['POST'])
def api_deploy():
    """
    Deploys an ant at a specific place.
    Can use this route to test game engine directly or with Flask.

    Via Terminal, call with:
    #############################################################
    curl -XPOST -H "Content-Type: application/json" \
        -d '{"place" : "tunnel_0_0", "ant" : "Thrower"}' \
        http://localhost:5000/api/deploy
    """
    with STATE_LOCK:
        data = request.get_json()
        place_name = data['place']
        ant_type   = data['ant']
        try:
            new_ant = gs.deploy_ant(place_name, ant_type)
            return jsonify({ 'status': 'ok', 'ant_id': new_ant.id, 'instance_id': id(new_ant) })
        except Exception as e:
            # If error -> below is thrown 
            return jsonify({ 'status': 'error', 'message': str(e) }), 400
    
@app.route('/api/new-game', methods = ["POST"])
def api_new_game():
    """
    Can use this route to make the game restart and start a new one. 

    In Terminal, excute this route with:

    curl -XPOST localhost:5000/api/new-game
    """
    with STATE_LOCK:
        global gs
        gs = ants_engine.GameState(
                strategy = ants_engine.interactive_strategy,
                beehive = ants_engine.Hive(ants_engine.make_normal_assault_plan()),
                ant_types = ants_engine.ant_types(),
                create_places = ants_engine.dry_layout,
                dimensions = (2,9), 
                food=2
        )
        print ("[/new-game]Started new gamestate")
        return jsonify({ 'status': 'ok'})

# NEW Sept 2, 2025: Route to either get or update game runtime settings. 
@app.route('/api/settings', methods = ["POST","GET"])  # <-- WHAT GOES HERE? 
def api_settings():
    """
    This Route can be used to either get or update the settigs, including: 

    - GAME_SECONDS --> the number of real seconds for every game time +1)
    - INCLUDE_BEES --> True or False, to include bees in game or not 

    NOTE: since we can change GAME_SECONDS from this function, we also 
    need to reset LAST_TIME_AT variable back to 0. 
    """
    global GAME_SECONDS, INCLUDE_BEES, LAST_TIME_AT
    with STATE_LOCK:

        if request.method == "GET":  # <-- WHAT GOES HERE? 
            # just return the current settings of the game
            return jsonify({
                "game_seconds": GAME_SECONDS,
                "include_bees": INCLUDE_BEES   
            })
        
        elif request.method == "POST":
            # this is the method where we update data! 

            data = request.get_json() or {}

            if 'game_seconds' in data:
                # Give 'GAME_SECONDS' global new value 
                GAME_SECONDS = int(data['game_seconds'])     # WHAT GOES HERE? HINT: look at how I did it below for INCLUDE_BEES. 

                # we also have to reset LAST_TIME_AT if we change GAME_SECONDS value: 
                LAST_TIME_AT = 0 
            
            if 'include_bees' in data: 
                # If the request has 'include_bees' then set INCLUDE_BEES to that boolean value. 
                # 0 is false, 1 is true 
                INCLUDE_BEES = bool(data['include_bees'])

            # return the updated settings
            return jsonify({
                "game_seconds": GAME_SECONDS,
                "include_bees": INCLUDE_BEES 
            })

        else: 
            # This else should NOT be reached. It means there was an error! 
            print(f"[ants.py | api_settings()] Error! request.method: {request.method}, request.get_json(): {request.get_json()}")
            return False 

# NOTE: check very end of this file for last additional change!
# --- END API hooks ---------

# Route to serve the main site
@app.route("/")
def index():
    #return send_from_directory("static", "gui.html")
    return app.send_static_file('gui.html')

# * Last change added to setup basic Flask api endpoint routing * 
if __name__ == '__main__':
    app.run(debug = True)