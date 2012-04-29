import logging
from django.core.management.base import BaseCommand, CommandError
from core.tasks import process_corps

class Command(BaseCommand):
    args = ''
    help = 'Process all corporation wallet journals'

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)
        process_corps()
