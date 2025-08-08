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
// 3) UI update functions 

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
  console.log("[app.js] in drawControlPanel function");
  var tr = $('#antsTableRow').empty();

  if (!Array.isArray(antTypes)) {
    console.warn("antTypes missing/invalid; skipping panel draw");
    return;
  }

  // If this function is running, then why do we not see the game board? 

  antTypes.forEach(function(ant) {
    var img = ant.img || '/assets/insects/placeholder.png'; // fallback
    var td = $('<td>')
      .data("name",     ant.name)
      .data("cost",     ant.cost)
      .data("img",      img)          
      .data("disabled", ant.cost > food ? 1 : 0)
      .addClass( ant.cost > food ? "ant-row ant-inactive" : "ant-row" )
      .attr("id", "ant_" + ant.name)
      .append('<img class="ant-img" src="' + ant.img + '"> ')
      .append(ant.name)
      .append('<hr class="ant-row-divider">')
      .append('<span class="badge ant-cost">' + ant.cost + '</span>');
    tr.append(td);
  });
  console.log("[app.js] at end of drawControlPanel function");
}

// Draw the initial tunnel/grid
function drawInitialPlaces(places, rows) {
  console.log("[app.js] in drawInitialPlaces function");
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
      console.log("[app.js] at end of drawControlPanel function");
    });
    // beehive in column r=0 only
    if (r === 0) {
      var hiveTd = $('<td rowspan="' + rows + '" class="place-beehive-td">');
      tr.append(hiveTd);
    }
    pTable.append(tr);
  }
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

$(function () {
  /*fetchState().done(function (state) {
    console.log("[/api/state] initial:", state);

    gui.food     = state.food ?? 0;
    gui.time     = state.time ?? 0;
    gui.points   = state.points ?? 0;
    gui.rows     = state.rows ?? 0;
    gui.antTypes = Array.isArray(state.ant_types) ? state.ant_types : [];
    gui.places   = state.places ?? {};

    drawControlPanel(gui.food, gui.antTypes);
    drawInitialPlaces(gui.places, gui.rows);
    updateFoodCount();
    updateTimeCount();
    updatePointsCount();
  }).fail(function (xhr) {
    console.error("Failed to load state:", xhr.status, xhr.responseText);
    alert("Failed to load /api/state. Check Flask console for errors.");
  });*/

  // 2) Poll every half second
  setInterval(function () {
    if (!$('#gameWrapper').is(':visible')) return; // guard: only run when game is visible! 
    fetchState().done(function (state) {
      gui.food   = state.food ?? gui.food;
      gui.time   = state.time ?? gui.time;
      gui.points = state.points ?? gui.points;
      gui.places = state.places ?? gui.places;

      updateFoodCount();
      updateTimeCount();
      updatePointsCount();
      updateControlPanel();
      updatePlacesAndBees(gui.places);
    });
  }, 500);
});

function updatePlacesAndBees(places) {
  // Minimal: if a cell reports an ant image, render it
  console.log("[app.js] in updatePlacesAndBees function");
  for (var r in places) {
    console.log("[app.js] in updatePlacesAndBees function(first for)");
    if (!places.hasOwnProperty(r)) continue;
    for (var c in places[r]) {
      console.log("[app.js] in updatePlacesAndBees function(second for)");
      if (!places[r].hasOwnProperty(c)) continue;
      var cell = places[r][c];
      var $td = $('.places-td[data-row="' + r + '"][data-col="' + c + '"] .tunnel-img-container');
      console.log("[app.js] in updatePlacesAndBees function, cell: ", cell);
      if (cell.insects && cell.insects.img) {
        console.log("[app.js] in updatePlacesAndBees function(innermost if loop)");
        // Single ant MVP (container/contained can come later)
        var html = '<img class="active-ant" src="' + cell.insects.img + '">';
        $td.html(html);
        console.log("[app.js] in updatePlacesAndBees function(innermost if loop after setting html)");
      } else {
        $td.empty();
      }
    }
  }
  console.log("[app.js] at end of updatePlacesAndBees function");
}


// ——————————————————————————————
// PLAY THE GAME: button event handler and start game

function startGame() {
  return $.ajax({ url: "/api/new-game", method: "POST" });
}

$('#playBtn').on('click', function () {
  console.log('[ui] Play clicked');
  $('#hero-head').hide();
  $('#gameWrapper').show();

  startGame().always(function () {
    // First draw after a fresh state
    fetchState().done(applyStateAndDraw)
                .fail(showStateError);
  });
});

function applyStateAndDraw(state) {
  console.log("[app.js] in applyStateAndDraw function");
  gui.food     = state.food ?? 0;
  gui.time     = state.time ?? 0;
  gui.points   = state.points ?? 0;
  gui.rows     = state.rows ?? 0;
  gui.antTypes = Array.isArray(state.ant_types) ? state.ant_types : [];
  gui.places   = state.places ?? {};

  drawControlPanel(gui.food, gui.antTypes);
  drawInitialPlaces(gui.places, gui.rows);
  updateFoodCount(); updateTimeCount(); updatePointsCount();
}

function showStateError(xhr) {
  console.error("Failed to load state:", xhr.status, xhr.responseText);
  alert("Failed to load /api/state. Check Flask console for errors.");
}

// EXIT BUTTON: start new-game 

$('#exitBtn').on('click', function () {
  $.post('/api/new-game').always(function () {
    $('#gameWrapper').hide();
    $('#hero-head').show();
  });
});