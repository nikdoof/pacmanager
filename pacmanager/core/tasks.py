import logging
from datetime import datetime
from decimal import Decimal
from django.utils.timezone import utc

from eveapi import EVEAPIConnection, Error, Rowset
from .conf import managerconf
from .models import Corporation, APICache, MonthTotal, Transaction

def import_wallet_journal(corporation_id):
    corp = Corporation.objects.get(pk=corporation_id)
    api = EVEAPIConnection(cacheHandler=APICache.DjangoCacheHandler())

    for key in corp.keys.all():
        auth = api.auth(keyID=key.pk, vCode=key.vcode)
        
        def get_records(corp=None, fromID=None, rowCount=2560):
            if fromID and fromID <= corp.last_transaction:
                return None
            #print "get_records: ", corp, fromID
            try:
                res = auth.corp.WalletJournal(rowCount=rowCount, fromID=fromID)
            except Error, e:
                print e
            else:
                if type(res.entries) == str: return None
                entries = res.entries.SortedBy('refID', reverse=True)
                if len(entries) == rowCount:
                    rows = get_records(corp, fromID=entries[-1].refID)
                    if rows and len(rows):
                        for row in rows._rows:
                            entries.append(row)
                return entries
                    

        # Process Rows
        rows = get_records(corp)
        if rows is None: return
        rows = rows.SortedBy('refID', reverse=True)
        logging.info("Total rows: %s" % len(rows))
        totals = {}
        for record in rows:
            if int(record.refID) > corp.last_transaction:
                if int(record.refTypeID) in [int(x.strip()) for x in managerconf.get('pac.tax_refids', '85,99').split(',')]:
                    #print record.refID, int(record.refTypeID), record.amount
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

    if not 'payments.keyid' in managerconf or not 'payments.vcode' in managerconf:
        logging.error('No payments Key ID / vCode set!')
        return 

    api = EVEAPIConnection(cacheHandler=APICache.DjangoCacheHandler())
    auth = api.auth(keyID=managerconf['payments.keyid'], vCode=managerconf['payments.vcode'])
    try:
        entries = auth.corp.WalletJournal(rowCount=2560).entries.SortedBy('refID', reverse=True)
    except Error, e:
        logging.error('Error importing Payments wallet: %s' % e)
        return

    if not 'payments.last_id' in managerconf:
        managerconf['payments.last_id'] = 0

    logging.info('Last processed Ref ID: %s' % managerconf['payments.last_id'])
    for record in entries:
        if int(record.refID) > int(managerconf['payments.last_id']):
            res = record.reason.replace('DESC: ', '').strip()
            if paymentid.has_key(res):
                corp = paymentid[res]
                logging.info('Payment Found, %s, Ref ID %s, Amount: %s ISK' % (corp.name, record.refID, record.amount))
                # Payment found
                trans = Transaction.objects.create(corporation=corp, value=Decimal(str(record.amount)), comment="Wallet Ref ID %s" % record.refID, type=Transaction.TRANSACTION_TYPE_PAYMENT)
                corp.balance += Decimal(str(record.amount))
                corp.save()
        else:
            break

    managerconf['payments.last_id'] = entries[0].refID
