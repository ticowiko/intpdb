import os
import csv

from django.core.management.base import BaseCommand

from pokemon.models import *


class Command(BaseCommand):
    help = 'Fill pokemon db with hard coded presets'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Type chart
        self.stdout.write("Filling types and type chart...")
        for line in csv.DictReader(
                open(os.path.dirname(os.path.abspath(__file__)) + '/data/type_effectiveness.csv', 'r')
        ):
            attack, _ = MoveType.objects.get_or_create(name=line['Attacking'].lower())
            del line['Attacking']
            for type_name in line:
                defense, _ = MoveType.objects.get_or_create(name=type_name.lower())
                TypeEffectiveness.objects.get_or_create(
                    attack=attack,
                    defense=defense,
                    defaults={
                        'effectiveness': float(line[type_name]),
                    })
        # Move type
        self.stdout.write("Filling move categories...")
        for move_cat in [MoveCategory.__dict__[e] for e in MoveCategory.__dict__ if e.upper() == e]:
            MoveCategory.objects.get_or_create(
                name=move_cat
            )
