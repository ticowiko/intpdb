from django.core.management.base import BaseCommand, CommandError

from pokemon.models import *


class Command(BaseCommand):
    help = 'Post process pokemon db data'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Assign main form to species
        for species in Species.objects.all():
            species.main_form = None
            species.save()
        for pokemon in Pokemon.objects.order_by('-id').all():
            pokemon.species.main_form = pokemon
            pokemon.species.save()
        # Custom data
        vikavolt = Species.objects.get(name='vikavolt')
        vikavolt.evolution_condition['location'] = 'special-magnetic-field'
        vikavolt.save()
        # TODO : add breeding moves to evolutions
        # TODO : add all moves to non primary forms
        # TODO : find better source for encounters
