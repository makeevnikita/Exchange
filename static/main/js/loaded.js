var receive_give_currency_list = {};
var give_token_standart_list = {};
var receive_token_standart_list = {};
var exchange_rates_dict = {}
var commission = {}
var MEDIA_URL = ''
jQuery(document).ready(function(){
    jQuery.ajax({
        url: 'select_coins/',
        dataType: 'json',
        method: 'get',
        success: function(response){
            receive_token_standart_list = JSON.parse(response['receive_token_standart_list'])
            give_token_standart_list = JSON.parse(response['give_token_standart_list'])
            receive_give_currency_list = JSON.parse(response['receive_give_currency_list'])
            console.log(give_token_standart_list)
            MEDIA_URL = response['MEDIA_URL']
            jQuery('#give-table').children(':first').children(':first').trigger('click')
            get_exchange_rates()
        }
    });
    function get_exchange_rates() {
        jQuery.ajax({
            url: 'get_exchange_rate/',
            method: 'get',
            dataType: 'json',
            success: function(response){
                exchange_rates_dict = JSON.parse(response['exchange_rates'])
                commissions = JSON.parse(response['commissions'])
                update_rates()
            }
        });
        setTimeout(get_exchange_rates, 60000)
    }
});
