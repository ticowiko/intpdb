import os
import json
import glob
import time

from collections import OrderedDict

from django.core.management.base import BaseCommand, CommandError

from pokemon.models import *


class GetCacher:

    def __init__(self):
        self.cache = {}

    def get(self, model, **query):
        try:
            key = model.__name__+'_+_'+str(query)
            if key not in self.cache:
                self.cache[key] = model.objects.get(**query)
            return self.cache[key]
        except Exception as e:
            print(f"Failed caching '{model.__class__.__name__}' with query '{query}'.")
            raise e


class Command(BaseCommand):
    help = 'Fill pokemon db with poke API data'
    path = os.path.dirname(os.path.abspath(__file__))
    int_to_gen = {
        1: 'I',
        2: 'II',
        3: 'III',
        4: 'IV',
        5: 'V',
        6: 'VI',
        7: 'VII',
        8: 'VIII',
        9: 'IX',
        10: 'X',
        11: 'XI',
        12: 'XII',
    }
    cacher = GetCacher()

    def add_arguments(self, parser):
        parser.add_argument('items', nargs='*')

    def handle_evo(self, chain, chain_id, depth):
        for evolution in chain['evolves_to']:
            self.stdout.write("Evolving species " + evolution['species']['name'] + "...")
            if len(evolution['evolution_details']) > 1:
                self.stderr.write("Multiple evolutions for " + evolution['species']['name'])
            details = evolution['evolution_details'][0] if evolution['evolution_details'] else {"min_level": None}
            Species.objects.filter(name=evolution['species']['name']).update(
                evolution_chain=EvolutionChain.objects.update_or_create(id=chain_id)[0],
                evolves_from=self.cacher.get(Species, name=chain['species']['name']),
                evolution_level=int(details['min_level']) if details['min_level'] is not None else None,
                evolution_condition=details,
                evolution_rank=depth,
            )
            self.handle_evo(evolution, chain_id, depth+1)

    def process_generation(self, data):
        Generation.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': self.int_to_gen[data['id']]
            }
        )

    def process_version_group(self, data):
        VersionGroup.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
                'generation': self.cacher.get(Generation, id=int(data['generation']['url'].split('/')[-2])),
            }
        )

    def process_version(self, data):
        Version.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
                'version_group': self.cacher.get(VersionGroup, name=data['version_group']['name']),
            }
        )

    def process_species(self, data):
        Species.objects.update_or_create(
            number=data['order'],
            defaults={
                'name': data['name'],
                'generation': self.cacher.get(Generation, id=[e for e in data['generation']['url'].split('/') if e][-1]),
            }
        )

    def process_evo(self, data):
        Species.objects.filter(name=data['chain']['species']['name']).update(
            evolution_chain=EvolutionChain.objects.update_or_create(id=data['id'])[0],
            evolution_rank=0,
        )
        self.handle_evo(data['chain'], data['id'], 1)

    def process_ability(self, data):
        if not data['is_main_series']:
            self.stderr.write("Skipping " + data['name'] + ' (' + str(data['id']) + ')')
            return
        Ability.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
                'description': [
                    text['flavor_text']
                    for text in data['flavor_text_entries']
                    if text['language']['name'] == 'en'
                ][0],
            }
        )

    def process_move(self, data):
        if data['id'] >= 10000:
            self.stderr.write('Skipping move ' + str(data['id']) + ' ...')
            return
        Move.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
                'description': [
                    text['flavor_text']
                    for text in data['flavor_text_entries']
                    if text['language']['name'] == 'en'
                ][0],
                'type': self.cacher.get(MoveType, name=data['type']['name']),
                'category': self.cacher.get(MoveCategory, name=data['damage_class']['name'][:2].upper()),
                'power': data['power'],
                'accuracy': data['accuracy'],
                'pp': data['pp'],
                'priority': data['priority'],
                'effect_chance': data['effect_chance'],
            }
        )

    def process_machine(self, data):
        MoveMachine.objects.update_or_create(
            id=data['id'],
            defaults={
                'move': self.cacher.get(Move, name=data['move']['name']),
                'version_group': self.cacher.get(VersionGroup, name=data['version_group']['name']),
                'name': data['item']['name'].upper(),
            }
        )

    def process_move_learn_method(self, data):
        MoveLearnMethod.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
            }
        )

    def process_pokemon(self, data):
        move_types = {move_type['slot']: move_type['type']['name'] for move_type in data['types']}
        if set(move_types.keys()) not in [{1, 2}, {1}]:
            raise CommandError('ERROR Got move type slots ' + str(move_types.keys()))
        stats = {stat['stat']['name'].replace('-', '_'): stat['base_stat'] for stat in data['stats']}
        if set(stats.keys()) != {'speed', 'special_defense', 'special_attack', 'defense', 'attack', 'hp'}:
            raise CommandError('ERROR Got stats ' + str(stats.keys()))
        pokemon, _ = Pokemon.objects.update_or_create(
            id=data['id'],
            defaults={
                'species': self.cacher.get(Species, name=data['species']['name']),
                'form_name': data['name'],
                'primary_type': self.cacher.get(MoveType, name=move_types[1]),
                'secondary_type': self.cacher.get(MoveType, name=move_types[2]) if move_types.get(2) is not None else None,
                'sprite_url': data['sprites']['front_default'],
                'weight': data['weight'],
                **stats,
            }
        )
        for ability in data['abilities']:
            PokemonAbility.objects.update_or_create(
                pokemon=pokemon,
                ability=self.cacher.get(Ability, name=ability['ability']['name']),
                defaults={
                    'hidden': ability['is_hidden'],
                }
            )
        for move_data in data['moves']:
            move = self.cacher.get(Move, name=move_data['move']['name'])
            for version_move in move_data['version_group_details']:
                # self.stdout.write(
                #     "Teaching " + pokemon.form_name +
                #     " from " + version_move['version_group']['name'] +
                #     " move " + move.name
                # )
                PokemonMoves.objects.update_or_create(
                    pokemon=pokemon,
                    version_group=self.cacher.get(VersionGroup, name=version_move['version_group']['name']),
                    move=move,
                    defaults={
                        'learn_method': self.cacher.get(MoveLearnMethod, name=version_move['move_learn_method']['name']),
                        'level': version_move[
                            'level_learned_at'
                        ] if version_move['move_learn_method']['name'] == 'level-up' else None,
                        'tm': self.cacher.get(
                            MoveMachine, move=move, version_group__name=version_move['version_group']['name']
                        ) if version_move['move_learn_method']['name'] == 'machine' else None,
                    }
                )

    def process_encounter_condition_value(self, data):
        EncounterCondition.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
            }
        )

    def process_encounter_method(self, data):
        EncounterMethod.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
            }
        )

    def process_location_area(self, data):
        location, _ = Location.objects.update_or_create(
            id=data['id'],
            defaults={
                'name': data['name'],
            }
        )
        for encounter_method_rate in data['encounter_method_rates']:
            encounter_method = self.cacher.get(EncounterMethod, name=encounter_method_rate['encounter_method']['name'])
            for version_detail in encounter_method_rate['version_details']:
                EncounterRate.objects.update_or_create(
                    location=location,
                    method=encounter_method,
                    version=self.cacher.get(Version, name=version_detail['version']['name']),
                    defaults={
                        'rate': version_detail['rate'],
                    }
                )
        for pokemon_encounter in data['pokemon_encounters']:
            pokemon = self.cacher.get(Pokemon, form_name=pokemon_encounter['pokemon']['name'])
            for version_detail in pokemon_encounter['version_details']:
                version = self.cacher.get(Version, name=version_detail['version']['name'])
                # TODO : allow for multiple conditions (requires change in data model)
                for encounter_detail in version_detail['encounter_details']:
                    if len(encounter_detail['condition_values']) > 1:
                        self.stderr.write("Found encounter with multiple conditions, using first condition...")
                        condition = self.cacher.get(
                            EncounterCondition, name=encounter_detail['condition_values'][0]['name']
                        )
                    elif len(encounter_detail['condition_values']) == 1:
                        condition = self.cacher.get(
                            EncounterCondition, name=encounter_detail['condition_values'][0]['name']
                        )
                    else:
                        condition = None
                    Encounter.objects.update_or_create(
                        location=location,
                        condition=condition,
                        pokemon=pokemon,
                        version=version,
                        method=self.cacher.get(EncounterMethod, name=encounter_detail['method']['name']),
                        min_level=encounter_detail['min_level'],
                        max_level=encounter_detail['max_level'],
                        defaults={
                            'chance': encounter_detail['chance'],
                        }
                    )

    def loop(self, folder, function):
        filepaths = sorted(
            glob.glob(self.path + '/data/' + folder + '/*.json'),
            key=lambda x: int(x.split('/')[-1].split('.')[0])
        )
        for filepath in filepaths:
            data = json.load(open(filepath, 'r'))
            now = time.time()
            self.stdout.write(
                "Processing " + folder +
                " (" + str(data['id']) + "/" + str(len(filepaths)) + ")" +
                " %.3f/%.3f" % (time.time() - self.start, now - self.last)
            )
            self.last = time.time()
            self.stdout.flush()
            function(data)

    def process(self, items):
        self.start = time.time()
        self.last = self.start
        loops = OrderedDict([
            ('generation', self.process_generation),
            ('version-group', self.process_version_group),
            ('version', self.process_version),
            ('pokemon-species', self.process_species),
            ('evolution-chain', self.process_evo),
            ('ability', self.process_ability),
            ('move', self.process_move),
            ('machine', self.process_machine),
            ('move-learn-method', self.process_move_learn_method),
            ('pokemon', self.process_pokemon),
            ('encounter-condition-value', self.process_encounter_condition_value),
            ('encounter-method', self.process_encounter_method),
            ('location-area', self.process_location_area),
        ])
        for item in items or loops:
            self.loop(item, loops[item])

    def handle(self, *args, **options):
        self.process(options['items'])
