import httpx
from . import services

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
    async def get_rate_crypto(cls, currency_name_short):
        for api in cls.SPECIFIC_RATES:
            if (currency_name_short != 'RUB'):
                try:
                    rate = await api(currency_name_short)
                    if (rate != None):
                        return float(rate)
                except:
                    pass

    async def get_usdt_rate():
        try:
            async with httpx.AsyncClient() as client:
                    response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
            if (response.status_code != 200):
                    raise ConnectionError
            return response.json()['Valute']['USD']['Value']
        except:
            pass

