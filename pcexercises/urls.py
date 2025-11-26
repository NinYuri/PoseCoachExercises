from django.urls import path, include


urlpatterns = [
    path('exercises/', include('exercises.urls')),
]