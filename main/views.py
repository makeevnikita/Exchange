from django.shortcuts import render
from django.http import JsonResponse
import json
from django.core.cache import cache
from django.middleware.csrf import get_token
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

def start_exchange(request):
    
    if (request.POST):

        print(f"\f\f{request.POST['give_coin']}")
        print(f"\f\f{request.POST['receive_coin']}")

        return render(request=request, template_name='main/exchange_from.html')