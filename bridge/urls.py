from django.urls import path

from . import views

app_name = 'bridge'

urlpatterns = [
    path('', views.consumer, name='consumer'),
    path('grade', views.grade, name='grade'),
    path('provider', views.moodle_provider)
]