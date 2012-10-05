$(document).ready(function() {
  // Set up forms for sending and getting messages.
  $("#get_messages").click(function() {
    var phoneNumber = $("#phone_number").val();
    var twilioNumber = $("#twilio_number").val();
    getMessages(phoneNumber, twilioNumber);
  });
  $("#send_message").click(function() {
    var phoneNumber = $("#phone_number").val();
    var twilioNumber = $("#twilio_number").val();
    var body = $("#body").val();
    sendMessage(phoneNumber, twilioNumber, body);
  });
  $("#get_conversations").click(function() {
    var userId = $("#user_id").val()
    getConversations(userId);
  });
});

// Fetches messages for the specified phone number and twilio number combo.
function getMessages(phoneNumber, twilioNumber) {
  $("#messages").html("");
  $.getJSON("/api/admin/get_messages", {"phone_number": phoneNumber, "twilio_number": twilioNumber}, 
    function(messages) {
      for (i in messages) {
        var message = messages[i];
        messageDiv = makeElement("message");
        messageDiv.find(".to").text(message.outbound == 0 ? "Me: " : "Them: ");
        messageDiv.find(".body").text(message.body);
        $("#messages").append(messageDiv);
      }
  });
}

function getConversations(userId) {
  $("#conversations").html("");
  $.getJSON("/api/admin/get_conversations", {"user_id": userId}, 
    function(conversations) {
      for (i in conversations) {
        var conversation = conversations[i];
        conversationDiv = makeElement("conversation");
        conversationDiv.find(".user_one").text(conversation["name"]);
        conversationDiv.find(".user_two").text(conversation["user_two.name"]);
        conversationDiv.find(".in_progress").text(conversation["in_progress"]);
        $("#conversations").append(conversationDiv);
      }
  });
}

// Sends a message, as long as its a legal number.
function sendMessage(phoneNumber, twilioNumber, body) {
  // Send the message.
  $.post("/api/message", {"From": phoneNumber, "To": twilioNumber, "Body": body}, function(response) {
    getMessages(phoneNumber, twilioNumber);
  });
}

function login() {
  $("#fb-login-box").hide();
  $("#loader").show();
  $.post("/api/login", {}, function(response) {    
    data = $.parseJSON(response);
    $("#loader").hide();
  }).error(function() {
    showErrorBox();
  });
}