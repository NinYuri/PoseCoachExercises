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
    muscles = request.query_params.getlist('muscle_group')

    # Si no vino getlist (solo vino uno con comas)
    if len(muscles) == 1 and ',' in muscles[0]:
        muscles = [m.strip() for m in muscles[0].split(',')]

    if not muscles:
        return Response(
            {"error": "Necesitas ingresar al menos un músculo a filtrar"},
            status=status.HTTP_400_BAD_REQUEST
        )

    valid_groups = [choice[0] for choice in Exercise.MUSCLE_GROUP]
    invalid = [m for m in muscles if m not in valid_groups]

    if invalid:
        return Response(
            {"error": f"Los siguientes grupos no son válidos: {invalid}. Opciones: {valid_groups}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    exercises = Exercise.objects.filter(
        muscle_group__in=muscles,
        is_active=True
    )

    serializer = ExerciseListSerializer(exercises, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exercise_list_by_difficulty(request):
    difficulties = request.query_params.getlist('difficulty')

    if len(difficulties) == 1 and ',' in difficulties[0]:
        difficulties = [d.strip() for d in difficulties[0].split(',')]

    if not difficulties:
        return Response(
            {"error": "Necesitas ingresar al menos una dificultad"},
            status=status.HTTP_400_BAD_REQUEST
        )

    valid_diff = [choice[0] for choice in Exercise.DIFFICULTY]
    invalid = [d for d in difficulties if d not in valid_diff]

    if invalid:
        return Response(
            {"error": f"Dificultades no válidas: {invalid}. Opciones: {valid_diff}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    exercises = Exercise.objects.filter(
        difficulty__in=difficulties,
        is_active=True
    )

    serializer = ExerciseListSerializer(exercises, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exercise_list_by_equipment(request):
    equipments = request.query_params.getlist('equipment')

    if len(equipments) == 1 and ',' in equipments[0]:
        equipments = [e.strip() for e in equipments[0].split(',')]

    if not equipments:
        return Response(
            {"error": "Necesitas ingresar al menos un equipo"},
            status=status.HTTP_400_BAD_REQUEST
        )

    valid_eqp = [choice[0] for choice in Exercise.EQUIPMENT]
    invalid = [e for e in equipments if e not in valid_eqp]

    if invalid:
        return Response(
            {"error": f"Equipos no válidos: {invalid}. Opciones: {valid_eqp}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    exercises = Exercise.objects.filter(
        equipment__in=equipments,
        is_active=True
    )

    serializer = ExerciseListSerializer(exercises, many=True)
    return Response(serializer.data)