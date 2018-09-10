$(document).ready(function () {
    $(function() {
        $('#upload-file-btn').click(function() {
            var form_data = new FormData($('#uploadform')[0]);
            $.ajax({
                type: 'POST',
                url: '/add',
                data: form_data,
                contentType: false,
                cache: false,
                processData: false,
                success: function(data) {
                    console.log('Success!');
                },
            });
        });
    });
});
