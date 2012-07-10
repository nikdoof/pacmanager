import logging
import datetime
import calendar

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import utc, now

from core.models import Transaction, MonthTotal

class Command(BaseCommand):
    args = ''
    help = 'Charge all outstand months for corporations'

    def handle(self, *args, **options):

        for total in MonthTotal.objects.filter(charged=False):
            if datetime.datetime(total.year, total.month, calendar.monthrange(total.year, total.month)[1], 23, 59, 59) < now():
                print "Charging %s - %s/%s" % (total.corporation, total.year, total.month)
                total.corporation.balance -= Decimal(str(self.object.fees_due))
                total.charged = True

                total.save()
                total.corporation.save()

                Transaction.objects.create(corporation=total.corporation, type=Transaction.TRANSACTION_TYPE_CHARGE, value=Decimal(str(-total.fees_due)), comment="Charges for period %s-%s" % (total.year, total.month))
