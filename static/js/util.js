// Javascript utility functions.

function isProductionEnvironment() {
  return window.location.toString().indexOf('localhost') == -1;
}

function makeElement(className) {
  return $("." + className + ".template").clone().removeClass("template");
}

// Gets url parameters.
function getUrlValues() {
  var vars = [], hash;
  var hashes = window.location.href.slice(window.location.href.indexOf("?") + 1).split("&");
  for (var i = 0; i < hashes.length; i++) {
    hash = hashes[i].split('=');
    vars.push(hash[0]);
    vars[hash[0]] = hash[1];
  }
  return vars;
}