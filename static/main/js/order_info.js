jQuery('#confirm').click(
    function confirmPayment() {
        jQuery.ajax({
            url: window.location.pathname.split('/').at(-1),
            method: 'post',
            dataType: 'json',
            data: { confirm: true,
                    csrfmiddlewaretoken: getCookie('csrftoken')},
            success: function(response){
                window.location = window.location.pathname.split('/').at(-1)
                jQuery('#modal').css('opacity', 1)
                jQuery('#modal').css('pointer-events', 'all')
            }
        });
    }
)
jQuery('#cancel').click(
    function cancelPayment() {
        jQuery.ajax({
            url: window.location.pathname.split('/').at(-1),
            method: 'post',
            dataType: 'json',
            data: { confirm: false,
                    csrfmiddlewaretoken: getCookie('csrftoken'),
                },
            success: function(response){
                window.location = response['link']
            }
        });
    }
)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function closeModal() {
    jQuery('.modal').css('opacity', 0)
    jQuery('.modal').css('pointer-events', 'none')
}