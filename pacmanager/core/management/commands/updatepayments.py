import logging
from django.core.management.base import BaseCommand, CommandError
from core.tasks import process_pac_wallet

class Command(BaseCommand):
    args = ''
    help = 'Process the payments wallet for new payments'

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        process_pac_wallet()
