from django.shortcuts import render
from django.http import JsonResponse
from django.core.cache import cache
from . import exchangenetwork as network
from . import services
from cryptosite.settings import MEDIA_URL, NAV_BAR
from django.core.cache import cache
from django.views import View
from datetime import datetime
from django.contrib.auth import get_user

import json
import logging


  
def get_context():
    context = {
        'nav_bar': NAV_BAR,
        'MEDIA_URL': MEDIA_URL,
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
        
        user = None
        if get_user(request).is_authenticated:
            user = get_user(request)

        random_string = await services.create_new_order(
                give_sum=request.POST['give_sum'],
                receive_sum=request.POST['receive_sum'],
                give_payment_method_id=request.POST['give_payment_method_id'],
                receive_payment_method_id=request.POST['receive_payment_method_id'],
                give_token_standart_id=request.POST['give_token_standart_id'],
                receive_token_standart_id=request.POST['receive_token_standart_id'],
                receive_name=request.POST['receive_name'],
                receive_address=request.POST['receive_address'],
                user=user
        )

        return JsonResponse(
            data={'link': 'start_exchange/exchange/{0}'.format(random_string)},
        )
    
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

            exchange = network.ExchangeClient(
                network.CurrenciesFromMYSQL,
                network.CentreBankAPI
            )
            rates = await exchange.get_rate()

            cache.set('rates', rates, 1800)

        return JsonResponse(
            data={'rates': json.dumps(rates)},
            safe=False,
            json_dumps_params={'ensure_ascii': False},
        )
    except Exception as exception:
        logging.exception(exception)

class MakeOrderView(View):

    async def get(self, request, *args, **kwargs):
        """
            Находит заказ, считает сколько прошло времени с момента создания заказа.
            Клиент видит данные заказа и сколько времени осталось, чтобы оплатить его.

            return: HttpResponse
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
                context['minutes'] = minutes if minutes >= 10 else '0{0}'.format(minutes)
                context['seconds'] = seconds if seconds >= 10 else '0{0}'.format(seconds)

            return render(
                request=request,
                template_name='main/pay_order.html',
                context=context,
            )
        except Exception as exception:
            logging.exception(exception)

            return render(
                request=request,
                template_name='InternalError.html',
                status=500,
                context=context,
            )

    async def post(self, request, *args, **kwargs):
        """
            Получает ответ от клиента о том оплатил ли он заказ или нет.

            return: JsonResponse
        """

        try:
            order = await services.set_order_confirm(
                request.POST['random_string'],
                request.POST['confirm'],
            )

            return JsonResponse(
                data={order.number, order.paid},
                safe=False,
                json_dumps_params={'ensure_ascii': False},
            )
        except Exception as exception:
            logging.exception(exception)
