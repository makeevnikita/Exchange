from django.db import models
from cryptosite.settings import STATIC_ROOT
from django.utils import timezone


class TokenStandart(models.Model):

    token_standart = models.CharField(max_length=10)
    commission = models.IntegerField(null=False, default=-1)
    
    def __str__(self) -> str:
        return self.token_standart

class CategoryPaymentMethod(models.Model):

    category_payment_method_name = models.CharField(max_length=255, null=False)

    def __str__(self) -> str:
        return self.category_payment_method_name

class GiveCurrency(models.Model):

    currency_name = models.CharField(max_length=150)
    currency_name_short = models.CharField(max_length=10)
    image = models.FileField(upload_to='images/coins/', null=False)
    category_payment_method = models.ForeignKey(CategoryPaymentMethod, on_delete=models.SET_NULL, null=True)
    token_standart = models.ManyToManyField(TokenStandart)

    def __str__(self) -> str:
        return f'{self.currency_name}'

class ReceiveCurrency(models.Model):
    
    currency_name = models.CharField(max_length=150)
    currency_name_short = models.CharField(max_length=10)
    image = models.FileField(upload_to='images/coins/', null=False)
    category_payment_method = models.ForeignKey(CategoryPaymentMethod, on_delete=models.SET_NULL, null=True)
    token_standart = models.ManyToManyField(TokenStandart)

    def __str__(self) -> str:
        return f'{self.currency_name}'

class ReceiveGiveCurrencies(models.Model):

    class Meta:
        unique_together = (('receive', 'give'),)

    receive = models.ForeignKey(ReceiveCurrency, on_delete=models.CASCADE, null=False)
    give = models.ForeignKey(GiveCurrency, on_delete=models.CASCADE, null=False)
    is_active = models.BooleanField(default=False, null=False)

    def __str__(self) -> str:
        return f'{self.receive.currency_name} {self.give.currency_name}'

class ReceiveAddress(models.Model):
    
    """
        Наши кошельки, на которые клиенты переводят свои деньги
        address - адрес, на который клиент переводит деньги
        currency - валюта
        token_standart - сеть криптовалюты
    """
    
    address = models.CharField(max_length=255, null=False, default='Без адреса')
    currency = models.ForeignKey(ReceiveCurrency, on_delete=models.SET_NULL, null=True)
    token_standart = models.ForeignKey(TokenStandart, on_delete=models.SET_NULL, null=True)

class Order(models.Model):
    """
        Заказы
        number - номер заказа
        date_time - время и дата заказа
        give_sum - сумма, которую отдаёт клиент
        receive_sum - сумма, которую получает клиент
        give - валюта, которую отдаёт клиент
        receive - валюта, которую получает клиент
        give_token_standart - сеть криптовалюты, которую отдаёт клиент
        receive_token_standart - сеть криптовалюты, которую получает клиент
        give_name - имя получателя
        receive_address - адрес, на которуй клиент кидает свои деньги
    """
    
    number = models.IntegerField(null=False, default=0)
    random_string = models.CharField(max_length=200, null=False, default='Нет строки')
    date_time = models.DateTimeField(null=False, default=timezone.now)
    give_sum = models.FloatField(null=False, default=0)
    receive_sum = models.FloatField(null=False, default=0)
    give = models.ForeignKey(GiveCurrency, on_delete=models.SET_NULL, null=True)
    receive = models.ForeignKey(ReceiveCurrency, on_delete=models.SET_NULL, null=True)
    give_token_standart = models.ForeignKey(TokenStandart, on_delete=models.SET_NULL, null=True, related_name='give_token_standart')
    receive_token_standart = models.ForeignKey(TokenStandart, on_delete=models.SET_NULL, null=True, related_name='receive_token_standart')
    give_name = models.CharField(max_length=255, null=False, default='Без имени')
    give_address = models.CharField(max_length=255, null=False, default='Без адреса')
    receive_address = models.ForeignKey(ReceiveAddress, on_delete=models.SET_NULL, null=True)