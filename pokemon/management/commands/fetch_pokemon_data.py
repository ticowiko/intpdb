import os
import json
import time
import requests

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Fill pokemon data from poke API'
    path = os.path.dirname(os.path.abspath(__file__))

    def add_arguments(self, parser):
        pass

    def loop(self, url, folder):
        abs_folder = self.path + '/data/' + folder + '/'
        if not os.path.isdir(abs_folder):
            os.mkdir(abs_folder)
        for result in requests.get(url).json()['results']:
            item = [part for part in result['url'].split('/') if part != ''][-1]
            filename = abs_folder + item + '.json'
            if not os.path.exists(filename):
                with open(filename, 'w') as file:
                    json.dump(
                        requests.get(result['url']).json(),
                        file,
                        indent=4,
                    )
                self.stdout.write("SUCCESS " + folder + ' ' + item)
                time.sleep(1)
            else:
                self.stdout.write("SKIPPING " + folder + ' ' + item)

    def handle(self, *args, **options):
        for endpoint in [
            'pokemon-species',
            'pokemon',
            'location-area',
            'evolution-chain',
            'move',
            'machine',
            'encounter-method',
            'ability',
            'version',
            'version-group',
            'generation',
            'move-learn-method',
            'encounter-condition-value',
        ]:
            self.stdout.write("Fetching '" + endpoint + "'...")
            self.loop('https://pokeapi.co/api/v2/' + endpoint + '/', endpoint)
        self.stdout.write("Fixing bugged machines from ORAS...")
        fix = {
            1190: 'tm93',
            1195: 'tm94',
            1200: 'tm95',
            1203: 'tm96',
            1206: 'tm97',
            1209: 'tm98',
            1212: 'tm99',
            1215: 'tm100',
        }
        for machine_id in [1195, 1209, 1190, 1212, 1203, 1206, 1200, 1215]:
            data = json.load(open(self.path+'/data/machine/' + str(machine_id) + '.json', 'r'))
            data['item']['name'] = fix[machine_id]
            data['item']['url'] = None
            json.dump(data, open(self.path+'/data/machine/' + str(machine_id) + '.json', 'w'), indent=4)
