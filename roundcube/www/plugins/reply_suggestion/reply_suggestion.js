window.doctor_email = ""
function mark_as_forwarded_by_care_ai(doctor_email) {
    // Access session and perform actions
    window.doctor_email = doctor_email
    rcmail.http_post('plugin.mark_as_forwarded_by_care_ai', {});
}

function download_attachment(fileName) {
    var downloadUrl = "/?_task=mail&_mbox=" + rcmail.env.mailbox + "&_uid=" + rcmail.env.uid + "&_part=2" + "&_download=1&_action=get&_token=" + rcmail.env.request_token;

    // Fetch the file
    fetch(downloadUrl)
        .then(response => response.blob()) // Convert response to Blob
        .then(blob => {
            // Create a temporary URL for the Blob object
            var blobUrl = window.URL.createObjectURL(blob);

            // Create an anchor element and trigger the download with the provided file name
            var anchor = document.createElement('a');
            anchor.href = blobUrl;
            anchor.setAttribute('download', fileName + '.pdf'); // Use the provided file name with .pdf suffix
            anchor.style.display = 'none';
            document.body.appendChild(anchor);
            anchor.click();
            
            // Clean up by removing the anchor element and releasing the Blob URL
            document.body.removeChild(anchor);
            window.URL.revokeObjectURL(blobUrl);
        })
        .catch(error => {
            console.error('Download failed:', error);
        });
}
function care_ai_forward(args) {
    // Access session and perform actions
    current_uid = rcmail.env.uid
    // redirect browser to ?_task=mail&_forward_uid=42&_mbox=INBOX&_action=compose use current_uid for _forward_uid
    url = {"_forward_uid": current_uid, "_mbox": rcmail.env.mailbox, "to" : window.doctor_email}
    window.doctor_email = ""
    rcmail.open_compose_step(url);
    //window.location.href = 'index.php?_task=mail&_forward_uid=' + current_uid + '&_mbox=' + rcmail.env.mailbox + '&_action=compose'

}

$(document).ready(function () {
    rcmail.addEventListener('plugin.care_ai_forward', care_ai_forward)
    $('#fetch-suggestion').on('click', function () {
        // Make an AJAX call to fetch the suggested reply
        $.ajax({
            url: 'plugin.reply_suggestion.fetch_suggestion', // URL to Roundcube plugin backend
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    $('#suggested-reply').html(response.suggestion); // Display the suggestion
                } else {
                    $('#suggested-reply').html('<p>Error fetching suggestion</p>');
                }
            },
            error: function () {
                $('#suggested-reply').html('<p>Error connecting to server</p>');
            }
        });
    });
});

