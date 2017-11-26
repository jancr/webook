
////////////////////////////////////////////////////////////////////////////////
// Event functions
////////////////////////////////////////////////////////////////////////////////
// var on_submit = (function(event) {
    // var form = $("#ebook_form");
    // var time = (new Date).getTime();
    // form.attr("action", "/ebook/" + time);
// });

var example_click = (function(event) {
    var example = "https://www.fanfiction.net/s/10360716/1/The-Metropolitan-Man";
    $("#url").val(example);
    $("#file_name").val('time');
    $("#parser > option")[1].selected = true;
});

////////////////////////////////////////////////////////////////////////////////
// Bind events
////////////////////////////////////////////////////////////////////////////////
var load_index_page = (function() {
    // $("#sumbit").click(on_submit);
    $("#example").click(example_click);
    // $(document).on('submit', '#ebook_form', on_submit);
});

