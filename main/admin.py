from django.contrib import admin
from django.forms import ModelForm
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
    class Media:
        js = ('admin/js/category_payment_method_select.js',)
    
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
    readonly_fields = ('user', 'number', 'date_time', 'give_sum',
                       'receive_sum', 'give', 'receive',
                       'give_token_standart', 'receive_token_standart',
                       'receive_name', 'receive_address', 'address_to',
                    )
    list_display = ('number', 'date_time',)
    exclude = ('random_string', )