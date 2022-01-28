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
        self.stdout.write(f"Looping on {url}")
        abs_folder = self.path + '/data/' + folder + '/'
        if not os.path.isdir(abs_folder):
            os.mkdir(abs_folder)
        response = requests.get(url).json()
        if response["next"] is not None:
            raise ValueError("Got paginated results")
        for result in response['results']:
            item = [part for part in result['url'].split('/') if part != ''][-1]
            filename = abs_folder + item + '.json'
            if not os.path.exists(filename):
                self.stdout.write(f"Fetching {result['url']} (Total : {len(response['results'])})")
                item_response = requests.get(result['url'])
                if item_response.status_code == 404:
                    self.stderr.write(f"SKIPPING 404 on {result['url']}")
                    continue
                data = item_response.json()
                with open(filename, 'w') as file:
                    json.dump(
                        data,
                        file,
                        indent=4,
                    )
                self.stdout.write("SUCCESS " + folder + ' ' + item)
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
            self.loop('https://pokeapi.co/api/v2/' + endpoint + '/?limit=10000', endpoint)
