import os
import glob
import json
import time
import requests

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Fill pokemon data from poke API'
    path = os.path.dirname(os.path.abspath(__file__))

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for filepath in glob.glob(self.path + '/data/pokemon/*.json'):
            self.stdout.write('Working on ' + filepath)
            data = json.load(open(filepath, 'r'))
            if data['sprites']['front_default'] is not None:
                open(
                    self.path + '/data/sprites/' + data['sprites']['front_default'].split('/')[-1], 'wb'
                ).write(
                    requests.get(
                        data['sprites']['front_default']
                    ).content
                )
