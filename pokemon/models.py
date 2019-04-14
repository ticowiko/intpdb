from django.db.models import *
from django.contrib.postgres.fields import JSONField

from pokemon.managers import PokemonVersionManager


class Generation(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)


class VersionGroup(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    generation = ForeignKey(Generation, on_delete=CASCADE)


class Version(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    version_group = ForeignKey(VersionGroup, on_delete=CASCADE)


class MoveType(Model):
    name = CharField(max_length=50, primary_key=True)
    sprite_url = CharField(max_length=100, blank=True, null=True)


class Ability(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    description = CharField(max_length=250)


class EvolutionChain(Model):
    id = IntegerField(primary_key=True)


class Species(Model):
    number = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    generation = ForeignKey(Generation, on_delete=CASCADE)
    main_form = OneToOneField('Pokemon', on_delete=CASCADE, blank=True, null=True, related_name='defined_species')
    evolves_from = ForeignKey('Species', on_delete=CASCADE, related_name='evolves_into', blank=True, null=True)
    evolution_level = IntegerField(blank=True, null=True)
    evolution_condition = JSONField(blank=True, null=True)
    evolution_chain = ForeignKey(EvolutionChain, on_delete=CASCADE, blank=True, null=True)
    evolution_rank = IntegerField(blank=True, null=True)


class Pokemon(Model):
    id = IntegerField(primary_key=True)
    species = ForeignKey(Species, on_delete=CASCADE)
    form_name = CharField(max_length=50, unique=True)
    primary_type = ForeignKey(MoveType, on_delete=CASCADE, related_name='primary_typed_pokemon')
    secondary_type = ForeignKey(MoveType, on_delete=CASCADE, blank=True, null=True, related_name='secondary_typed_pokemon')
    sprite_url = CharField(max_length=100, blank=True, null=True)
    weight = IntegerField()
    hp = IntegerField()
    attack = IntegerField()
    defense = IntegerField()
    special_attack = IntegerField()
    special_defense = IntegerField()
    speed = IntegerField()

    # Managers
    objects = Manager()
    versioned = PokemonVersionManager()

    class Meta:
        unique_together = (('species', 'form_name'),)


class PokemonAbility(Model):
    pokemon = ForeignKey(Pokemon, on_delete=CASCADE)
    ability = ForeignKey(Ability, on_delete=CASCADE)
    hidden = BooleanField()

    class Meta:
        unique_together = (('pokemon', 'ability'),)


class TypeEffectiveness(Model):
    attack = ForeignKey(MoveType, on_delete=CASCADE, related_name='attack_effectiveness')
    defense = ForeignKey(MoveType, on_delete=CASCADE, related_name='defense_effectiveness')
    effectiveness = FloatField()

    class Meta:
        unique_together = (('attack', 'defense'),)


class MoveCategory(Model):
    # Vars
    PHYSICAL = 'PH'
    SPECIAL = 'SP'
    STATUS = 'ST'
    # DB columns
    name = CharField(max_length=50, primary_key=True,
                     choices=[
                         (PHYSICAL, 'Physical'),
                         (SPECIAL, 'Special'),
                         (STATUS, 'Status'),
                     ])
    sprite_url = CharField(max_length=100, blank=True, null=True)


class Move(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    description = CharField(max_length=200)
    type = ForeignKey(MoveType, on_delete=CASCADE)
    category = ForeignKey(MoveCategory, on_delete=CASCADE)
    power = IntegerField(null=True, blank=True)
    accuracy = IntegerField(null=True, blank=True)
    pp = IntegerField()
    priority = IntegerField()


class MoveMachine(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50)
    version_group = ForeignKey(VersionGroup, on_delete=CASCADE)
    move = ForeignKey(Move, on_delete=CASCADE)

    class Meta:
        unique_together = (
            ('name', 'version_group'),
            ('move', 'version_group'),
        )


class Location(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)


class EncounterMethod(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    sprite_url = CharField(max_length=100, blank=True, null=True)


class EncounterCondition(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    sprite_url = CharField(max_length=100, blank=True, null=True)


class EncounterRate(Model):
    location = ForeignKey(Location, on_delete=CASCADE)
    method = ForeignKey(EncounterMethod, on_delete=CASCADE)
    version = ForeignKey(Version, on_delete=CASCADE)
    rate = IntegerField()

    class Meta:
        unique_together = (('location', 'method', 'version'),)


class Encounter(Model):
    location = ForeignKey(Location, on_delete=CASCADE)
    condition = ForeignKey(EncounterCondition, on_delete=CASCADE, blank=True, null=True)
    pokemon = ForeignKey(Pokemon, on_delete=CASCADE)
    version = ForeignKey(Version, on_delete=CASCADE)
    method = ForeignKey(EncounterMethod, on_delete=CASCADE)
    min_level = IntegerField()
    max_level = IntegerField()
    chance = FloatField()

    class Meta:
        unique_together = (('location', 'pokemon', 'version', 'method', 'condition', 'min_level', 'max_level'),)


class MoveLearnMethod(Model):
    id = IntegerField(primary_key=True)
    name = CharField(max_length=50, unique=True)
    sprite_url = CharField(max_length=200, blank=True, null=True)


class PokemonMoves(Model):
    pokemon = ForeignKey(Pokemon, on_delete=CASCADE)
    version_group = ForeignKey(VersionGroup, on_delete=CASCADE)
    move = ForeignKey(Move, on_delete=CASCADE)
    learn_method = ForeignKey(MoveLearnMethod, on_delete=CASCADE)
    level = IntegerField(blank=True, null=True)
    tm = ForeignKey(MoveMachine, on_delete=CASCADE, blank=True, null=True)

    class Meta:
        unique_together = (('pokemon', 'version_group', 'move', 'learn_method', 'level'),)
