from rest_framework import serializers

from .models import CustomUser


class CitizenRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'password',
        ]
        read_only_fields = [
            'id',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = CustomUser(
            **validated_data,
            is_admin=False,
            is_member=True
        )
        user.set_password(password)
        user.save()

        return user