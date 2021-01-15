/* Scroll to the top of the page Javascript 
 * requires: a button with a class of "top"
 * */

$(document).ready(function() {

    // When the user scrolls down 20px from the top of the document, show the button
    window.onscroll = function() {scrollFunction()};
});

function scrollFunction() {
  var scrollBtn = document.getElementById("top");
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    scrollBtn.style.display = "block";
  } else {
    scrollBtn.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
function topFunction() {
  var scrollBtn = document.getElementById("top");
  document.body.scrollTop = 0;
  document.documentElement.scrollTop = 0;
}
