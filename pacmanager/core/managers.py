import logging

from django.db.models import Manager
from eveapi import EVEAPIConnection, Error

class CorporationManager(Manager):

    def import_corporation(self, id):
        from .models import Corporation, Character, APICache

        api = EVEAPIConnection(cacheHandler=APICache.DjangoCacheHandler())

        try:
            return Corporation.objects.get(pk=id)
        except Corporation.DoesNotExist:
            pass
        try: 
            res = api.corp.CorporationSheet(corporationID=id)
        except Error, e:
            raise Exception('Error creating Corporation: %s' % str(e))
        ceo, created = Character.objects.get_or_create(pk=int(res.ceoID), name=res.ceoName)
        return Corporation.objects.create(pk=int(id), name=res.corporationName, tax_rate=res.taxRate, ceo=ceo)
