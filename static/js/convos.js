function login() {
  $.post("/login", {}, function(response) {
    data = $.parseJSON(response);
    console.log(data)
  });
}

function logout() {
  // TODO: implement.
}