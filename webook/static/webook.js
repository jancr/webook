"use strict";

////////////////////////////////////////////////////////////////////////////////
// globals
////////////////////////////////////////////////////////////////////////////////
// var time_stamp = (new Date).getTime();

////////////////////////////////////////////////////////////////////////////////
// Event functions
////////////////////////////////////////////////////////////////////////////////


var submit_click = (function(event) {
    event.preventDefault();
    
    // show progress bar and parse argd
    $('.progress').show();
    var url = btoa($("#url").val())
    var parser = btoa($("#parser").val())

    // var file_name = "tmplkmtr_j1.epub";
    // var request_str = "/download_ebook/" + os.path.basename(file_name);
    // $.get(request_str);
    //
    var progress = new EventSource("/create_ebook/" + parser + '/' + url);
    progress.onmessage = function(event) {
        // the last message is the file name that was created
        if (/^file-name/.test(event.data)) {
            var file_name = /^file-name: (.+)/.exec(event.data)[1]
            var request_str = "/download_ebook/" + file_name;
            $.get(request_str);
            // $('#ebook_form').attr('action', 'download_ebook/' + file_name);
            // $('#ebook_form').submit()

            progress.close();
        // all other messages are the progress in percent
        } else {
            $('.progress-bar').css('width', event.data+'%').attr('aria-valuenow', event.data);   
        }
    }
});

var example_click = (function(event) {
    var example = "https://www.fanfiction.net/s/10360716/1/The-Metropolitan-Man";
    // this book is shorter
    // var example = "https://www.fanfiction.net/s/12729710/1/Love-is-Love-Warrior-Cats-Fan-Fiction"
    $("#url").val(example);
    // $("#file_name").val('time');
    $("#parser > option")[1].selected = true;
});

////////////////////////////////////////////////////////////////////////////////
// Bind events
////////////////////////////////////////////////////////////////////////////////
var load_index_page = (function() {
    $("#example").click(example_click);
    // $(document).on('submit', '#ebook_form', on_submit);
    $("#submit").click('submit', submit_click);
    $('#url').bind("enterKey", submit_click);
    //
    // $("form").on("submit", function( event ) {
        // event.preventDefault();
    // });
});

