from django.contrib import admin
from .models import Setting, Character, Corporation, Key, Transaction, MonthTotal, APICache

class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')

class CharacterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class CorporationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact', 'balance')
    readonly_fields = ('name', 'tax_rate', 'ceo', 'balance', 'last_transaction', 'payment_id')


class KeyAdmin(admin.ModelAdmin):
    list_display = ('keyid', 'corporation', 'mask', 'active', 'created', 'update')
    list_filter = ('corporation', 'active')
    readonly_fields = ('keyid', 'vcode', 'mask', 'corporation')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'corporation', 'type', 'value', 'comment')
    readonly_fields = list_display
    date_hierarchy = 'date'
    list_filter = ('corporation', 'type')


class MonthTotalAdmin(admin.ModelAdmin):
    pass

    
class APICacheAdmin(admin.ModelAdmin):
    list_display = ('key', 'cache_until')


admin.site.register(Setting, SettingAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Corporation, CorporationAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(MonthTotal, MonthTotalAdmin)
admin.site.register(APICache, APICacheAdmin)
