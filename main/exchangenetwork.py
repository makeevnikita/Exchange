from .models import ReceiveGiveCurrencies
from abc import ABC, abstractmethod
import httpx



class GetRateError(Exception):
    
    def __init__(self, __name__, response) -> None:
        super().__init__(f'{__name__}: Failed to get rate. URL: {response.url}. Status code: {response.status_code}')

class NetworkAPI(ABC):
    
    @classmethod
    @abstractmethod
    async def get_rate(cls, currency_name):
        raise NotImplementedError
    
    @classmethod
    @abstractmethod
    def check_status_code(cls, response) -> bool:
        if (response.status_code != 200):
            return False
        
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
                
                return None
            except Exception as exception:
                raise exception

class BitpayAPI(NetworkAPI):

    RATE_URL = 'https://bitpay.com/rates/{0}/usd'

    @classmethod
    async def get_rate(cls, currency):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(cls.RATE_URL.format(currency))
                
            if (cls.check_status_code(response) != False):
                return response.json()['data']['rate']
            
            return None
        except Exception as exception:
            raise exception

class CurrenciesSource(ABC):

    @classmethod
    @abstractmethod
    def get_currency_list(cls):
        raise NotImplementedError

class CurrenciesFromMYSQL(CurrenciesSource):

    @classmethod
    def get_currency_list(cls):
        queryset = ReceiveGiveCurrencies.objects.short_names_of_coins()
        currencies = [x['give__currency_name_short'] for x in queryset]
        return currencies

class CentreBankAPI(NetworkAPI):

    @classmethod
    async def get_rate(cls):
        
        try:
            async with httpx.AsyncClient() as client:
                    response = await client.get('https://www.cbr-xml-daily.ru/daily_json.js')
            if (cls.check_status_code(response) != False):
                    return response.json()['Valute']['USD']['Value']
            
            raise GetRateError(cls.__name__, response)
        except Exception as exception:
            raise exception

class NullAPI(NetworkAPI):

    @classmethod
    async def get_rate(self):
        return None

class ExchangeClient:
    """Запрашивает курсы валют из сторонних API"""
    
    def __init__(self, crypto_source: CurrenciesSource, usd_source: NetworkAPI = NullAPI) -> None:

        self.crypto_source = crypto_source
        self.usd_source = usd_source   

    async def get_rate(self):

        currencies = self.crypto_source.get_currency_list()
        rates = dict.fromkeys(currencies)

        api_list = [PoloniexAPI.get_rate, BitpayAPI.get_rate]
        
        for currency in currencies:
            for api in api_list:
                rate = await api(currency)
                if (rate != None):
                    rates[currency] = float(rate)
                    break

        rates['RUB'] = await self.usd_source.get_rate()
        
        return rates
