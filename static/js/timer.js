var Stopwatch = function(elem, options) {
  
  var timer       = createTimer(),
      startButton = createButton("start", start),
      stopButton  = createButton("stop", stop),
      resetButton = createButton("reset", reset),
      offset,
      clock,
      interval;


  // default options
  options = options || {};
  //options.delay = options.delay || 1;
  options.delay = 1000
 
  // append elements     
  elem.appendChild(timer);
  /*
  elem.appendChild(startButton);
  elem.appendChild(stopButton);
  elem.appendChild(resetButton);
  */
  
  // initialize
  reset();
  
  // private functions
  function createTimer() {
    return document.createElement("span");
  }
  
  function createButton(action, handler) {
    var a = document.getElementById(action)
    a.href = "#" + action;
    a.innerHTML = action;

    a.addEventListener("click", function(event) {
      handler();
      event.preventDefault();
    });
    return a;
  }
  
  function start() {
    if (!interval) {
      offset   = Date.now();
      interval = setInterval(update, options.delay);
    }
  }
  
  function stop() {
    if (interval) {
      clearInterval(interval);
      interval = null;
    }
  }
  
  function reset() {
    clock = 0;
    render(0);
  }
  
  function update() {
    clock += delta();
    render();
  }
  
  function render() {

    var seconds = Math.round(clock/1000);
    var hours = Math.floor(seconds / 3600);
    seconds = seconds % 3600;
    var minutes = Math.floor(seconds / 60);
    seconds = seconds % 60;

    var str = "".concat(hours.toString(), ":", minutes.toString(), ":", seconds.toString());


    timer.innerHTML = str;


  }
  
  function delta() {
    var now = Date.now(),
        d   = now - offset;
    
    offset = now;
    return d;
  }
  
  // public API
  this.start  = start;
  this.stop   = stop;
  this.reset  = reset;
};



window.onload = function()
{
  // Make sure we don't reset the timer if we refresh the page
  var a = document.getElementById("timer");
  aTimer = new Stopwatch(a);

}
