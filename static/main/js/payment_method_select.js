jQuery('#give-table').children().children('.currency-td').click(function(event) {

  if (jQuery(this).hasClass('selected')){
    return
  }
  jQuery(this).addClass('selected').parent().siblings().children().removeClass('selected');

  let td = ''
  if (event.target.tagName == 'IMG'){
    td = event.target.closest('td')
  }else{
    td = event.target
  }
  payment_method = td.getAttribute('payment-method')
  currency_name = td.textContent.replace(/\s/g, "")
  currency_id = td.getAttribute('currency-id')

  jQuery('#give-currency-name-short').text(td.getAttribute('currency-name-short'))

  let table = ''
  for (const [key, value] of Object.entries(receive_give_currency_list)) {
    if (value['give_id'] == currency_id) {
      table += `<tr><td class="currency-td" currency-id="${value['receive_id']}"` +
      `payment-method="${value['receive__category_payment_method__id']}"` +
      `currency-name-short="${value['receive__currency_name_short']}">` +
      `<img src="${MEDIA_URL + value['receive__image']}">${value['receive__currency_name']}</td></tr>`
    }
  }
  if (payment_method == '1') {
    jQuery('#give-bank-card-form').prop('hidden', false)
    jQuery('#give-online-wallet').prop('hidden', true)
    jQuery('#give-crypto-form').prop('hidden', true)
    
    jQuery('#give-input-bank-card').attr('placeholder', 'Номер карты ' + currency_name + ' (без пробелов)')
  }
  if (payment_method == '2') {
    jQuery('#give-networks-body').empty()
    for (const [key, value] of Object.entries(give_token_standart_list)) {
      if (value['give_id'] == currency_id) {
      let network = '<div class="network">' +
      `<input id="network-choice${value['give__token_standart__id']}" class="custom-radio" name="networks_1" ` +
      `type="radio" value="${value['give__token_standart__token_standart']}" undefined="">` +
      `<label for="network-choice${value['give__token_standart__id']}">${value['give__token_standart__token_standart']}</label>`
      '</div>'
      jQuery('#give-networks-body').append(network)
      }
    }
    jQuery('#give-bank-card-form').prop('hidden', true)
    jQuery('#give-online-wallet').prop('hidden', true)
    jQuery('#give-crypto-form').prop('hidden', false)
    
    jQuery('#give_input_crypto').attr('placeholder', currency_name + ' адрес кошелька')
  }
  if (payment_method == '3') {
    jQuery('#give-bank-card-form').prop('hidden', true)
    jQuery('#give-online-wallet').prop('hidden', false)
    jQuery('#give-crypto-form').prop('hidden', true)

    jQuery('#give-input-online-wallet').attr('placeholder', currency_name + ' адрес кошелька')
  }
  jQuery('#receive-table').html(table)
  jQuery('#receive-table').children(':first').children(':first').trigger('click');
});


jQuery('#receive-table').click(function(event) {
  let td = ''
  if (event.target.tagName == 'IMG') {
    td = event.target.closest('td')
  }else if (event.target.tagName == 'TR') {
    td = event.target.children('td')
  }else if (event.target.tagName == 'TD') {
    td = event.target
  }else {
    return
  }
  if (jQuery(td).hasClass('selected')){
    return
  }
  jQuery(td).addClass('selected').parent().siblings().children().removeClass('selected');

  payment_method = td.getAttribute('payment-method')
  currency_name = td.textContent.replace(/\s/g, "")
  currency_id = td.getAttribute('currency-id')

  jQuery('#receive-currency-name-short').text(td.getAttribute('currency-name-short'))

  if (payment_method == '1') {
    jQuery('#receive-bank-card-form').prop('hidden', false)
    jQuery('#receive-online-wallet').prop('hidden', true)
    jQuery('#receive-crypto-form').prop('hidden', true)
    
    jQuery('#receive-input-bank-card').attr('placeholder', 'Номер карты ' + currency_name + ' (без пробелов)')
  }
  if (payment_method == '2') {
    jQuery('#receive-networks-body').empty()
    for (const [key, value] of Object.entries(receive_token_standart_list)) {
      if (value['receive_id'] == currency_id) {
        let network = '<div class="network">' +
        `<input id="network-choice${value['receive__token_standart__id']}" class="custom-radio" name="networks_1" ` +
        `type="radio" value="${value['receive__token_standart__token_standart']}" undefined="">` +
        `<label for="network-choice${value['receive__token_standart__id']}">${value['receive__token_standart__token_standart']}</label>`
        '</div>'
        jQuery('#receive-networks-body').append(network)
      }
    }
    jQuery('#receive-bank-card-form').prop('hidden', true)
    jQuery('#receive-online-wallet').prop('hidden', true)
    jQuery('#receive-crypto-form').prop('hidden', false)

    jQuery('#receive_input_crypto').attr('placeholder', currency_name + ' адрес кошелька')
  }
  if (payment_method == '3') {
    jQuery('#receive-bank-card-form').prop('hidden', true)
    jQuery('#receive-online-wallet').prop('hidden', false)
    jQuery('#receive-crypto-form').prop('hidden', true)

    jQuery('#receive-input-online-wallet').attr('placeholder', currency_name + ' адрес кошелька')
  }
  
  update_rates()
});
function update_rates() {

  if (Object.keys(exchange_rates_dict).length == 0) {
    return
  }
  
  give_currency_name_short = jQuery('#give-table').children().children('.currency-td.selected')[0].getAttribute('currency-name-short')
  receive_currency_name_short = jQuery('#receive-table').children().children('.currency-td.selected')[0].getAttribute('currency-name-short')
  if (give_currency_name_short == 'RUB' && receive_currency_name_short != 'RUB') {
    sum = exchange_rates_dict[receive_currency_name_short] * exchange_rates_dict['RUB']
    jQuery('#rate-exchange').text(`${Math.round(sum * 100) / 100} RUB = 1 ${receive_currency_name_short}`)
  }
  else if (give_currency_name_short != 'RUB' && receive_currency_name_short == 'RUB') {
    sum = exchange_rates_dict[give_currency_name_short] * exchange_rates_dict['RUB']
    jQuery('#rate-exchange').text(` 1 ${give_currency_name_short} = ${Math.round(sum * 100) / 100} RUB`)
  }
  else if (give_currency_name_short != 'RUB' && receive_currency_name_short != 'RUB') {
    if (exchange_rates_dict[give_currency_name_short] > exchange_rates_dict[receive_currency_name_short]) {
      sum = exchange_rates_dict[give_currency_name_short] / exchange_rates_dict[receive_currency_name_short]
      jQuery('#rate-exchange').text(` 1 ${give_currency_name_short} = ${Math.round(sum * 100) / 100} ${receive_currency_name_short}`)
    } else {
      sum = exchange_rates_dict[receive_currency_name_short] / exchange_rates_dict[give_currency_name_short]
      jQuery('#rate-exchange').text(` 1 ${receive_currency_name_short} = ${Math.round(sum * 100) / 100} ${give_currency_name_short}`)
    }
  }

  jQuery('.rate-span').css('display', 'flex')
  jQuery('.middle').css('display', 'none')
  
}