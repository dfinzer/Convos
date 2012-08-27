var APP_ID = '326547147430900';

function facebookLogin() {
  FB.login(function(response) {
    handleResponse(response);
  }, {scope:'email'});
}

function facebookLogout() {
  FB.logout(function(response) {
    logout();
  });
}

function showLoginButton() {
  $("#fb-login").unbind("click");
  $("#fb-login").text("Login with Facebook")
  $("#fb-login").click(function() {
    facebookLogin();
  });
}

function handleResponse(response) {
  if (response.authResponse) {
    $("#fb-login").unbind("click");
    $("#fb-login").text("Logout")
    $("#fb-login").click(facebookLogout);
    login();
  } else {
    showLoginButton();
  }
}

// Set up Facebook Javascript SDK.
window.fbAsyncInit = function() {
  FB.init({ appId: APP_ID, 
	    status: true, 
	    cookie: true,
	    xfbml: true,
	    oauth: true });
	    
  // Run once with current status and whenever the status changes.
  FB.getLoginStatus(handleResponse);
  FB.Event.subscribe('auth.statusChange', handleResponse);	
};
	
(function() {
  var e = document.createElement('script'); e.async = true;
  e.src = document.location.protocol 
    + '//connect.facebook.net/en_US/all.js';
  document.getElementById('fb-root').appendChild(e);
}());