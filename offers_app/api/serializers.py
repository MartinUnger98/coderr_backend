from rest_framework import serializers
from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the OfferDetail model.
    Used to handle full detail data of individual offer components.
    """

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions',
                  'delivery_time_in_days', 'price', 'features', 'offer_type']


class OfferDetailLinkSerializer(serializers.HyperlinkedModelSerializer):
    """
    Hyperlinked serializer for OfferDetail.
    Provides URL-based referencing to detail objects.
    """

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']
        extra_kwargs = {
            'url': {'view_name': 'offer-details', 'lookup_field': 'id'}
        }


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing offers with minimal detail and user summary.
    Includes calculated fields for minimum price and delivery time.
    """
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        ]

    def get_user_details(self, obj):
        """
        Returns selected fields of the user profile associated with the offer.
        """
        profile = getattr(obj.user, 'profile', None)
        return {
            'first_name': profile.first_name if profile else '',
            'last_name': profile.last_name if profile else '',
            'username': profile.username if profile else obj.user.username
        }


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Offer instances.
    Handles nested creation of OfferDetail items.
    """
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        """
        Ensures that at least three details are provided on offer creation.
        Skipped on PATCH (partial update).
        """
        request = self.context.get('request', None)
        is_patch = request and request.method == 'PATCH'

        if not is_patch and len(value) < 3:
            raise serializers.ValidationError(
                "Ein Angebot muss mindestens 3 Details enthalten.")
        return value

    def create(self, validated_data):
        """
        Creates an offer with nested offer details.
        The user is retrieved from the request context.
        """
        details_data = validated_data.pop('details')
        validated_data.pop('user', None)
        user = self.context['request'].user
        offer = Offer.objects.create(user=user, **validated_data)
        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)

        return offer

    def update(self, instance, validated_data):
        """
        Updates an offer and optionally its related details.
        """
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if details_data:
            self._update_details(instance, details_data)
        return instance
                    
    def _update_details(self, instance, details_data):
        """
        Internal helper to update offer details based on 'offer_type'.
        Matches existing details and updates fields accordingly.
        """
        for detail_data in details_data:
            offer_type = detail_data.get('offer_type')
            if not offer_type:
                continue

            detail_obj = instance.details.filter(offer_type=offer_type).first()
            if detail_obj:
                for field, value in detail_data.items():
                    if field != 'offer_type':
                        setattr(detail_obj, field, value)
                detail_obj.save()



class FileUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading or modifying the image of an offer.
    Also includes timestamps.
    """

    class Meta:
        model = Offer
        fields = ['image', 'created_at', 'updated_at']
        
class OfferRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a single offer with price and delivery time info.
    Excludes user profile summary.
    """
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    details = OfferDetailLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time'
        ]
