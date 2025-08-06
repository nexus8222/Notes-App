from django.urls import path
from . import views



urlpatterns = [
    path("", views.note_list, name="note_list"),
    path("new/", views.note_create, name="note_create"),
    path("<str:pk>/", views.note_detail, name="note_detail"),
    path("<str:pk>/edit/", views.note_edit, name="note_edit"),
    path("<str:pk>/delete/", views.note_delete, name="note_delete"),
    path("api/notes/", views.api_notes, name="api_notes"),
]
    
