from rest_framework import serializers
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    Handles serialization and deserialization of Review instances,
    including validation for creation and update.
    """
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = [
            'id',
            'reviewer',
            'created_at',
            'updated_at'
        ]
