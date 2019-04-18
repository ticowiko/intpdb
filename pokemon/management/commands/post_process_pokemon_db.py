from django.core.management.base import BaseCommand, CommandError

from pokemon.models import *


class Command(BaseCommand):
    help = 'Post process pokemon db data'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        self.stdout.write('Assigning main form to species...')
        for species in Species.objects.all():
            species.main_form = None
            species.save()
        for pokemon in Pokemon.objects.order_by('-id').all():
            pokemon.species.main_form = pokemon
            pokemon.species.save()

        self.stdout.write('Adding custom data...')
        vikavolt = Species.objects.get(name='vikavolt')
        vikavolt.evolution_condition['location'] = 'special-magnetic-field'
        vikavolt.save()

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

        # TODO : account for abilities in resistances
        # TODO : add breeding moves to evolutions
        # TODO : find better source for encounters
