import logging
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.utils.timezone import utc

from eveapi import EVEAPIConnection, Error, Rowset
from .conf import managerconf
from .models import Corporation, APICache, MonthTotal

def import_wallet_journal(corporation_id):
    corp = Corporation.objects.get(pk=corporation_id)
    api = EVEAPIConnection(cacheHandler=APICache.DjangoCacheHandler())

    for key in corp.keys.all():
        auth = api.auth(keyID=key.pk, vCode=key.vcode)
        
        def get_records(corp=None, fromID=None, rowCount=2560):
            if fromID and fromID <= corp.last_transaction:
                return None
            print "get_records: ", corp, fromID
            try:
                res = auth.corp.WalletJournal(rowCount=rowCount, fromID=fromID)
            except Error, e:
                print e
            else:
                entries = res.entries.SortedBy('refID', reverse=True)
                if len(entries) == rowCount:
                    rows = get_records(corp, fromID=entries[-1].refID)
                    if rows and len(rows):
                        for row in rows._rows:
                            entries.append(row)
                return entries
                    

        # Process Rows
        rows = get_records(corp).SortedBy('refID', reverse=True)
        print "Total rows: ", len(rows)
        totals = {}
        for record in rows:
            if int(record.refID) > corp.last_transaction:
                if int(record.refTypeID) in getattr(settings, 'PAC_TAX_REFIDS', [85, 99]):
                    print record.refID, int(record.refTypeID), record.amount
                    dt = datetime.fromtimestamp(record.date).replace(tzinfo=utc)
                    if not totals.has_key('%s-%s' % (dt.year, dt.month)):
                        totals['%s-%s' % (dt.year, dt.month)], created = MonthTotal.objects.get_or_create(corporation=corp, year=dt.year, month=dt.month)
                    if not totals['%s-%s' % (dt.year, dt.month)].charged:
                        totals['%s-%s' % (dt.year, dt.month)].tax += Decimal(str(record.amount))
            else:
                 break
        for t in totals.values():
            t.save()
        corp.last_transaction = rows[0].refID
        corp.save()


def process_corps():
    for corp in Corporation.objects.all():
        if corp.keys.count():
            logging.info('Processing %s' % corp.name)
            import_wallet_journal(corp.id)
            
            
            
def process_pac_wallet():
    paymentid = {}
    for corp in Corporation.objects.all():
        paymentid[corp.payment_id] = corp

    auth = api.auth(keyID=managerconf['payments.keyid'], vCode=managerconf['payments.vcode'])
    try:
        res = auth.corp.WalletJournal(rowCount=2560)
    except Error, e:
        print e

    for record in res.entries:
        if int(record.refID) > managerconf['payments.last_id'] and record.reason.replace('DESC:', '') in paymentid.keys():
            continue
        else:
            break

