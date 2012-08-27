function login() {
  $.post("/login", {}, function(response) {
    console.log(response);
  });
}

function logout() {
  // TODO: implement.
}