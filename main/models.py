from django.db import models
from cryptosite.settings import STATIC_ROOT

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

    def get_receive(self):
        return self.receive.currency_name

    def get_give(self):
        return self.give.currency_name

    def __str__(self) -> str:
        return f'{self.receive.currency_name} {self.give.currency_name}'

""" class Status(models.Model):

    status_name = models.CharField(max_length=32) """

""" class Order(models.Model):

    order_date = models.DateTimeField()
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    give_sum = models.CharField(max_length=32)
    receive_sum = models.CharField(max_length=32)
    give_payment_method = models.CharField(max_length=128)
    receive_payment_method = models.CharField(max_length=128)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    email = models.CharField(max_length=255) """