function login() {
  $.post("/login", {}, function(response) {
    data = $.parseJSON(response);
    console.log(data)
    if (data.status == "pending") {
      $("#verification-code").text(data.verification_code)
    }
  });
}