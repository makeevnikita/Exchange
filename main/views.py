from django.shortcuts import render
from django.http import JsonResponse
import json
from django.core.cache import cache
from django.middleware.csrf import get_token
from . import exchange
from . import services
from cryptosite.settings import MEDIA_URL
from django.core.cache import cache

NAV_BAR = [{'title': 'Правила обмена', 'url_name': 'rules'},
           {'title': 'Контакты', 'url_name': 'contacts'}]

async def index(request):
    
    give_currency_list = cache.get('give_currency_list')
    if not give_currency_list:
        give_currency_list = [giveCurrency for giveCurrency in await services.get_GiveCurrencies_from_database()]
        cache.set('give_currency_list', give_currency_list, 300)

    context = {
            'nav_bar': NAV_BAR,
            'give_currency_list': give_currency_list,                             
            'MEDIA_URL': MEDIA_URL,
            'token': get_token(request)
        }
    
    return render(request, 'main/index.html', context=context)

def rules(request):

    if (request.method == 'GET'):
        context = {
            'nav_bar': NAV_BAR
        }
        return render(request, 'main/rules.html', context=context)

def contacts(request):

    pass

async def exclude_values(list, invalid_value):

    tmp_list = []
    for dict in list:
        tmp_list.append({key: dict[key] for key in dict if dict[invalid_value] != 1})
    return tmp_list

async def exclude_keys(list, valid_keys):
    
    tmp_list = []
    for dict in list:
        tmp_list.append({key: dict[key] for key in dict if key in valid_keys})
    return tmp_list

async def remove_duplicate(list):

    seen = set()
    distinct_list = []
    for dict in list:
        t = tuple(dict.items())
        if (t not in seen):
            seen.add(t)
            distinct_list.append(dict)
    return distinct_list

async def select_coins(request):
    
    coins = await services.get_ReceiveGiveCurrencies()
    valid_keys = ['receive_id',
                  'receive__token_standart__id',
                  'receive__token_standart__token_standart',
                  'receive__category_payment_method__id']

    receive_token_standart_list = await remove_duplicate(await exclude_values((await exclude_keys(coins, valid_keys)), 'receive__token_standart__id'))

    valid_keys = ['give_id',
                  'give__token_standart__id',
                  'give__token_standart__token_standart']
    give_token_standart_list = await remove_duplicate(await exclude_values((await exclude_keys(coins, valid_keys)), 'give__token_standart__id'))

    valid_keys = ['give_id','receive_id',
                  'receive__currency_name','receive__currency_name_short',
                  'receive__image','receive__category_payment_method__id']
    receive_give_currency_list = await remove_duplicate(await exclude_keys(coins, valid_keys))

    return JsonResponse({'receive_token_standart_list': json.dumps(list(receive_token_standart_list)),
                         'give_token_standart_list': json.dumps(list(give_token_standart_list)),
                         'receive_give_currency_list': json.dumps(receive_give_currency_list),
                            'MEDIA_URL': MEDIA_URL},
                            safe=False,
                            json_dumps_params={'ensure_ascii': False})

async def get_exchange_rate(request):
    
    
    response = {}
    currency_dict_cache = cache.get('exchange_rate')
    if not currency_dict_cache:
        coins = await services.get_ReceiveGiveCurrencies()
        give_currency_name_short_list = await remove_duplicate(await(exclude_keys(coins, ['give__currency_name_short'])))
        receive_currency_name_short_list = await remove_duplicate(await(exclude_keys(coins, ['receive__currency_name_short'])))

        currency_name_short_list = []
        for coin in give_currency_name_short_list + receive_currency_name_short_list:
            if ('RUB' not in coin.values()):
                currency_name_short_list.extend(coin.values())

        
        commissions = [commission for commission in await services.get_give_token_standart_commission_list()]
        currency_dict = {currency: await exchange.NetworkAPI.get_rate_crypto(currency) for currency in set(currency_name_short_list)}

        usd_rate = cache.get('RUB')
        if not usd_rate:
            currency_dict['RUB'] = await exchange.NetworkAPI.get_usdt_rate()
            cache.set('RUB', currency_dict['RUB'], 1800)
        else:
            currency_dict['RUB'] = usd_rate
            
        response['exchange_rates'] = json.dumps(currency_dict)
        response['commissions'] = json.dumps(commissions)
        
        cache.set('exchange_rate', response, 60)

        return JsonResponse(response, safe=False, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse(currency_dict_cache, safe=False, json_dumps_params={'ensure_ascii': False})
            
def get_coins(request):
    
    print(request.POST)
    return JsonResponse({'answer': 'Okay'},
                                safe=False,
                                json_dumps_params={'ensure_ascii': False})