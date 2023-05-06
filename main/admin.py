from django.contrib import admin
from django.forms import ModelForm
from django.db import transaction
from typing import Any
from .models import *



@admin.register(TokenStandart)
class TokenStandartAdmin(admin.ModelAdmin):
    pass

class CurrencyForm(ModelForm):
    def clean(self):
        if (self.cleaned_data['category_payment_method'].id == 1):
            currency = [TokenStandart.objects.get(id=1), ]
            self.cleaned_data['token_standart'] = currency
        return super().clean()
    
@admin.register(ReceiveCurrency)
class ReceiveCurrencyAdmin(admin.ModelAdmin):
    form = CurrencyForm
    list_display = ('currency_name', 'currency_name_short')
    
@admin.register(GiveCurrency)
class GiveCurrencyAdmin(ReceiveCurrencyAdmin):
    pass

@admin.register(ReceiveGiveCurrencies)
class ReceiveGiveCurrenciesAdmin(admin.ModelAdmin):
    list_display = ('get_receive_currency_name', 'get_give_currency_name', 'is_active',)

@admin.register(AddressTo)
class AddressToAdmin(admin.ModelAdmin):
    list_display = ('address', 'currency', 'token_standart',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = (
        'status', 'user', 'number', 'date_time', 'give_sum',
        'receive_sum', 'give', 'receive',
        'give_token_standart', 'receive_token_standart',
        'receive_name', 'receive_address', 'address_to',
    )
    list_display = ('number', 'date_time',)
    exclude = ('random_string', )

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        
        if obj.paid == True:

            with transaction.atomic():
                currency = ReceiveCurrency.objects.get(id=obj.receive_id)
                currency.fund -= obj.receive_sum
                currency.save(update_fields=['fund',])
                return super().save_model(request, obj, form, change)
    