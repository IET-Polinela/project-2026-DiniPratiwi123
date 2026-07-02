from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

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
            'is_owner',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'reporter',
            'is_owner',
            'created_at',
            'updated_at',
        ]

    def get_reporter(self, obj):
        request = self.context.get('request')

        if not obj.reporter:
            return 'Warga Anonim'

        if not request or not request.user or not request.user.is_authenticated:
            return 'Warga Anonim'

        if request.query_params.get('tab') == 'feed':
            return 'Warga Anonim'

        if obj.reporter_id == request.user.id:
            return obj.reporter.username

        return 'Warga Anonim'

    def get_is_owner(self, obj):
        request = self.context.get('request')

        if not request or not request.user or not request.user.is_authenticated:
            return False

        return obj.reporter_id == request.user.id

    def validate(self, attrs):
        request = self.context.get('request')
        user = request.user if request else None

        if not user or not user.is_authenticated:
            return attrs

        is_admin = getattr(user, 'is_admin', False) or user.is_superuser

        if self.instance is None:
            if not is_admin:
                attrs['status'] = 'DRAFT'
            return attrs

        if is_admin:
            sent_fields = set(attrs.keys())
            allowed_fields = {'status'}

            if not sent_fields.issubset(allowed_fields):
                raise serializers.ValidationError(
                    'Admin hanya diizinkan mengubah status laporan.'
                )

            return attrs

        if 'status' in attrs and attrs['status'] != self.instance.status:
            raise serializers.ValidationError(
                {
                    'status': 'Citizen tidak diizinkan mengubah status secara langsung. Gunakan endpoint submit.'
                }
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        is_admin = False

        if user and user.is_authenticated:
            is_admin = getattr(user, 'is_admin', False) or user.is_superuser

        if not is_admin:
            validated_data['status'] = 'DRAFT'

        return super().create(validated_data)