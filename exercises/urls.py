from django.urls import path
from . import views

urlpatterns = [
    # Listar todos y crear nuevo
    path('all/', views.ExerciseListCreateView.as_view(), name='exercise-list-create'),

    # Obtener, actualizar o eliminar por ID
    path('<uuid:id>/', views.ExerciseDetailView.as_view(), name='exercise-detail'),

    # Buscar por nombre
    path('search/', views.exercise_search_by_name, name='exercise-search'),

    # Filtrar
    path('muscle-group/', views.exercise_list_by_muscle_group, name='exercise-muscle-group'),
    path('difficulty/', views.exercise_list_by_difficulty, name='exercise-difficulty'),
    path('equipment/', views.exercise_list_by_equipment, name='exercise-equipment'),
]