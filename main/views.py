from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from django.core.cache import cache
from . import services
from cryptosite.settings import MEDIA_URL
from django.core.cache import cache
from django.views import View

NAV_BAR = [{'title': 'Правила обмена', 'url_name': 'rules'},
           {'title': 'Контакты', 'url_name': 'contacts'}]

class ExchangeView(View):
    
    template_name = 'main/coins.html'

    async def get(self, request, *args, **kwargs):
        context = {
                'nav_bar': NAV_BAR,
                'give_coins': [coin for coin in await services.get_coins()][0],
                'receive_coins': [coin for coin in await services.get_coins()][1],
                'exchange_ways': json.dumps(list([coin for coin in await services.get_coins()][2])),
                'give_tokens': json.dumps(list([coin for coin in await services.get_coins()][3])),
                'receive_tokens': json.dumps(list([coin for coin in await services.get_coins()][4])),
                'MEDIA_URL': MEDIA_URL,
                'titile': 'Главная'
            }
        
        return render(request=request, template_name=self.template_name, context=context)

def rules(request):

    if (request.method == 'GET'):
        context = {
            'nav_bar': NAV_BAR
        }
        return render(request, 'main/rules.html', context=context)

def contacts(request):

    pass

async def get_exchange_rate(request):
    
    rates = cache.get('rates')
    if not rates:

        rates = await services.NetworkAPI.get_rate_crypto()
        usd_rate = cache.get('RUB')
        if not usd_rate:
            rates['RUB'] = await services.NetworkAPI.get_usdt_rate()
            cache.set('RUB', rates['RUB'], 1800)
        else:
            rates['RUB'] = usd_rate
        cache.set('rates', rates, 60)

        return JsonResponse({'rates': json.dumps(rates)}, safe=False, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'rates': json.dumps(rates)}, safe=False, json_dumps_params={'ensure_ascii': False})

async def start_exchange(request):
    
    if (request.POST):
        
        order_number = await services.create_new_order(
            give_sum=request.POST['give_sum'],
            receive_sum=request.POST['receive_sum'],
            give_payment_method_id=request.POST['give_payment_method_id'],
            receive_payment_method_id=request.POST['receive_payment_method_id'],
            give_token_standart_id=request.POST['give_token_standart_id'],
            receive_token_standart_id=request.POST['receive_token_standart_id'],
            give_name=request.POST['give_name'],
            give_address=request.POST['give_address'],
            receive_address=request.POST['receive_address'])

        return JsonResponse({'link': 'start_exchange/exchange/%s' % order_number})
    
async def exchange(request, random_string):
    print(f'\f\f{random_string}/\f\f')
    order = await services.get_order(random_string)
    print(order.give.currency_name)
    context = {'order': order, 
               'MEDIA_URL': MEDIA_URL}
    return render(request=request, template_name='main/exchange.html', context=context)