import uuid

from cloudinary.models import CloudinaryField
from django.db import models

class Exercise(models.Model):
    MUSCLE_GROUP = [
        ('pierna', 'Pierna'),
        ('gluteo', 'Glúteo'),
        ('pecho', 'Pecho'),
        ('espalda', 'Espalda'),
        ('hombros', 'Hombros'),
        ('brazos', 'Brazos'),
        ('abdomen', 'Abdomen'),
        ('cuerpo_completo', 'Cuerpo Completo')
    ]

    DIFFICULTY = [
        ('principiante', 'Principiante'),
        ('intermedio', 'Intermedio'),
        ('avanzado', 'Avanzado')
    ]

    EQUIPMENT = [
        ('mancuernas', 'Mancuernas'),
        ('cuerpo', 'Sólo mi cuerpo'),
        ('bandas', 'Bandas de resistencia'),
        ('gimnasio', 'Máquinas de gimnasio')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=100, null=False, blank=False)
    muscle_group = models.CharField(choices=MUSCLE_GROUP, max_length=50, null=False, blank=False)
    secondary_muscles = models.JSONField(null=True, blank=True)
    difficulty = models.CharField(choices=DIFFICULTY, max_length=20, null=False, blank=False)
    equipment = models.CharField(choices=EQUIPMENT, max_length=50, null=False, blank=False)
    image = CloudinaryField('exercise_image', folder='exercises/', null=True, blank=True, help_text="Imagen ejemplo")

    ideal_angles = models.JSONField(null=False, blank=False)
    common_mistakes = models.JSONField(null=False, blank=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Metodo str
    # Define como se muestra el objeto cuando es convertido a string.
    def __str__(self):
        return f"{self.name} - {self.get_muscle_group_display()} - {self.get_difficulty_display()}"

    class Meta:
        ordering = ['-created_at']  # Los mas recientes primero
        verbose_name = 'Ejercicio'
        verbose_name_plural = 'Ejercicios'