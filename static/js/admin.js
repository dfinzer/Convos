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

// Sends a message, as long as its a legal number.
function sendMessage(phoneNumber, twilioNumber, body) {
  // Make sure the phone number starts with the secret character.
  if (phoneNumber.indexOf("$") != 0) {
    alert("Illegal! You can only send messages from admin numbers.");
    return;
  }
  
  // Send the message.
  $.post("/api/message", {"From": phoneNumber, "To": twilioNumber, "Body": body}, function(response) {
    getMessages(phoneNumber, twilioNumber);
  });
}