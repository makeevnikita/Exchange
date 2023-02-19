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
function start_exchange(){
    give_coin = jQuery('#give-table').children().children('.currency-td.selected')[0].getAttribute('id')
    receive_coin = jQuery('#receive-table').children().children('.currency-td.selected')[0].getAttribute('id')
    jQuery.ajax({
        url: 'test/',
        method: 'post',
        dataType: 'html',
        data: { 'give_coin': give_coin, 'receive_coin': receive_coin, 'csrfmiddlewaretoken': getCookie('csrftoken') },
        success: function(response){
            console.log(response)
        }
    });
}
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    console.log(cookieValue)
    return cookieValue;
}
function start_exchange() {
    /*Начать обмен
      Показываем модальное окно и заполняем его данными
    */
    
    give_sum = jQuery('#give-input-sum').val()//Сумма, которую отдаёт юзер
    currency_name_short = jQuery('#give-table .selected')[0].getAttribute('currency-name-short')//Короткое название валюты
    give_payment_method_id = jQuery('#give-table .selected')[0].getAttribute('payment-method')//Споособ оплаты
    give_payment_method_name = jQuery('#give-table .selected')[0].innerText//Название валюты/системы платежа
    
    jQuery('.check-claim-side.from .payment-sum .check-claim-amount')[0].innerHTML = give_sum + " " + currency_name_short

    jQuery('.check-claim-side.from .exchange_icon img')[0].src = jQuery('#give-table .selected img')[0].src

    if (give_payment_method_id == 1) {//Банковская карта
        if (jQuery('#give-input-bank-card').val() == '' 
            || jQuery('#give-input-bank-card').val().length < jQuery('#give-input-bank-card')[0].getAttribute('min')
            || jQuery('#give-input-bank-card').val().length > jQuery('#give-input-bank-card')[0].getAttribute('max')
            || jQuery('#give-input-name').val() == '') {
                return
            }
        jQuery('.check-claim-side.from .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#give-input-bank-card').val()
    }
    else if (give_payment_method_id == 2) {//Криптовалюта
        if (typeof jQuery('#give-networks-body .custom-radio:checked+label')[0] != 'undefined') {
            give_payment_method_name += ` <b>сеть: ${jQuery('#give-networks-body .custom-radio:checked+label')[0].innerHTML}</b> `
        }
        jQuery('.check-claim-side.from .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#give_input_crypto').val()
    }
    else if (give_payment_method_id == 3) {//Онлайн кошелёк
        jQuery('.check-claim-side.from .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#give-input-online-wallet').val()
    }
    jQuery('.check-claim-side.from .payment-sum .check-claim-ps')[0].innerHTML = give_payment_method_name

    receive_sum = jQuery('#receive-input-sum').val()//Сумма, которую получает юзер
    currency_name_short = jQuery('#receive-table .selected')[0].getAttribute('currency-name-short')//Короткое название валюты
    receive_payment_method_id = jQuery('#receive-table .selected')[0].getAttribute('payment-method')//Споособ оплаты
    receive_payment_method_name = jQuery('#receive-table .selected')[0].innerText//Название валюты/системы платежа
    
    jQuery('.check-claim-side.to .payment-sum .check-claim-amount')[0].innerHTML = receive_sum + " " + currency_name_short

    jQuery('.check-claim-side.to .exchange_icon img')[0].src = jQuery('#receive-table .selected img')[0].src

    if (receive_payment_method_id == 1) {//Банковская карта
        jQuery('.check-claim-side.to .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#receive-input-bank-card').val()
    }
    else if (receive_payment_method_id == 2) {//Криптовалюта
        if (typeof jQuery('#receive-networks-body .custom-radio:checked+label')[0] != 'undefined') {
            receive_payment_method_name += ` <b>сеть: ${jQuery('#receive-networks-body .custom-radio:checked+label')[0].innerHTML}</b> `
        }
        jQuery('.check-claim-side.to .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#receive_input_crypto').val()
    }
    else if (receive_payment_method_id == 3) {//Онлайн кошелёк
        jQuery('.check-claim-side.to .check-claim-reqs').children('#address')[0].innerHTML = jQuery('#receive-input-online-wallet').val()
    }
    jQuery('.check-claim-side.to .payment-sum .check-claim-ps')[0].innerHTML = receive_payment_method_name

    receive_sum = jQuery('#receive-input-sum').val()
    jQuery('.modal').css('opacity', 1)
    jQuery('.modal').css('pointer-events', 'all')
}