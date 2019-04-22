from django.core.cache import cache


from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Clear cache'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        cache.clear()
