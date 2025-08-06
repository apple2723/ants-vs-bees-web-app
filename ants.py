"""Ants Vs. Bees (extension)"""

import random
from ucb import main, interact, trace
from collections import OrderedDict
#from ants_engine import *
import ants_engine      # <-- if import just file, then use file name . class or function name (e.g. ants_engine.GameState())

from flask import Flask, jsonify, request, send_from_directory

#--------------------------------------------------
# Make a sample gamestate instance 
#--------------------------------------------------
gs = ants_engine.GameState(
    strategy = ants_engine.interactive_strategy,
    beehive = ants_engine.Hive(ants_engine.make_normal_assault_plan()),
    ant_types = ants_engine.ant_types(),
    create_places = ants_engine.dry_layout,
    dimensions=(3, 9),
    food=4
)

#--------------------------------------------------
# Begin tiny REST api via Flask  
#--------------------------------------------------
app = Flask(__name__,
            static_url_path="", #This makes it so that the / route will go to gui.html
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
    return jsonify({
        'status' : 'ok',
        'time'   : gs.time,
        'food'   : gs.food,
        'points' : gs.points    
    })

@app.route('/api/points')
def api_points():
    """
    Can use this route to check point value in game engine. 

    In Terminal, execute with: 

    curl localhost:5000/api/points
    """
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
    gs.time += 1
    return jsonify({
        'time' : gs.time    
    })

@app.route('/api/food-increase', methods = ["POST"])
def api_food_increase():
    """
    Can use this route to make the game engine increment +1 food. 

    In Terminal, excute this route with:

    curl -XPOST localhost:5000/api/food-increase
    """
    gs.food += 1
    return jsonify({
        'food' : gs.food    
    })

@app.route('/api/deploy', methods=['POST'])
def api_deploy():
    """
    Can use this route to test game engine directly or with Flask.

    Via Terminal, call with:
    #############################################################
    curl -XPOST -H "Content-Type: application/json" \
        -d '{"place" : "tunnel_0_0", "ant" : "Thrower"}' \
        http://localhost:5000/api/deploy
    """
    data = request.get_json()
    place_name = data['place']
    ant_type   = data['ant']
    try:
        new_ant = gs.deploy_ant(place_name, ant_type)
        return jsonify({ 'status': 'ok', 'ant_id': new_ant.id, 'instance_id': id(new_ant) })
    except Exception as e:
        # If error -> below is thrown 
        return jsonify({ 'status': 'error', 'message': str(e) }), 400

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