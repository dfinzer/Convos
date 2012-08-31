// Javascript utility functions.

function isProductionEnvironment() {
  return window.location.toString().indexOf('localhost') == -1;
}