jQuery(document).ready(function () {
    countTime()
})
function countTime() {
    if (jQuery('#minutes')[0].innerText == '00' && jQuery('#seconds')[0].innerText == '00') {
        jQuery('#timeout').css('display', 'block')
        return
    }
    seconds = jQuery('#seconds')[0].innerText
    if (seconds == '00') {
        if (jQuery('#minutes')[0].innerText <= 10) {
            jQuery('#minutes')[0].innerText = `0${jQuery('#minutes')[0].innerText - 1}`
        }
        else {
            jQuery('#minutes')[0].innerText = jQuery('#minutes')[0].innerText - 1
        }
        jQuery('#seconds')[0].innerText = '59'
    }
    else {
        if (jQuery('#seconds')[0].innerText <= 10) {
            jQuery('#seconds')[0].innerText = `0${jQuery('#seconds')[0].innerText - 1}`    
        } else {
            jQuery('#seconds')[0].innerText = jQuery('#seconds')[0].innerText - 1   
        }
    }
    setTimeout(countTime, 1000)    
}
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