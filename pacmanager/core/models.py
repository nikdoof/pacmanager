from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4
import logging
from eveapi import EVEAPIConnection, Error

from django.db import models
from django.utils.timezone import utc
from django.contrib.auth.models import User

from .managers import CorporationManager


class Setting(models.Model):
    key = models.CharField(max_length=32)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return self.key


class Character(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return u'%s' % self.name


class Corporation(models.Model):
    """Represents a Corporation"""
    name = models.CharField(max_length=255)
    tax_rate = models.PositiveIntegerField('Tax Rate', default=0)
    ceo = models.ForeignKey(Character, related_name='+')
    contact = models.ForeignKey(User, related_name='corporations', null=True, blank=True)
    balance = models.DecimalField('Current Balance', max_digits=25, decimal_places=2, default=0)
    fixed_value = models.DecimalField('Fixed Value Fee', max_digits=25, decimal_places=2, default=None, null=True, blank=True, help_text='Define a fixed fee to charge instead of a pro-rata of tax income')

    last_transaction = models.BigIntegerField('Last Transaction ID', default=0)
    payment_id = models.CharField('Payment ID', max_length=36)
    
    objects = CorporationManager()

    def save(self, *args, **kwargs):
        if self.payment_id is None or self.payment_id == '':
            self.payment_id = str(uuid4())
        return super(Corporation, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.name: 
            return u'%s' % self.name
        return u'%s' % self.pk 


class MonthTotal(models.Model):
    """Holds the monthly fee totals for a corporation"""
    year = models.PositiveIntegerField('Year')
    month = models.PositiveIntegerField('Month')

    corporation = models.ForeignKey(Corporation, related_name='totals')
    tax = models.DecimalField('Total Tax Earned', max_digits=25, decimal_places=2, default=0)
    charged = models.BooleanField('Charged?', default=False)

    @property
    def fees_due(self):
        from .conf import managerconf
        if self.corporation.fixed_value is not None:
            return self.corporation.fixed_value
        threshold = Decimal(managerconf.get('pac.tax_threshold', '200000000'))
        if self.corporation.tax_rate == 0:
            calc = 0
        else:
            calc = (self.tax / self.corporation.tax_rate) * int(managerconf.get('pac.tax_rate', '10'))
        if calc > threshold: return round(calc, 2)
        return threshold

    class Meta:
        ordering = ['-year', '-month']

    def __unicode__(self):
        return u'%s: %s/%s' % (self.corporation.name, self.year, self.month)


class Transaction(models.Model):
    """Transaction tracking"""

    TRANSACTION_TYPE_CHARGE = 1
    TRANSACTION_TYPE_PAYMENT = 2
    TRANSACTION_TYPE_MANUAL = 3

    TRANSACTION_TYPE_CHOICES = (
        (TRANSACTION_TYPE_CHARGE, 'Monthly Charge'),
        (TRANSACTION_TYPE_PAYMENT, 'Fees Payment'),
        (TRANSACTION_TYPE_MANUAL, 'Manual Adjustment'),
    )

    corporation = models.ForeignKey(Corporation, related_name='transactions')
    type = models.PositiveIntegerField(choices=TRANSACTION_TYPE_CHOICES, help_text="The type of transaction")
    date = models.DateTimeField('Transaction Date', auto_now_add=True, help_text="The date/time the transaction was processed")
    value = models.DecimalField('Transaction Value', max_digits=25, decimal_places=2)
    comment = models.CharField(max_length=255)

    class Meta:
         ordering = ['-date']

class Key(models.Model):
    """EVE API Key"""
    corporation = models.ForeignKey(Corporation, related_name='keys', blank=False, null=False)

    keyid = models.BigIntegerField('Key ID', primary_key=True, help_text="Your EVE API key ID")
    vcode = models.CharField('vCode', max_length=64, help_text="Your EVE API key vCode")
    mask = models.BigIntegerField('Access Mask')
    active = models.BooleanField('Active', default=True)
    
    created = models.DateTimeField('Created Date/Time', auto_now_add=True)
    update = models.DateTimeField('Last Update Date/Time', auto_now=True)

    @staticmethod
    def check_access_bit(accessmask, bit):
        """ Returns a bool indicating if the bit is set in the accessmask """
        mask = 1 << bit
        return (accessmask & mask) > 0

    def save(self, *args, **kwargs):
        self.update_api()
        return super(Key, self).save(*args, **kwargs)

    def update_api(self):
        api = EVEAPIConnection(cacheHandler=APICache.DjangoCacheHandler())
        auth = api.auth(keyID=self.keyid, vCode=self.vcode)
        try:
            res = auth.account.APIKeyInfo()
        except Error, e:
            logging.error('Error calling EVE API: %s' % str(e))
            raise e

        if not res.key.type == 'Corporation':
            raise Exception('Invalid key type, got %s, expected Corporation' % res.key.type)

        self.corporation = Corporation.objects.import_corporation(id=res.key.characters[0].corporationID)
        self.mask = int(res.key.accessMask)

        if not Key.check_access_bit(self.mask, 20):
            logging.debug('Access Mask: %s' % mask)
            raise Exception('Invalid access, got %s, expected %s' % (res.key.accessMask, 1048576))
                        
        class Meta:
                permissions = (
                        ('view_all_keys', 'Can view all keys stored'),
                )


class APICache(models.Model):

    key = models.CharField('Cache Key', blank=False, max_length=40)
    cache_until = models.DateTimeField('Cached Until', blank=False)
    document = models.TextField('Document')
    error = models.CharField('API Error', blank=False, null=True, max_length=512)

    class DjangoCacheHandler(object):

        def hash(self, data):
             from hashlib import sha1
             return sha1('-'.join(data)).hexdigest()

        def store(self, host, path, params, doc, obj):
            key = self.hash((host, path, str(params.items())))
            cached = datetime.utcnow().replace(tzinfo=utc) + timedelta(seconds=obj.cachedUntil - obj.currentTime)
            print cached

            try:
                obj = APICache.objects.get(key=key)
            except APICache.DoesNotExist:
                APICache.objects.create(key=key, cache_until=cached, document=doc)
            else:
                obj.cache_until = cached
                obj.document = doc
                obj.save()

        def retrieve(self, host, path, params):
            key = self.hash((host, path, str(params.items())))
            try:
                obj = APICache.objects.get(key=key)
            except APICache.DoesNotExist:
                pass
            else:
                if obj.cache_until >= datetime.utcnow().replace(tzinfo=utc):
                    return obj.document
            return None

    def __unicode__(self):
        return self.key
   
