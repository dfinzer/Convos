var hasSetPollingInterval = false;
var pollingIntervalId;

function login() {
  $("#loader").show();
  $("#fb-login").hide();
  $.post("/api/login", {}, function(response) {
    data = $.parseJSON(response);
    if (data.status == "pending") {
      $("#verification-code").text(data.verification_code)
      $("#verification-code-box").fadeIn("slow");
      
      // Poll for the user's registration status, so we can auto-update the page.
      if (!hasSetPollingInterval) {
        pollingIntervalId = setInterval(pollRegistrationStatus, 1000);
        hasSetPollingInterval = true;
      }
    } else if (data.status == "registered") {
      showGetStartedBox();
    }
    $("#loader").hide();
  }).error(function() {
    showErrorBox();
  });
}

function showErrorBox() {
  $("#error-box").show();
  $("#loader").hide();
  $("#verification-code-box").hide();
}

function showGetStartedBox() {
  $("#verification-code-box").hide();
  $("#get-started-box").fadeIn("slow");
  clearInterval(pollingIntervalId)
}

function pollRegistrationStatus() {
  $.get("/api/registration_status", {}, function(response) {
    data = $.parseJSON(response);
    if (data.status == "registered") {
      showGetStartedBox();
    }
  }).error(function() {
    showErrorBox();
    clearInterval(pollingIntervalId)
  });
}

function switchPage(pageId) {
  // Find visible page.
  $(".page.current-page").hide("slow", function() {
    $(this).removeClass("current-page");
    $("#" + pageId).show("slow", function() {
      $("#" + pageId).addClass("current-page");
    });
  });
}