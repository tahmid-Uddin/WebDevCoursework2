
$(document).ready(function() {
    // Set the CSRF token for all AJAX requests
    var csrf_token = $('meta[name=csrf-token]').attr('content');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    // Handle wishlist toggle clicks
    $("a.wishlist").on("click", function() {
        var clicked_obj = $(this);
        var product_id = $(this).attr('id');
        var heart_icon = $(this).children()[0];

        $.ajax({
            url: '/toggle_wishlist/' + product_id,
            type: 'POST',
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(response) {
                if (response.success) {
                    if (response.in_wishlist) {
                        $(heart_icon).removeClass('text-secondary').addClass('text-danger');
                    } else {
                        $(heart_icon).removeClass('text-danger').addClass('text-secondary');
                    }
                }
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});