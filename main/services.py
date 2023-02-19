from main.models import ReceiveGiveCurrencies
from django.core.cache import cache
from asgiref.sync import sync_to_async
import httpx

@sync_to_async
def get_coins():
    
    coins = cache.get('coins')
    if not coins:
        try:
            coins = ReceiveGiveCurrencies.objects.select_related('give', 'receive', 'token_standart').values(
                    'give_id',
                    'give__currency_name',
                    'give__currency_name_short',
                    'give__image',
                    'give__category_payment_method__id',
                    'give__token_standart__id',
                    'give__token_standart__token_standart',
                    'receive_id',
                    'receive__currency_name',
                    'receive__currency_name_short',
                    'receive__image',
                    'receive__category_payment_method__id',
                    'receive__token_standart__id',
                    'receive__token_standart__token_standart'
                    )

            give_coins = coins.values('give_id',
                                      'give__currency_name',
                                      'give__currency_name_short',
                                      'give__image',
                                      'give__category_payment_method__id').distinct()

            receive_coins = coins.values('receive_id',
                                         'receive__currency_name',
                                         'receive__currency_name_short',
                                         'receive__image',
                                         'receive__category_payment_method__id').distinct()
            
            exchange_ways = coins.values('give_id',
                                'receive_id')
            
            give_tokens = coins.values('give_id',
                                       'give__token_standart__id',
                                       'give__token_standart__token_standart')\
                                        .exclude(give__token_standart__id = 1).distinct()
            
            receive_tokens = coins.values('receive_id',
                                          'receive__token_standart__id',
                                          'receive__token_standart__token_standart')\
                                          .exclude(receive__token_standart__id = 1).distinct()

            coins_name_short = []
            for coin in coins.values('give__currency_name_short','receive__currency_name_short')\
                                                      .exclude(give__currency_name_short='RUB',
                                                      receive__currency_name_short='RUB').distinct():
                if (coin['give__currency_name_short'] not in coins_name_short and coin['give__currency_name_short'] != 'RUB'):
                    coins_name_short.append(coin['give__currency_name_short'])
                if (coin['receive__currency_name_short'] not in coins_name_short and coin['receive__currency_name_short'] != 'RUB'):
                    coins_name_short.append(coin['receive__currency_name_short'])

            response = (give_coins, receive_coins, exchange_ways, give_tokens, receive_tokens, coins_name_short)           
            cache.set('coins', response, 300)
            return response
        except:
            pass
    
    return coins


class PoloniexAPI:
    
    SPECIFIC_RATE = 'https://api.poloniex.com/markets/{}/markPrice'

    @classmethod
    async def get_rate(cls, currency_name):
        try:
            pair = currency_name + '_USDT'
            print(cls.SPECIFIC_RATE.format(pair))
            async with httpx.AsyncClient() as client:
                response = await client.get(cls.SPECIFIC_RATE.format(pair))
            if (response.status_code != 200):
                raise ConnectionError
            return response.json()["markPrice"]
        except:
            raise ConnectionError

class BitpayAPI:
    SPECIFIC_RATE = 'https://bitpay.com/rates/{}/usd'

    @classmethod
    async def get_rate(cls, currency):
        try:
            print(cls.SPECIFIC_RATE.format(currency))
            async with httpx.AsyncClient() as client:
                    response = await client.get(cls.SPECIFIC_RATE.format(currency))
            if (response.status_code != 200):
                    raise ConnectionError
            return response.json()['data']['rate']
        except:
            raise ConnectionError
            
class NetworkAPI:
    SPECIFIC_RATES = [PoloniexAPI.get_rate, BitpayAPI.get_rate]
                
    @classmethod
    async def get_rate_crypto(cls):
        rate_dict = {}
        for coin in [coin for coin in await get_coins()][5]:
            for api in cls.SPECIFIC_RATES:
                try:
                    rate = await api(coin)
                    if (rate != None):
                        rate_dict[coin] = float(rate)
                        break
                except:
                    pass
        return rate_dict
        
    async def get_usdt_rate():
        try:
            async with httpx.AsyncClient() as client:
                    response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
            if (response.status_code != 200):
                    raise ConnectionError
            return response.json()['Valute']['USD']['Value']
        except:
            pass