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