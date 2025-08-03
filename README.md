# Ants vs Bees Game 

[![ci](https://github.com/apple2723/ants-vs-bees-web-app/actions/workflows/ci.yml/badge.svg)](https://github.com/apple2723/ants-vs-bees-web-app/actions)

This web-based game is an extension of the original **Ants vs Some Bees** game that is taught as a project in UC Berkeley's C88C / CS61 course; Data Structures.

Our app extends the functionality of the original game with some major changes. 

<br>

## Tests

To run tests on this program, we use PyTest based unit testing.

Current Tests:
- test_core_ant.py
- test_gamestate.py

### To run tests from terminal

> pytest

<br>

## Roadmap of Development (Extensions) 

After taking the completed game from the project description, our app implements the following steps: 

### 1. Version Control with Git and Github 

This is not so much shown in the code but will be reflected in how we interact with the app. 

<hr>

### 2. Automated Testing with PyTest 

- add **tests/** directory for all test files 
- include **PyTest** in the *requirements.txt* file 
- write unit tests for core game behavior 

Tests are easily extensible and modularized. 

<hr>

### 3. Continuous Integration (CI) 

We will set up **Github Actions** so that every push to the project repo automatically runs the entire folder of tests and gives a pass or fail report. 

<hr>

### 4. Scoring System 

- add scoring system to **GameState** class 
- add points for killing bees, subtract points for time, subtract points for bees killing ants 
- update score each turn 
- write tests to test our scoring works / changes 

<hr>

### 5. Front-end Development with Flask 

Game is already Flask based but we will work on extending the functionality of Flask. 

- add form for user to pick difficulty of the game before game starts 
- change Flask routes so that there are multiple routes to go to / from 

<hr>

### 6. (Optional) Advanced Web Framework 

Generally, Flask-based web apps are usually only used for tutorials and toy examples. Flask is very lightweight and, thus, very limited in what can 
integrate with it and its functionality. Most production web apps in Python do **NOT** use Flask. 

We can swap out Flask and use a more advanced and powerful web framework, *e.g.* **FastAPI** *or* **Django** 

<hr>

### 7. User Accounts and Login (SQL / Databases) 

- add user signup and login flows 
- create a **postgres** (*i.e. PostgreSQL*) database 
- store user profiles / accounts, scores, and game settings in the database 

<hr>

### 8. (Optional) Extend Game 

- create improved graphics / visuals for the game 
- create more types of ants and / or bees 
- implement power-ups 
- create levels of the game 


<hr>

### 9. Deployment 

Nearly all production level applications, including practically all company websites and apps that people use on a daily basis, run in the cloud 
from **Docker containers.**

The **cloud** is just a network of computers (*i.e. server*) that you connect to virtually and can run code on, instead of running the code on your own machine. 

**Docker** is an extremely popular containerization software. It is somewhat similar to creating a virtual environment 

