function showMessage() {
    // get the message element
    var message = document.querySelector("#message");

    // show the message
    message.style.display = "block";

    // hide the message after 1 second
    setTimeout(function() {
      message.style.display = "none";
    }, 9000);
  }