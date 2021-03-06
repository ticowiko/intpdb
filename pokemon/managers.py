from django.db.models import Manager, Prefetch, Q, Count, Case, When, IntegerField


class PokemonVersionManager(Manager):

    def enrich(self, version_name=None, search=None):
        from pokemon.models import PokemonMoves, Encounter, Species, Version, PokemonTypeEffectiveness, PokemonAbility
        if not version_name:
            return self.get_queryset().none()
        version = Version.objects.select_related(
            'version_group__generation',
        ).get(name=version_name)
        filters = Q(species__generation_id__lte=version.version_group.generation.id)
        if search:
            for term in search.split():
                filters = filters & (Q(form_name__istartswith=term) | Q(form_name__icontains='-'+term))
        return self.get_queryset().order_by(
            'species__number',
            'id',
        ).prefetch_related(
            Prefetch(
                'pokemonmoves_set',
                queryset=PokemonMoves.objects.select_related(
                    'learn_method',
                    'tm',
                    'move',
                    'move__type',
                ).filter(
                    version_group=version.version_group,
                ).order_by(
                    'learn_method_id',
                    'level',
                    'tm__id',
                    'move__id',
                ),
                to_attr='version_moves',
            ),
            Prefetch(
                'encounter_set',
                queryset=Encounter.objects.select_related(
                    'location',
                    'method',
                    'condition',
                ).filter(
                    version=version,
                ).order_by(
                    'location_id',
                    'method_id',
                    'condition_id',
                    'min_level',
                ),
                to_attr='version_encounters',
            ),
            Prefetch(
                'species__evolution_chain__species_set',
                queryset=Species.objects.order_by(
                    'evolution_rank',
                ).select_related(
                    'main_form',
                )
            ),
            Prefetch(
                'species__evolution_chain__species_set__main_form__encounter_set',
                queryset=Encounter.objects.select_related(
                    'location',
                    'method',
                    'condition',
                ).filter(
                    version=version,
                ).order_by(
                    'location_id',
                    'method_id',
                    'condition_id',
                    'min_level',
                ),
                to_attr='version_encounters',
            ),
            Prefetch(
                'pokemontypeeffectiveness_set',
                queryset=PokemonTypeEffectiveness.objects.order_by(
                    '-effectiveness',
                    'attack__name',
                ).select_related(
                    'attack',
                )
            ),
            Prefetch(
                'pokemonability_set',
                queryset=PokemonAbility.objects.order_by(
                    'id',
                ).select_related(
                    'ability',
                )
            ),
        ).select_related(
            'primary_type',
            'secondary_type',
            'species',
            'species__main_form',
            'species__main_form__primary_type',
            'species__main_form__secondary_type',
        ).filter(filters)


class LocationVersionManager(Manager):

    def enrich(self, version_name=None, search=None):
        from pokemon.models import PokemonMoves, Encounter, EncounterRate, Species, Version, PokemonTypeEffectiveness, PokemonAbility
        if not version_name:
            return self.get_queryset().none()
        version = Version.objects.select_related(
            'version_group__generation',
        ).get(name=version_name)
        filters = Q(n_version_encounters__gt=0)
        if search:
            for term in search.split():
                try:
                    int(term)
                    filters = filters & Q(name__icontains='-' + term + '-')
                except ValueError:
                    filters = filters & (Q(name__istartswith=term) | Q(name__icontains='-'+term))
        return self.get_queryset().order_by(
            'id',
        ).annotate(
            n_version_encounters=Count(Case(When(encounter__version=version, then=1), output_field=IntegerField()))
        ).prefetch_related(
            Prefetch(
                'encounter_set',
                queryset=Encounter.objects.select_related(
                    'method',
                    'condition',
                    'pokemon',
                    'pokemon__primary_type',
                    'pokemon__secondary_type',
                ).filter(
                    version=version,
                ).order_by(
                    'method_id',
                    'condition_id',
                    'pokemon_id',
                    'min_level',
                ),
                to_attr='version_encounters',
            )
        ).prefetch_related(
            Prefetch(
                'encounterrate_set',
                queryset=EncounterRate.objects.select_related(
                    'method',
                ).filter(
                    version=version,
                ).order_by(
                    'method_id',
                ),
                to_attr='version_encounter_rates',
            )
        ).filter(filters)
