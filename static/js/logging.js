function logClickedFacebookLogin() {
  $.post("/api/log_clicked_facebook_login", {},
    function(response) {});
}

function logVisitedPage(name) {
  $.post("/api/log_visited_page", {"name": name},
    function(response) {});
}