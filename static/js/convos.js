function login() {
  $("#loader").show();
  $("#fb-login").hide();
  $.post("/login", {}, function(response) {
    data = $.parseJSON(response);
    if (data.status == "pending") {
      $("#verification-code").text("#" + data.verification_code)
      $("#verification-code-box").fadeIn("slow");
    } else {
      $("#fb-login").show();
    }
    $("#loader").hide();
  });
}