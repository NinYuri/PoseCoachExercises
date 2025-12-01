from rest_framework import serializers
from .models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id',
            'name',
            'muscle_group',
            'secondary_muscles',
            'difficulty',
            'equipment',
            'image_url',
            'ideal_angles',
            'common_mistakes',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ExerciseUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        required=False,
        max_length=100,
        error_messages={
            'required': 'El nombre del ejercicio es obligatorio.',
            'blank': 'El nombre del ejercicio no puede estar vacío.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.',
            'null': 'El nombre del ejercicio no puede ser nulo.'
        }
    )
    muscle_group = serializers.ChoiceField(
        required=False,
        choices=Exercise.MUSCLE_GROUP,
        error_messages={
            'required': 'El grupo muscular es obligatorio.',
            'blank': 'Debes seleccionar un grupo muscular.',
            'null': 'El grupo muscular no puede ser nulo.',
            'invalid_choice': 'Opción de grupo muscular no válida.',
        }
    )
    difficulty = serializers.ChoiceField(
        required=False,
        choices=Exercise.DIFFICULTY,
        error_messages={
            'required': 'La dificultad es obligatoria.',
            'blank': 'Debes seleccionar una dificultad.',
            'null': 'La dificultad no puede ser nula.',
            'invalid_choice': 'Opción de dificultad no válida.',
        }
    )
    equipment = serializers.ChoiceField(
        required=False,
        choices=Exercise.EQUIPMENT,
        error_messages={
            'required': 'El equipo es obligatorio.',
            'blank': 'Debes seleccionar un equipo.',
            'null': 'El equipo no puede ser nulo.',
            'invalid_choice': 'Opción de equipo no válida.',
        }
    )
    secondary_muscles = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        error_messages={
            'invalid_image': 'El archivo debe ser una imagen válida.',
            'invalid': 'El archivo de imagen no es válido.'
        }
    )
    ideal_angles = serializers.JSONField(
        required=False,
        error_messages={
            'required': 'Los ángulos ideales son obligatorios.',
            'invalid': 'Los ángulos ideales deben ser un JSON válido.',
            'null': 'Los ángulos ideales no pueden ser nulos.',
            'blank': 'Los ángulos ideales son obligatorios.'
        }
    )
    common_mistakes = serializers.JSONField(
        required=False,
        allow_null=True,
        error_messages={
            'required': 'Los errores comunes son obligatorios.',
            'invalid': 'Los errores comunes deben ser un JSON válido.',
            'null': 'Los errores comunes no pueden ser nulos.'
        }
    )
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = Exercise
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def validate_name(self, value):
        if value is not None:
            if not value.strip():
                raise serializers.ValidationError("El nombre del ejercicio no puede estar vacío.")

            # Verificar que no exista otro ejercicio activo con el mismo nombre
            if Exercise.objects.filter(
                    name__iexact=value,
                    is_active=True
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya existe otro ejercicio activo con este nombre.")

            return value.strip()
        return value

    def validate_muscle_group(self, value):
        if value is not None:
            valid_choices = [choice[0] for choice in Exercise.MUSCLE_GROUP]
            if value not in valid_choices:
                raise serializers.ValidationError(
                    f"'{value}' no es un grupo muscular válido. "
                    f"Opciones válidas: {', '.join(valid_choices)}"
                )
        return value

    def validate_secondary_muscles(self, value):
        if value is not None:
            valid_muscle_groups = [choice[0] for choice in Exercise.MUSCLE_GROUP]

            invalid_muscles = [muscle for muscle in value if muscle not in valid_muscle_groups]

            if invalid_muscles:
                raise serializers.ValidationError(
                    f"Músculos no válidos: {', '.join(invalid_muscles)}. "
                    f"Opciones válidas: {', '.join(valid_muscle_groups)}"
                )
        return value

    def validate_difficulty(self, value):
        if value is not None:
            valid_choices = [choice[0] for choice in Exercise.DIFFICULTY]
            if value not in valid_choices:
                raise serializers.ValidationError(
                    f"'{value}' no es un nivel de dificultad válido. "
                    f"Opciones válidas: {', '.join(valid_choices)}"
                )
        return value

    def validate_equipment(self, value):
        if value is not None:
            valid_choices = [choice[0] for choice in Exercise.EQUIPMENT]
            if value not in valid_choices:
                raise serializers.ValidationError(
                    f"'{value}' no es un equipo válido. "
                    f"Opciones válidas: {', '.join(valid_choices)}"
                )
        return value

    def validate_image(self, value):
        if value:
            max_size = 5 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError("La imagen no puede pesar más de 5MB.")

            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            extension = value.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise serializers.ValidationError(
                    f"Formato no válido. Formatos permitidos: {', '.join(valid_extensions)}"
                )
        return value

    def validate_ideal_angles(self, value):
        if value is not None and value in [None, {}, []]:
            raise serializers.ValidationError("Los ángulos ideales no pueden estar vacíos.")
        return value

    def validate_common_mistakes(self, value):
        if value is not None and value in [[], ""]:
            raise serializers.ValidationError("Los errores comunes no pueden estar vacíos.")
        return value

    def validate(self, data):
        errors = {}

        # Obtener valores actuales o nuevos
        muscle_group = data.get('muscle_group', getattr(self.instance, 'muscle_group', None))
        secondary_muscles = data.get('secondary_muscles', getattr(self.instance, 'secondary_muscles', []))

        # Solo validar si tenemos ambos valores
        if muscle_group and secondary_muscles and muscle_group in secondary_muscles:
            errors['secondary_muscles'] = f"El músculo principal '{muscle_group}' no puede estar en los secundarios."

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def update(self, instance, validated_data):
        # Actualizar solo los campos que se enviaron en PATCH
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ExerciseCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        error_messages={
            'required': 'El nombre del ejercicio es obligatorio.',
            'blank': 'El nombre del ejercicio no puede estar vacío.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.',
            'null': 'El nombre del ejercicio no puede ser nulo.'
        }
    )
    muscle_group = serializers.ChoiceField(
        choices=Exercise.MUSCLE_GROUP,
        error_messages={
            'required': 'El grupo muscular es obligatorio.',
            'blank': 'Debes seleccionar un grupo muscular.',
            'null': 'El grupo muscular no puede ser nulo.',
            'invalid_choice': 'Opción de grupo muscular no válida.',
        }
    )
    difficulty = serializers.ChoiceField(
        choices=Exercise.DIFFICULTY,
        error_messages={
            'required': 'La dificultad es obligatoria.',
            'blank': 'Debes seleccionar una dificultad.',
            'null': 'La dificultad no puede ser nula.',
            'invalid_choice': 'Opción de dificultad no válida.',
        }
    )
    equipment = serializers.ChoiceField(
        choices=Exercise.EQUIPMENT,
        error_messages={
            'required': 'El equipo es obligatorio.',
            'blank': 'Debes seleccionar un equipo.',
            'null': 'El equipo no puede ser nulo.',
            'invalid_choice': 'Opción de equipo no válida.',
        }
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        error_messages={
            'invalid_image': 'El archivo debe ser una imagen válida.',
            'invalid': 'El archivo de imagen no es válido.'
        }
    )
    ideal_angles = serializers.JSONField(
        error_messages={
            'required': 'Los ángulos ideales son obligatorios.',
            'invalid': 'Los ángulos ideales deben ser un JSON válido.',
            'null': 'Los ángulos ideales no pueden ser nulos.',
            'blank': 'Los ángulos ideales son obligatorios.'
        }
    )
    common_mistakes = serializers.JSONField(
        error_messages={
            'required': 'Los errores comunes son obligatorios.',
            'invalid': 'Los errores comunes deben ser un JSON válido.',
            'null': 'Los errores comunes no pueden ser nulos.'
        }
    )

    def validate_name(self, value):
        if self.instance:
            if Exercise.objects.filter(name__iexact=value, is_active=True).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Lo siento, ya existe otro ejercicio activo con este nombre.")
        else:
            if Exercise.objects.filter(name__iexact=value, is_active=True).exists():
                raise serializers.ValidationError("Lo siento, ya existe un ejercicio activo con este nombre.")

        return value.strip()

    def validate_image(self, value):
        if value:
            # Validar tamaño máximo (5MB)
            max_size = 5 * 1024 * 1024
            if value.size > max_size:
                raise serializers.ValidationError("La imagen no puede pesar más de 5MB.")

            # Validar formatos permitidos
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
            extension = value.name.split('.')[-1].lower()
            if extension not in valid_extensions:
                raise serializers.ValidationError(
                    f"Formato no válido. Formatos permitidos: {', '.join(valid_extensions)}"
                )

        return value

    def validate_secondary_muscles(self, value):
        if value is not None:
            valid_muscle_groups = [choice[0] for choice in Exercise.MUSCLE_GROUP]

            invalid_muscles = [muscle for muscle in value if muscle not in valid_muscle_groups]

            if invalid_muscles:
                raise serializers.ValidationError(
                    f"Músculos no válidos: {', '.join(invalid_muscles)}. "
                    f"Opciones válidas: {', '.join(valid_muscle_groups)}"
                )

        return value

    def validate(self, data):
        errors = {}

        # Validar que muscle_group no esté en secondary_muscles
        muscle_group = data.get('muscle_group')
        secondary_muscles = data.get('secondary_muscles', [])

        if muscle_group and secondary_muscles and muscle_group in secondary_muscles:
            errors['secondary_muscles'] = f"El músculo principal '{muscle_group}' no puede estar en los secundarios."

        # Validar que ideal_angles no esté vacío
        ideal_angles = data.get('ideal_angles')
        if ideal_angles in [None, {}, []]:
            errors['ideal_angles'] = "Los ángulos ideales no pueden estar vacíos."

        # Validar que common_mistakes no esté vacío si se proporciona
        common_mistakes = data.get('common_mistakes')
        if common_mistakes in [[], ""]:
            errors['common_mistakes'] = "Los errores comunes no pueden estar vacíos."

        if errors:
            raise serializers.ValidationError(errors)
        return data

    class Meta:
        model = Exercise
        fields = [
            'name',
            'muscle_group',
            'secondary_muscles',
            'difficulty',
            'equipment',
            'image',
            'ideal_angles',
            'common_mistakes'
        ]


class ExerciseListSerializer(serializers.ModelSerializer):
    muscle_group_display = serializers.CharField(source='get_muscle_group_display', read_only=True)
    secondary_muscles = serializers.SerializerMethodField()
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    equipment_display = serializers.CharField(source='get_equipment_display', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id',
            'name',
            'muscle_group_display',
            'secondary_muscles',
            'difficulty_display',
            'equipment_display',
            'image_url',
        ]

    def get_secondary_muscles(self, obj):
        if not obj.secondary_muscles:
            return []

        MUSCLE_DICT = dict(Exercise.MUSCLE_GROUP)

        return [
            MUSCLE_DICT.get(m, m)
            for m in obj.secondary_muscles
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None