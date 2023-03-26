var receive_give_currency_list = {};
var give_token_standart_list = {};
var receive_token_standart_list = {};
var exchange_rates_dict = {}
var commission = {}
var MEDIA_URL = ''
jQuery(document).ready(function(){
    receive_give_currency_list = JSON.parse(jQuery('#exchange_ways')[0].innerHTML)
    give_tokens = JSON.parse(jQuery('#give_tokens')[0].innerHTML)
    receive_tokens = JSON.parse(jQuery('#receive_tokens')[0].innerHTML)
    jQuery('#give-table').children(':first').children(':first').trigger('click')
    get_exchange_rates()
});
function get_exchange_rates() {
    jQuery.ajax({
        url: 'get_exchange_rate/',
        method: 'get',
        dataType: 'json',
        success: function(response){
            exchange_rates_dict = JSON.parse(response['rates'])
            update_rates()
        }
    });
    setTimeout(get_exchange_rates, 60000)
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
function show_model() {
    
    /*Начать обмен
      Показываем модальное окно и заполняем его данными
    */
     
    valid = true
    if (jQuery('#give-input-sum').val() == '') {
        jQuery('#give-input-sum').css('border', '1px solid red')
        valid = false
    } else {
        var give_sum = jQuery('#give-input-sum').val()//Сумма, которую отдаёт юзер
    }
    
    give_currency_name_short = jQuery('#give-table .selected')[0].getAttribute('currency-name-short')//Короткое название валюты
    give_payment_method_id = jQuery('#give-table .selected')[0].getAttribute('payment-method')//Споособ оплаты
    give_payment_method_name = jQuery('#give-table .selected')[0].innerText//Название валюты/системы платежа
    
    jQuery('.check-claim-side.from .payment-sum .check-claim-amount')[0].innerHTML = give_sum + " " + give_currency_name_short

    jQuery('.check-claim-side.from .exchange_icon img')[0].src = jQuery('#give-table .selected img')[0].src

    if (give_payment_method_id == 1) {//Банковская карта
        if (jQuery('#give-input-name').val() == '') {
            jQuery('#give-input-name').css('border', '1px solid red')
            valid = false
        } else {
            jQuery('.check-claim-side.from .check-claim-reqs').children('#name')[0].innerHTML = jQuery('#give-input-name').val()
        }
        if (jQuery('#give-input-bank-card').val() == '' || 
            jQuery('#give-input-bank-card').val().length < 16 ||
            jQuery('#give-input-bank-card').val().length > 18) {
            jQuery('#give-input-bank-card').css('border', '1px solid red')
            valid = false
        } else {
            jQuery('.check-claim-side.from .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#give-input-bank-card').val()
        }   
    }
    else if (give_payment_method_id == 2) {//Криптовалюта
        give_payment_method_name += ` <b>сеть: ${jQuery('#give-networks-body .custom-radio:checked+label')[0].innerHTML}</b>`
    }
    else if (give_payment_method_id == 3) {//Онлайн кошелёк
        if (jQuery('#give-input-online-wallet').val() == '') {
            jQuery('#give-input-online-wallet').css('border', '1px solid red')
            valid = false
        } else {
            jQuery('.check-claim-side.from .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#give-input-online-wallet').val()
        }
    }
    jQuery('.check-claim-side.from .payment-sum .check-claim-ps')[0].innerHTML = give_payment_method_name

    if (jQuery('#receive-input-sum').val() == '') {
        jQuery('#receive-input-sum').css('border', '1px solid red')
        valid = false
    } else {
        var receive_sum = jQuery('#receive-input-sum').val()//Сумма, которую получает юзер
    }
    
    receive_currency_name_short = jQuery('#receive-table .selected')[0].getAttribute('currency-name-short')//Короткое название валюты
    receive_payment_method_id = jQuery('#receive-table .selected')[0].getAttribute('payment-method')//Споособ оплаты
    receive_payment_method_name = jQuery('#receive-table .selected')[0].innerText//Название валюты/системы платежа
    
    jQuery('.check-claim-side.to .payment-sum .check-claim-amount')[0].innerHTML = receive_sum + " " + receive_currency_name_short

    jQuery('.check-claim-side.to .exchange_icon img')[0].src = jQuery('#receive-table .selected img')[0].src

    if (receive_payment_method_id == 1) {//Банковская карта
        if (jQuery('#receive-input-name').val() == '') {
            jQuery('#receive-input-name').css('border', '1px solid red')
            valid = false
        } else {
            jQuery('.check-claim-side.to .check-claim-reqs').children('#name')[0].innerHTML = jQuery('#receive-input-name').val()
        }
        if (jQuery('#receive-input-bank-card').val() == '' || 
            jQuery('#receive-input-bank-card').val().length < 16 ||
            jQuery('#receive-input-bank-card').val().length > 18) {
            jQuery('#receive-input-bank-card').css('border', '1px solid red')
            valid = false
        } else {
            jQuery('.check-claim-side.to .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#receive-input-bank-card').val()
        }
    }
    else if (receive_payment_method_id == 2) {//Криптовалюта
        if (jQuery('#receive_input_crypto').val() == '') {
            jQuery('#receive_input_crypto').css('border', '1px solid red')
            valid = false
        } else {
            if (typeof jQuery('#receive-networks-body .custom-radio:checked+label')[0] != 'undefined') {
                receive_payment_method_name += ` <b>сеть: ${jQuery('#receive-networks-body .custom-radio:checked+label')[0].innerHTML}</b> `
            }
            jQuery('.check-claim-side.to .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#receive_input_crypto').val()
        } 
    }
    else if (receive_payment_method_id == 3) {//Онлайн кошелёк
        if (jQuery('#receive-input-online-wallet').val() == '') {
            jQuery('#receive-input-online-wallet').css('border', '1px solid red')
            valid = false
        } else {
            jQuery('.check-claim-side.to .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#receive-input-online-wallet').val()
        }
    }
    if (valid) {
        jQuery('.check-claim-side.to .payment-sum .check-claim-ps')[0].innerHTML = receive_payment_method_name
        jQuery('.modal').css('opacity', 1)
        jQuery('.modal').css('pointer-events', 'all')
    }
}
function start() {
    jQuery('#accept').css('pointer-events', 'none')
    var data = {}
    data['csrfmiddlewaretoken'] = getCookie('csrftoken')
    data['give_sum'] = jQuery('#give-input-sum').val()
    data['receive_sum'] = jQuery('#receive-input-sum').val()
    data['give_payment_method_id'] = jQuery('#give-table .selected')[0].id
    data['receive_payment_method_id'] = jQuery('#receive-table .selected')[0].id
    data['give_token_standart_id'] = 1
    data['receive_token_standart_id'] = 1
    data['receive_name'] = jQuery('#receive-input-name').val()
    data['receive_address'] = null

    give_payment_method_id = jQuery('#give-table .selected')[0].getAttribute('payment-method')//Споособ оплаты
    if (give_payment_method_id == 1) {
        //Банковская карта
        data['give_address'] = jQuery('#give-input-bank-card').val()
    } else if (give_payment_method_id == 2) {
        //Криптовалюта
        data['give_token_standart_id'] = jQuery('#give-networks-body .custom-radio:checked+label')[0].closest('DIV').children[0].id.match(/(\d+)/)[0]
    } else if (give_payment_method_id == 3) {
        //Онлайн кошелёк
        data['give_address'] = jQuery('#give-input-online-wallet').val()
    }
    
    receive_payment_method_id = jQuery('#receive-table .selected')[0].getAttribute('payment-method')//Споособ оплаты
    if (receive_payment_method_id == 1) {
        //Банковская карта
        data['receive_address'] = jQuery('#receive-input-bank-card').val()
    } else if (receive_payment_method_id == 2) {
        //Криптовалюта
        data['receive_address'] = jQuery('#receive_input_crypto').val()
    } else if (receive_payment_method_id == 3) {
        //Онлайн кошелёк
        data['receive_token_standart_id'] = jQuery('#receive-networks-body .custom-radio:checked+label')[0].closest('DIV').children[0].id.match(/(\d+)/)[0]
        data['receive_address'] = jQuery('#receive-input-online-wallet').val()
    }
    jQuery.ajax({
        url: 'start_exchange/',
        method: 'post',
        dataType: 'json',
        data: data,
        success: function(response){
            window.location = response['link']
        }
    });
}
function cancel() {
    jQuery('.modal').css('opacity', 0)
    jQuery('.modal').css('pointer-events', 'none')

    jQuery('.check-claim-side.from .check-claim-reqs').children('#address')[0].innerHTML = ''
    jQuery('.check-claim-side.from .check-claim-reqs').children('#name')[0].innerHTML = ''

    jQuery('.check-claim-side.to .check-claim-reqs').children('#address')[0].innerHTML = ''
    jQuery('.check-claim-side.to .check-claim-reqs').children('#name')[0].innerHTML = ''
}