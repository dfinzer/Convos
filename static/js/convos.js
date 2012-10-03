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
  
  // Set up auto-selection of the next field for phone input.
  $(".phone-input").keyup(function() {
     if(this.value.length == $(this).attr('maxlength')) {
         $(this).next(".phone-input").focus();
     }
   });
   
   $("#phone-submit").unbind("click");
   $("#phone-submit").click(function() {
     submitPhoneNumber();
   });
});

function showMoreHints() {
  $("#more_hints").show("slow");
}

function login() {
  $("#loader").show();
  $("#fb-login-box").hide();
  $("#description").hide();
  
  // Get the verification code from the url.
  code = getUrlValues()["code"];
  $.post("/api/login", {"code": code}, function(response) {    
    var data = $.parseJSON(response);
    if (data.status == "pending") {
      $("#phone-number-box").fadeIn("slow");
      $(".phone-input:first").select();
    } else if (data.status == "registered") {
      showGetStartedBox();
    }
    $("#loader").hide();
  }).error(function() {
    showErrorBox();
  });
}

function submitPhoneNumber() {
  var phoneDigits = $(".phone-input:first").val()
    + $(".phone-input-second:first").val()
    + $(".phone-input:last").val()
  var phoneNumber = "+1" + phoneDigits;
  var isValid = true;
  
  // If it's valid, go ahead and register.
  if (isValid) {
    $("#loader").show();
    $("#phone-number-box").hide();
    $("#phone-number-error").hide();
    $.post("/api/register_phone_number", {"phone_number": phoneNumber}, function(response) {
      $("#loader").hide();
      var data = $.parseJSON(response);
      if (data.status == "registered") {
        showGetStartedBox();
      } else if (data.status == "error") {
        showErrorBox();
      }
    }).error(function() {
        showErrorBox();
    });
  // Otherwise display the error.
  } else {
    $("#phone-number-error").text(error);
    $("#phone-number-error").show();
  }
}

function showErrorBox() {
  $("#error-box").show();
  $("#loader").hide();
  $("#phone-number-box").hide();
}

function showGetStartedBox() {
  $("#phone-number-box").hide();
  $("#get-started-box").fadeIn("slow");
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
  data = {"form_text": $(".page.current-page").find(".form_text").val()}
  $.post(url, data, function() {
    // TODO: this is kinda ghetto.
    alert("Thanks for your feedback!");
  });
}