from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'title',
            'category',
            'description',
            'location',
            'status',
            'reporter',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'reporter',
            'created_at',
            'updated_at',
        ]

    def get_reporter(self, obj):
        return 'Warga Anonim'

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None

        if not user or not user.is_authenticated:
            return attrs

        is_admin = getattr(user, 'is_admin', False) or user.is_superuser

        # Saat Citizen membuat laporan, status selalu dipaksa menjadi DRAFT.
        if self.instance is None:
            if not is_admin:
                attrs['status'] = 'DRAFT'
            return attrs

        # Admin hanya boleh mengubah field status.
        if is_admin:
            sent_fields = set(attrs.keys())
            allowed_fields = {'status'}

            if not sent_fields.issubset(allowed_fields):
                raise serializers.ValidationError(
                    'Admin hanya diizinkan mengubah status laporan.'
                )

            return attrs

        # Citizen tidak boleh mengubah status lewat PUT/PATCH biasa.
        if 'status' in attrs and attrs['status'] != self.instance.status:
            raise serializers.ValidationError(
                {'status': 'Citizen tidak diizinkan mengubah status secara langsung. Gunakan endpoint submit.'}
            )

        return attrs