import httpx
import traceback
from .services import get_short_names_of_coins

class NetworkAPI:
    
    @classmethod
    async def get_rate(cls, currency_name):
        raise NotImplementedError
    
    @classmethod
    def check_status_code(cls, response) -> bool:
        if (response.status_code != 200):
            return False
    
    @classmethod
    def output_error(cls, response):
        print(f'{cls.__name__}: Failed to get rate. URL: {response.url}. Status code: {response.status_code}')
        
class PoloniexAPI(NetworkAPI):
    
    RATE_URL = 'https://api.poloniex.com/markets/{0}/markPrice'
    
    @classmethod
    async def get_rate(cls, currency_name):

        async with httpx.AsyncClient() as client:
            try:
                currency_name = currency_name + '_USDT'
                response = await client.get(cls.RATE_URL.format(currency_name))

                if (cls.check_status_code(response) != False):
                    return response.json()['markPrice']
                
                raise
            except Exception as exception:
                print(exception)
                print(''.join(traceback.format_tb(exception.__traceback__)))
                cls.output_error(response)

class BitpayAPI(NetworkAPI):

    RATE_URL = 'https://bitpay.com/rates/{0}/usd'

    @classmethod
    async def get_rate(cls, currency):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(cls.RATE_URL.format(currency))
                
            if (cls.check_status_code(response) != False):
                return response.json()['data']['rate']
            
            raise
        except Exception as exception:
            print(exception)
            print(''.join(traceback.format_tb(exception.__traceback__)))
            cls.output_error(response)

class CurrenciesSource:

    @classmethod
    async def get_currency_list(self):
        raise NotImplementedError

class CurrenciesFromMYSQL(CurrenciesSource):

    @classmethod
    async def get_currency_list(self):
        return await get_short_names_of_coins()

class CentreBankAPI(NetworkAPI):

    @classmethod
    async def get_rate(cls):

        try:
            async with httpx.AsyncClient() as client:
                    response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
            if (cls.check_status_code(response) != False):
                    return response.json()['Valute']['USD']['Value']
            
            raise
        except Exception as exception:
            print(exception)
            print(''.join(traceback.format_tb(exception.__traceback__)))
            cls.output_error(response)

class NullAPI(NetworkAPI):

    @classmethod
    async def get_rate(self):
        return None

class ExchangeClient:
    
    def __init__(self, crypto_source: CurrenciesSource, usd_source: NetworkAPI = NullAPI) -> None:

        self.crypto_source = crypto_source
        self.usd_source = usd_source   

    async def get_rate(self):

        currencies = await self.crypto_source.get_currency_list()
        api_list = [PoloniexAPI.get_rate, BitpayAPI.get_rate]
        rates = {}
        
        for currency in currencies:
            for api in api_list:
                try:
                    rate = await api(currency)
                    if (rate != None):
                        rates[currency] = float(rate)
                        break
                except Exception as exception:
                    print(exception)
                    print(''.join(traceback.format_tb(exception.__traceback__)))

        rates['RUB'] = await self.usd_source.get_rate()
        
        return rates