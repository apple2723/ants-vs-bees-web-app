// static/app.js
// ——————————————————————————————
// 1) Global “GUI” state
var gui = {
  food:       0,
  time:       0,
  points:     0,
  rows:       0,
  antTypes:   [],    // [{ name, cost, img }, …]
  places:     {},    // { row: { col: { name, type, water, insects }, … }, … }
  selectedAnt: null
};

// Turn off caching so we always get fresh JSON
$.ajaxSetup({ cache: false });

// ——————————————————————————————
// 2) AJAX helpers for our new Flask API

// GET /api/state → { time, food, points, rows, ant_types, places }
function fetchState() {
  return $.ajax({
    url: "/api/state",
    method: "GET",
    dataType: "json"
  });
}

// POST /api/deploy { place, ant } → { status, ant_id } or HTTP 400 + { message }
function deployAnt(place, antName) {
  return $.ajax({
    url: "/api/deploy",
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ place: place, ant: antName })
  });
}

// POST /api/time-step → { time }
function timeStep() {
  return $.ajax({
    url: "/api/time-step",
    method: "POST",
    dataType: "json"
  });
}

// ——————————————————————————————
// 3) UI update functions (unchanged from before except using gui.*)

// Update the little “Food : X” badge
function updateFoodCount() {
  $('#foodCount').text(gui.food);
}

// Update the little “Time : Y” badge
function updateTimeCount() {
  $('#timeCount').text(gui.time);
}

// Update the new “Points : Z” badge
function updatePointsCount() {
  $('#pointsCount').text(gui.points);
}

// Enable/disable ant buttons
function updateControlPanel() {
  $('#antsTableRow td').each(function() {
    var cost     = +$(this).data("cost"),
        disabled = $(this).data("disabled");
    if (disabled && gui.food >= cost) {
      $(this).data("disabled", 0).removeClass("ant-inactive");
    } else if (!disabled && gui.food < cost) {
      $(this).data("disabled", 1).addClass("ant-inactive");
    }
  });
}

// Draw the ant‐selection panel
function drawControlPanel(food, antTypes) {
  var tr = $('#antsTableRow').empty();
  antTypes.forEach(function(ant) {
    var td = $('<td>')
      .data("name",     ant.name)
      .data("cost",     ant.cost)
      .data("disabled", ant.cost > food ? 1 : 0)
      .addClass( ant.cost > food ? "ant-row ant-inactive" : "ant-row" )
      .attr("id", "ant_" + ant.name)
      .append('<img class="ant-img" src="' + ant.img + '"> ')
      .append(ant.name)
      .append('<hr class="ant-row-divider">')
      .append('<span class="badge ant-cost">' + ant.cost + '</span>');
    tr.append(td);
  });
}

// Draw the initial tunnel/grid
function drawInitialPlaces(places, rows) {
  var pTable = $('.places-table').empty();
  for (var r = 0; r < rows; r++) {
    var tr = $('<tr id="pRow' + r + '">');
    Object.keys(places[r]).forEach(function(c) {
      var cell = places[r][c],
          td   = $('<td>')
            .data("row",   r)
            .data("col",   c)
            .data("name",  cell.name)
            .addClass("places-td")
            .append('<div class="tunnel-div"><div class="tunnel-img-container"></div></div>');
      tr.append(td);
    });
    // beehive in column r=0 only
    if (r === 0) {
      var hiveTd = $('<td rowspan="' + rows + '" class="place-beehive-td">');
      tr.append(hiveTd);
    }
    pTable.append(tr);
  }
}

// Move bees & animate removals (same logic as before)
function updatePlacesAndBees(places) {
  // …copy in your old moveBees() and removeAnts() code here…
}

// ——————————————————————————————
// 4) Wire up clicks

// Select an ant type
$('#antsTableRow').on('click', '.ant-row', function() {
  if ($(this).data("disabled")) return;
  $('#antsTableRow .ant-selected').removeClass("ant-selected");
  $(this).addClass("ant-selected");
  gui.selectedAnt = {
    name: $(this).data("name"),
    img:  $(this).data("img")
  };
});

// Deploy on tunnel click
$('.places-table').on('click', '.places-td', function() {
  if (!gui.selectedAnt) {
    alert("Please select an ant first!");
    return;
  }
  var place = $(this).data("name");
  deployAnt(place, gui.selectedAnt.name)
    .fail(function(xhr) {
      alert(xhr.responseJSON.message);
    });
});

// ——————————————————————————————
// 5) Kick off the loop

$(function() {
  // 1) Initial draw
  fetchState().done(function(state) {
    gui.food     = state.food;
    gui.time     = state.time;
    gui.points   = state.points;
    gui.rows     = state.rows;
    gui.antTypes = state.ant_types;
    gui.places   = state.places;

    drawControlPanel(gui.food, gui.antTypes);
    drawInitialPlaces(gui.places, gui.rows);
    updateFoodCount();
    updateTimeCount();
    updatePointsCount();
  });

  // 2) Poll every half‐second
  setInterval(function() {
    fetchState().done(function(state) {
      gui.food   = state.food;
      gui.time   = state.time;
      gui.points = state.points;
      gui.places = state.places;

      updateFoodCount();
      updateTimeCount();
      updatePointsCount();
      updateControlPanel();
      updatePlacesAndBees(gui.places);
    });
  }, 500);
});
