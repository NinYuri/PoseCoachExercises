from django.core.serializers import serialize
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from .models import Exercise
from .serializers import ExerciseSerializer, ExerciseCreateSerializer, ExerciseListSerializer, ExerciseUpdateSerializer
from .permissions import IsAuthenticated


class ExerciseListCreateView(generics.ListCreateAPIView):
    """
    GET: Lista todos los ejercicios activos
    POST: Crea un nuevo ejercicio
    """
    queryset = Exercise.objects.filter(is_active=True)
    serializer_class = ExerciseListSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExerciseCreateSerializer
        return ExerciseListSerializer


class ExerciseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtiene un ejercicio específico por ID
    PUT/PATCH: Actualiza un ejercicio
    DELETE: Elimina un ejercicio
    """
    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ExerciseUpdateSerializer
        return ExerciseListSerializer

    def perform_destroy(self, instance):
        # Soft delete - cambia is_active a False en lugar de eliminar
        instance.is_active = False
        instance.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exercise_search_by_name(request):
    name = request.query_params.get('name', '').strip()

    if not name:
        return Response(
            {"error": "Necesitas ingresar el nombre del ejercicio"},
            status=status.HTTP_400_BAD_REQUEST
        )

    exercises = Exercise.objects.filter(
        Q(name__icontains=name) & Q(is_active=True)
    )

    serializer = ExerciseListSerializer(exercises, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exercise_list_by_muscle_group(request):
    muscle_group = request.query_params.get('muscle_group', '').strip()

    if not muscle_group:
        return Response(
            {"error": "Necesitas ingresar el músculo a filtrar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validar que el muscle_group esté en las opciones
    valid_groups = [choice[0] for choice in Exercise.MUSCLE_GROUP]
    if muscle_group not in valid_groups:
        return Response(
            {"error": f"Grupo muscular no válido. Opciones: {valid_groups}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    exercises = Exercise.objects.filter(
        muscle_group=muscle_group,
        is_active=True
    )

    serializer = ExerciseListSerializer(exercises, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exercise_list_by_difficulty(request):
    difficulty = request.query_params.get('difficulty', '').strip()

    if not difficulty:
        return Response(
            {"error": "Necesitas ingresar la dificultad a filtrar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    valid_diff = [choice[0] for choice in Exercise.DIFFICULTY]
    if difficulty not in valid_diff:
        return Response(
            {"error": f"Dificultad no válida. Opciones: {valid_diff}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    exercises = Exercise.objects.filter(
        difficulty=difficulty,
        is_active=True
    )
    serializer = ExerciseListSerializer(exercises, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exercise_list_by_equipment(request):
    equipment = request.query_params.get('equipment', '').strip()

    if not equipment:
        return Response(
            {"error": "Necesitas ingresar el equipo disponible"},
            status=status.HTTP_400_BAD_REQUEST
        )

    valid_eqp = [choice[0] for choice in Exercise.EQUIPMENT]
    if equipment not in valid_eqp:
        return Response(
            {"error": f"Equipo no válido. Opciones: {valid_eqp}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    exercises = Exercise.objects.filter(
        equipment=equipment,
        is_active=True
    )

    serializer = ExerciseListSerializer(exercises, many=True)
    return Response(serializer.data)