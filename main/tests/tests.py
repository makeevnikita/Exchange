from django.test import TestCase
from main import exchangenetwork as network
from main.models import ReceiveCurrency, GiveCurrency, ReceiveGiveCurrencies, TokenStandart, CategoryPaymentMethod 



class ExchangeViewTest(TestCase):

    def test_exchange_view(self):

        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

class ExchangeNetworkTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        
        tokens = ['BIP20', 'Нет сети']
        for token in tokens:
            token_standart = TokenStandart(token_standart = token, commission = 0)
            token_standart.save()

        categories = ['Криптовалюта', 'Банк']
        for category in categories:
            category_payment_method = CategoryPaymentMethod(category_payment_method_name = category)
            category_payment_method.save()

        receive_coins = \
        [{'currency_name': 'Bitcoin', 'currency_name_short': 'BTC', 'image': '', 
        'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Криптовалюта'),
        'token_standart': [TokenStandart.objects.get(token_standart = 'BIP20')]},
        
        {'currency_name': 'Etherium', 'currency_name_short': 'ETH', 'image': '', 
        'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Криптовалюта'),
        'token_standart': [TokenStandart.objects.get(token_standart = 'BIP20')]},

        {'currency_name': 'Сбербанк', 'currency_name_short': 'RUB', 'image': '', 
        'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Банк'),
        'token_standart': [TokenStandart.objects.get(token_standart = 'Нет сети')]}]
        
        for coin in receive_coins:
            receive_coin = ReceiveCurrency(
                                currency_name = coin['currency_name'],
                                currency_name_short = coin['currency_name_short'],
                                image = coin['image'],
                                category_payment_method = coin['category_payment_method'])
            receive_coin.save()
            receive_coin.token_standart.set(coin['token_standart'])
            receive_coin.save()
            
        give_coins = \
        [{'currency_name': 'Сбербанк', 'currency_name_short': 'RUB', 'image': '', 
        'category_payment_method': CategoryPaymentMethod.objects.get(category_payment_method_name = 'Банк'),
        'token_standart': [TokenStandart.objects.get(token_standart = 'Нет сети')]}]
        
        for coin in give_coins:
            give_coin = GiveCurrency(
                                currency_name = coin['currency_name'],
                                currency_name_short = coin['currency_name_short'],
                                image = coin['image'],
                                category_payment_method = coin['category_payment_method'])
            give_coin.save()
            give_coin.token_standart.set(coin['token_standart'])
            give_coin.save()
            

        receive_give_currencies = ReceiveGiveCurrencies(receive = ReceiveCurrency.objects.get(currency_name = 'Bitcoin'),
                                                        give = GiveCurrency.objects.get(currency_name = 'Сбербанк'))
        receive_give_currencies.save()

        receive_give_currencies = ReceiveGiveCurrencies(receive = ReceiveCurrency.objects.get(currency_name = 'Etherium'),
                                                        give = GiveCurrency.objects.get(currency_name = 'Сбербанк'))
        receive_give_currencies.save()

    async def test_get_rates(self):
        
        """
            Запрашивает курс валюты из стороннего API. Если курс равен None, то тест не пройдёт.
        """

        exchange = network.ExchangeClient(network.CurrenciesFromMYSQL, network.CentreBankAPI)
        rates = await exchange.get_rate()
        print(rates.items())

        if (None in rates.values()):
            self.assertTrue(False)
        else:
            self.assertTrue(True)