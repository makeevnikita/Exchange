jQuery('#confirm').click(
    function confirmPayment() {
        jQuery.ajax({
            url: 'confirm_payment/',
            method: 'post',
            dataType: 'json',
            data: { confirm: 1,
                    random_string: window.location.pathname.split('/').at(-1),
                    csrfmiddlewaretoken: getCookie('csrftoken')},
            success: function(response){
                window.location = response['link']
                jQuery('#modal').css('opacity', 1)
                jQuery('#modal').css('pointer-events', 'all')
            }
        });
    }
)
function cancelPayment() {
    jQuery.ajax({
        url: '/confirm_payment/',
        method: 'post',
        dataType: 'json',
        data: { confirm: 0,
                random_string: window.location.pathname.split('/').at(-1),
                csrfmiddlewaretoken: getCookie('csrftoken')},
        success: function(response){
            window.location = response['link']
        }
    });
}
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