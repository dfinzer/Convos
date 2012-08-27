function login() {
  $.post("/login", {}, function(response) {
    data = $.parseJSON(response);
    if (data.status == "pending") {
      $("#verification-code").text(data.verification_code)
    }
  });
}