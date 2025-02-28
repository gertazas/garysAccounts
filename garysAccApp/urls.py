from django.urls import path
from .views import trailer_selection, trailer_step2, trailer_summary
from .views_upload import upload_bank 
from .views_sheetprint import views_sheetprint
from .final_views import final_views

urlpatterns = [
    path("", trailer_selection, name="trailer_selection"),
    path("trailer-selection/", trailer_selection, name="trailer_selection"),
    path("step2/", trailer_step2, name="trailer_step2"),
    path("summary/", trailer_summary, name="trailer_summary"),
    path("upload_bank/", upload_bank, name="upload_bank"),
    path("views_sheetprint/", views_sheetprint, name="views_sheetprint"),
    path("final_views/", final_views, name="final_views/"),
]
