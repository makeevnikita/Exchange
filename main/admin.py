from django.contrib import admin
from .models import *

@admin.register(TokenStandart)
class TokenStandartAdmin(admin.ModelAdmin):
    pass

@admin.register(ReceiveCurrency)
class ReceiveCurrencyAdmin(admin.ModelAdmin):
    pass

@admin.register(GiveCurrency)
class GiveCurrencyAdmin(admin.ModelAdmin):
    list_display = ('currency_name', 'currency_name_short')

@admin.register(ReceiveGiveCurrencies)
class ReceiveGiveCurrenciesAdmin(admin.ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(ReceiveAddress)
class ReceiveAddressAdmin(admin.ModelAdmin):
    pass