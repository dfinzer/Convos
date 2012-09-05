var DEV_APP_ID = '415440758502999';
var PRODUCTION_APP_ID = '326547147430900';

function facebookLogin() {
  logClickedFacebookLogin();
  FB.login(function(response) { },
    {scope:'email,user_location,user_birthday,user_education_history,user_likes,user_relationship_details'});
}

function facebookLogout() {
  FB.logout(function(response) { });
}

function showLoginButton() {
  $("#fb-login").unbind("click");
  $("#fb-login").click(function() {
    facebookLogin();
  });
}

function handleResponse(response) {
  if (response.authResponse) {
    login();
  } else {
    showLoginButton();
  }
}

// Set up Facebook Javascript SDK.
window.fbAsyncInit = function() {
  // Configure App ID based on production vs. dev.
  if(isProductionEnvironment()) {
    appId = PRODUCTION_APP_ID;
	} else {
		appId = DEV_APP_ID;
	}
	
  FB.init({ appId: appId, 
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
