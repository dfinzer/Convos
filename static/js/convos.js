var hasSetPollingInterval = false;
var pollingIntervalId;

// Google analytics.
if (isProductionEnvironment()) {
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-16848831-7']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
}

$(document).ready(function() {
  // Log home page visit.
  logVisitedPage("home");
});

function login() {
  $("#loader").show();
  $("#fb-login-box").hide();
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

// Switch to the page with the specified id.
function switchPage(pageId) {
  // Find visible page.
  $(".page.current-page").hide("slow", function() {
    $(this).removeClass("current-page");
    $("#" + pageId).show("slow", function() {
      $("#" + pageId).addClass("current-page");
      logVisitedPage(pageId);
    });
  });
}

function submitForm(url) {
  console.log($(".page.current-page").find(".form_text").val())
  data = {"form_text": $(".page.current-page").find(".form_text").val()}
  $.post(url, data, function() {
    // TODO: this is kinda ghetto.
    alert("Thanks for your feedback!");
  });
}