import re

from rest_framework import serializers

from pokemon.models import *


def model_serializer_factory(cls):
    class Ret(serializers.ModelSerializer):
        class Meta:
            model = cls
            fields = '__all__'
    return Ret


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class TypeEffectivenessSerializer(serializers.ModelSerializer):
    attack = model_serializer_factory(MoveType)()
    defense = model_serializer_factory(MoveType)()

    class Meta:
        model = TypeEffectiveness
        fields = '__all__'


class PokemonTypeEffectivenessSerializer(serializers.ModelSerializer):
    attack = model_serializer_factory(MoveType)()

    class Meta:
        model = PokemonTypeEffectiveness
        fields = '__all__'


class VersionGroupSerializer(serializers.ModelSerializer):
    generation = model_serializer_factory(Generation)()

    class Meta:
        model = VersionGroup
        fields = '__all__'


class VersionSerializer(serializers.ModelSerializer):
    version_group = VersionGroupSerializer()

    class Meta:
        model = Version
        fields = '__all__'


class EncounterPokemonSerializer(serializers.ModelSerializer):
    location = model_serializer_factory(Location)()
    condition = model_serializer_factory(EncounterCondition)()
    method = model_serializer_factory(EncounterMethod)()

    class Meta:
        model = Encounter
        fields = '__all__'


class MoveSerializer(serializers.ModelSerializer):
    type = model_serializer_factory(MoveType)()
    category = serializers.CharField(source='category.get_name_display')

    class Meta:
        model = Move
        fields = '__all__'


class PokemonMoveSerializer(serializers.ModelSerializer):
    move = MoveSerializer()
    learn_method = model_serializer_factory(MoveLearnMethod)()
    tm = model_serializer_factory(MoveMachine)()

    class Meta:
        model = PokemonMoves
        fields = '__all__'


class PokemonEvoInfoSerializer(serializers.ModelSerializer):
    version_encounters = EncounterPokemonSerializer(many=True)
    primary_type = model_serializer_factory(MoveType)()
    secondary_type = model_serializer_factory(MoveType)()

    class Meta:
        model = Pokemon
        fields = tuple(
            field.name for field in Pokemon._meta.fields
        ) + (
            'version_encounters',
        )


class SpeciesEvoInfoSerializer(serializers.ModelSerializer):
    evo_summary = serializers.SerializerMethodField()
    main_form = PokemonEvoInfoSerializer()

    def get_evo_summary(self, obj):
        if not obj.evolution_condition:
            return None
        ret = []
        for key, val in obj.evolution_condition.items():
            if not val or key == 'trigger':
                continue
            if isinstance(val, bool):
                ret.append(key)
            elif isinstance(val, dict) and 'name' in val:
                ret.append(key + ': ' + val['name'])
            else:
                ret.append(key + ': ' + str(val))
        return [' '.join([term.capitalize() for term in re.split('[ _-]', item) if term]) for item in ret]

    class Meta:
        model = Species
        fields = tuple(
            field.name for field in Species._meta.fields
        ) + (
            'evo_summary',
        )


class EvolutionChainSerializer(serializers.ModelSerializer):
    species_set = SpeciesEvoInfoSerializer(many=True)

    class Meta:
        model = EvolutionChain
        fields = ('id', 'species_set',)


class SpeciesSerializer(serializers.ModelSerializer):
    evolution_chain = EvolutionChainSerializer()

    class Meta:
        model = Species
        fields = ('number', 'name', 'generation', 'evolution_chain',)


class PokemonAbilitySerializer(serializers.ModelSerializer):
    ability = model_serializer_factory(Ability)()

    class Meta:
        model = PokemonAbility
        fields = '__all__'


class PokemonVersionEnrichedSerializer(serializers.ModelSerializer):
    version_moves = PokemonMoveSerializer(many=True)
    version_encounters = EncounterPokemonSerializer(many=True)
    species = SpeciesSerializer()
    primary_type = model_serializer_factory(MoveType)()
    secondary_type = model_serializer_factory(MoveType)()
    pokemonability_set = PokemonAbilitySerializer(many=True)
    pokemontypeeffectiveness_set = PokemonTypeEffectivenessSerializer(many=True)

    class Meta:
        model = Pokemon
        fields = tuple(
            field.name for field in Pokemon._meta.fields
        ) + (
            'version_moves',
            'version_encounters',
            'pokemonability_set',
            'pokemontypeeffectiveness_set',
        )


class PokemonSerializer(serializers.ModelSerializer):
    primary_type = model_serializer_factory(MoveType)()
    secondary_type = model_serializer_factory(MoveType)()

    class Meta:
        model = Pokemon
        fields = '__all__'


class EncounterLocationSerializer(serializers.ModelSerializer):
    condition = model_serializer_factory(EncounterCondition)()
    method = model_serializer_factory(EncounterMethod)()
    pokemon = PokemonSerializer()

    class Meta:
        model = Encounter
        fields = '__all__'


class EncounterRateSerializer(serializers.ModelSerializer):
    method = model_serializer_factory(EncounterMethod)()

    class Meta:
        model = Encounter
        fields = '__all__'


class LocationSerializer(serializers.ModelSerializer):
    version_encounters = EncounterLocationSerializer(many=True)
    version_encounter_rates = EncounterRateSerializer(many=True)

    class Meta:
        model = Location
        fields = tuple(
            field.name for field in Location._meta.fields
        ) + (
            'version_encounters',
            'version_encounter_rates',
        )


class SpeciesPokemonListSerializer(serializers.ModelSerializer):
    pokemon_set = PokemonSerializer(many=True)

    class Meta:
        model = Species
        fields = tuple(
            field.name for field in Species._meta.fields
        ) + (
            'pokemon_set',
        )


class GenerationPokemonListSerializer(serializers.ModelSerializer):
    species_set = SpeciesPokemonListSerializer(many=True)

    class Meta:
        model = Generation
        fields = tuple(
            field.name for field in Generation._meta.fields
        ) + (
            'species_set',
        )
