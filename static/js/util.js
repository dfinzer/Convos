// Javascript utility functions.

function isProductionEnvironment() {
  return window.location.toString().indexOf('localhost') == -1;
}

function makeElement(className) {
  return $("." + className + ".template").clone().removeClass("template");
}