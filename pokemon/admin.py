from django.contrib import admin
from django.apps import apps


app_names = [
    'pokemon',
]


for app_name in app_names:
    for model_name, model in apps.get_app_config(app_name).models.items():
        admin.site.register(model)
