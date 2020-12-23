/* Collections A-Z Javascript */
$(document).ready(function() {
    // Get an array of the characters from A - Z
    var abcChars = Array.apply(null, {length: 26}).map((x, i) => String.fromCharCode(65+i));

    // Giroup collections by their first letter
    var abcColls = {}
    $.each(collections, function(index, value) {
        if (!(value.charAt(0) in abcColls)) {
            abcColls[value.charAt(0)] = [];
        }
        abcColls[value.charAt(0)].push(value);
    });

    // Build the top navigation bar
    $.each(abcChars, function(index, value) {
        if (value in abcColls){
            $('#az-list').append("<li class='page-item'><a class='page-link' href='#" + value + "'>" + value + "</a></li>");
        } else {
            $('#az-list').append("<li class='page-item disabled'><a class='page-link' href='#'>" + value + "</a></li>");
        }
    });

});
