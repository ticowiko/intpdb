from django.urls import include, re_path

from pokemon.views import *


apipatterns = [
    re_path('^pokemon/$', PokemonPluralView.as_view()),
    re_path('^pokemon/(?P<form_name>.+)/$', PokemonSingularView.as_view()),
    re_path('^versions/$', VersionPluralView.as_view()),
    re_path('^versions/(?P<name>.+)/$', VersionSingularView.as_view()),
    re_path('^type_effectiveness/$', TypeEffectivenessPluralView.as_view()),
    re_path('^type_effectiveness/(?P<attack>.+)/(?P<defense>.+)/$', TypeEffectivenessSingularView.as_view()),
    re_path('^locations/$', LocationPluralView.as_view()),
    re_path('^locations/(?P<name>.+)/$', LocationSingularView.as_view()),
    re_path('^autocomplete/$', AutoCompleteView.as_view()),
]


urlpatterns = [
    re_path('^api/', include(apipatterns)),
    re_path('^$', index, name='index'),
    re_path('^coverage/$', coverage, name='coverage'),
]
