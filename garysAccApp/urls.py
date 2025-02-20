from django.urls import path
from .views import trailer_selection, trailer_step2, trailer_summary

urlpatterns = [
    path("trailer-selection/", trailer_selection, name="trailer_selection"),
    path("trailer-selection/step2/", trailer_step2, name="trailer_step2"),
    path("trailer-selection/summary/", trailer_summary, name="trailer_summary"),
]
