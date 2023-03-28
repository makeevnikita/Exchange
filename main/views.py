from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from . import exchangenetwork as network
from . import services
from cryptosite.settings import MEDIA_URL
from django.core.cache import cache
from django.views import View
from datetime import datetime

import json
import logging
import traceback



NAV_BAR = [{'title': 'Правила обмена', 'url_name': 'rules'},
           {'title': 'Контакты', 'url_name': 'contacts'}]
    
def get_context():
    context = {
        'nav_bar': NAV_BAR,
        'MEDIA_URL': MEDIA_URL
    }
    return context

logging.getLogger('main')

class ExchangeView(View):
    
    template_name = 'main/coins.html'

    async def get(self, request, *args, **kwargs):
        
        context = get_context()
        try:
            context['title'] = 'Главная'
            context['give_coins'] = [coin for coin in await services.get_coins_to_give()]
            context['receive_coins'] = [coin for coin in await services.get_coins_to_receive()]
            context['exchange_ways'] =  json.dumps(list([coin for coin in await services.get_exchange_ways()]))
            context['give_tokens'] = json.dumps(list([coin for coin in await services.get_give_tokens()]))
            context['receive_tokens'] = json.dumps(list([coin for coin in await services.get_receive_tokens()]))
            
            return render(request=request, template_name=self.template_name, context=context)
        except Exception as exception:
            logging.exception(exception)

            return render(request=request, template_name='InternalError.html', status=500, context=context)
        
    async def post(self, request, *args, **kwargs):

        try:
            random_string = await services.create_new_order(
                    give_sum=request.POST['give_sum'],
                    receive_sum=request.POST['receive_sum'],
                    give_payment_method_id=request.POST['give_payment_method_id'],
                    receive_payment_method_id=request.POST['receive_payment_method_id'],
                    give_token_standart_id=request.POST['give_token_standart_id'],
                    receive_token_standart_id=request.POST['receive_token_standart_id'],
                    receive_name=request.POST['receive_name'],
                    receive_address=request.POST['receive_address'])

            return JsonResponse({'link': 'start_exchange/exchange/%s' % random_string})
        except Exception as exception:
            logging.exception(exception)
    
def rules(request):

    if (request.method == 'GET'):
        context = {
            'nav_bar': NAV_BAR
        }
        return render(request, 'main/rules.html', context=context)

def contacts(request):

    pass

async def get_exchange_rate(request):
    
    try:
        rates = cache.get('rates')
        if not rates:

            exchange = network.ExchangeClient(network.CurrenciesFromMYSQL, network.CentreBankAPI)
            rates = await exchange.get_rate()

            cache.set('rates', rates, 1800)

        return JsonResponse({'rates': json.dumps(rates)}, safe=False, json_dumps_params={'ensure_ascii': False})
    except Exception as exception:
        logging.exception(exception)

class MakeOrderView(View):

    async def get(self, request, *args, **kwargs):

        """
            Находит заказ, считает сколько прошло времени с момента создания заказа
            Клиент видит данные заказа и сколько времени осталось, чтобы оплатить его 
        """

        try:
            context = get_context()
            order = await services.get_order(kwargs['random_string'])
            context['order'] = order

            delta = datetime.now() - order.date_time.replace(tzinfo=None)
            total_seconds = 1200 - delta.total_seconds()

            if (total_seconds <= 0):
                context['minutes'] = '00'
                context['seconds'] = '00'
            else:
                minutes = int(total_seconds / 60)
                seconds = int(((total_seconds / 60) % 1) * 60)
                context['minutes'] = minutes if minutes >= 10 else f'0{minutes}'
                context['seconds'] = seconds if seconds >= 10 else f'0{seconds}'

            return render(request=request, template_name='main/pay_order.html', context=context)
        except Exception as exception:
            logging.exception(exception)

            return render(request=request, template_name='InternalError.html', status=500, context=context)
        
    async def post(self, request, *args, **kwargs):

        """
            Получает ответ от клиента о том оплатил ли он заказ или нет
        """

        try:
            order = await services.get_order(request.POST['random_string'])
            order.paid = request.POST['confirm']
            order.save()

            return JsonResponse({order.number, order.paid}, safe=False, json_dumps_params={'ensure_ascii': False})
        except Exception as exception:
            logging.exception(exception)