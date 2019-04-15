from django.shortcuts import render
from django.db.models import Q

# noinspection PyUnresolvedReferences
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView

from pokemon.models import *
from pokemon.serializers import *


class VersionPluralView(ListAPIView):
    serializer_class = VersionSerializer
    queryset = Version.objects.select_related(
        'version_group',
        'version_group__generation',
    ).order_by('id').all()


class VersionSingularView(RetrieveAPIView):
    lookup_field = 'name'
    serializer_class = VersionSerializer
    queryset = Version.objects.select_related(
        'version_group',
        'version_group__generation',
    ).all()


class TypeEffectivenessPluralView(ListAPIView):
    serializer_class = TypeEffectivenessSerializer
    queryset = TypeEffectiveness.objects.select_related(
        'attack',
        'defense',
    ).all()


class PokemonPluralView(ListAPIView):
    serializer_class = PokemonSerializer

    def get_queryset(self):
        return Pokemon.versioned.enrich(
            version_name=self.request.GET.get('version'),
            search=self.request.GET.get('search'),
        )[:5]


class PokemonSingularView(RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = PokemonSerializer

    def get_queryset(self):
        return Pokemon.versioned.enrich(Version.objects.get(name=self.request.GET.get('version', 'red'))).all()


def index(request):
    return render(
        request,
        'pokemon/index.html',
    )
