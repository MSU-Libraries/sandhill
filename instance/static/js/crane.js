/* Crane Javascript */

/* General Utilities */

/* Given the ID of an elemnt on the page, it will copy 
 * it's value into the client's clipboard 
 * ex:
 *    <div id="my_field">Some text</div>
 *    <div class="copyOnClick" data-copytarget="#my_field"></div>  */
$(document).ready(function() {
    $(".copy-on-click").on("click", function() {
        var field_name = $(this).data("copytarget");
        var copy_elem = $(field_name);

        /* Get the value to be copied */
        const el = document.createElement('textarea');
        el.value = $(field_name).val();
        if (el.value == ""){
            el.value = $(field_name).text();
        }

        el.setAttribute('readonly', '');
        el.style.position = 'absolute';
        el.style.left = '-9999px';
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        document.body.removeChild(el);
        return false;
    });
});

/* Stop dropdown-items from closing on click */
$(document).ready(function() {
    $(".disable-close-on-click").on("click", function(e) {
        e.stopPropagation();
    });
});
