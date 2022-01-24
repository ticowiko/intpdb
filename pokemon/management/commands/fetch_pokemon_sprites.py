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
        if not os.path.isdir(self.path + '/data/sprites/'):
            os.mkdir(self.path + '/data/sprites/')
        for filepath in glob.glob(self.path + '/data/pokemon/*.json'):
            self.stdout.write('Working on ' + filepath)
            data = json.load(open(filepath, 'r'))
            if data['sprites']['front_default'] is not None:
                out_path = self.path + '/data/sprites/' + data['sprites']['front_default'].split('/')[-1]
                if not os.path.exists(out_path):
                    open(
                        self.path + '/data/sprites/' + data['sprites']['front_default'].split('/')[-1], 'wb'
                    ).write(
                        requests.get(
                            data['sprites']['front_default']
                        ).content
                    )
                    self.stdout.write("SUCCESS " + out_path)
                else:
                    self.stdout.write("SKIPPING " + out_path)
