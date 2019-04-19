import pandas as pd

from django.core.management.base import BaseCommand, CommandError

from collections import OrderedDict

from pokemon.models import *


class Command(BaseCommand):
    help = 'Post process pokemon db data'

    def add_arguments(self, parser):
        parser.add_argument('processors', nargs='*', help='Select processors')

    def handle(self, *args, **options):
        processors = OrderedDict([
            ('main-form', self.main_form),
            ('custom-data', self.custom_data),
            ('type-resistances', self.type_resistances),
            ('breeding-moves', self.breeding_moves),
            ('group-encounters', self.group_encounters),
        ])
        for processor in processors:
            if processor in options['processors'] or not options['processors']:
                processors[processor]()

    def main_form(self):
        self.stdout.write('Assigning main form to species...')
        for species in Species.objects.all():
            species.main_form = None
            species.save()
        for pokemon in Pokemon.objects.order_by('-id').all():
            pokemon.species.main_form = pokemon
            pokemon.species.save()

    def custom_data(self):
        self.stdout.write('Adding custom data...')
        vikavolt = Species.objects.get(name='vikavolt')
        vikavolt.evolution_condition['location'] = 'special-magnetic-field'
        vikavolt.save()

    def type_resistances(self):
        self.stdout.write('Computing type resistances...')
        PokemonTypeEffectiveness.objects.all().delete()
        matrix = TypeEffectiveness.matrix()
        for pokemon in Pokemon.objects.all():
            for attack in matrix:
                effectiveness = matrix[attack][pokemon.primary_type_id]
                if pokemon.secondary_type is not None:
                    effectiveness *= matrix[attack][pokemon.secondary_type_id]
                PokemonTypeEffectiveness.objects.create(
                    pokemon=pokemon,
                    attack_id=attack,
                    effectiveness=effectiveness,
                )

    def breeding_moves(self):
        self.stdout.write('Adding breeding moves to evolutions...')
        for baby in Pokemon.objects.filter(
                id__in=Species.objects.filter(
                    evolution_rank=0,
                ).values(
                    'main_form_id',
                )
        ):
            baby_egg_moves = PokemonMoves.objects.filter(
                pokemon=baby,
                learn_method__name='egg',
            )
            for pokemon in Pokemon.objects.filter(
                species__evolution_chain=baby.species.evolution_chain,
            ).exclude(
                species__evolution_rank=0,
            ).exclude(
                form_name__contains='alola',
            ):
                for move in baby_egg_moves:
                    PokemonMoves.objects.get_or_create(
                        pokemon=pokemon,
                        **{
                            field: getattr(move, field)
                            for field in [
                                field.name
                                for field in move._meta.fields
                                if field.name not in ['pokemon', 'id']
                            ]
                        }
                    )

    def group_encounters(self):
        self.stdout.write('Grouping encounter data...')
        df = pd.DataFrame(list(Encounter.objects.all().values()))
        grouped = df.groupby(
            by=[
                'location_id',
                'pokemon_id',
                'version_id',
                'method_id',
                'condition_id'
            ],
            as_index=False
        ).agg({
            'min_level': 'min',
            'max_level': 'max',
            'chance': 'sum',
        })
        grouped.to_csv('grouped-encounters.csv', index=False)
        return
        grouped = grouped.to_dict('records')
        # Risky but cheap to repopulate
        Encounter.objects.all().delete()
        for group in grouped:
            Encounter.objects.update_or_create(
                **{
                    key: value for key, value in group.items() if key.endswith('id')
                },
                defaults={
                    key: value for key, value in group.items() if not key.endswith('id')
                }
            )

    # TODO : account for abilities in resistances
    # TODO : find better source for encounters
