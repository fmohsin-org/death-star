"""Serializers for the Docking Bay API."""
from rest_framework import serializers
from docking.models import Ship, DockingPermit, CargoManifest, BayAllocation


class ShipSerializer(serializers.ModelSerializer):
    """Serializer for ship registration and retrieval."""

    class Meta:
        model = Ship
        fields = "__all__"


class ShipRegistrationSerializer(serializers.ModelSerializer):
    """Handles new ship registration intake."""

    class Meta:
        model = Ship
        fields = "__all__"
        extra_kwargs = {
            "is_rebel": {"required": False},
            "clearance_level": {"required": False},
            "role": {"required": False},
            "weapons_manifest": {"required": False},
            "shield_frequency": {"required": False},
        }


class DockingPermitSerializer(serializers.ModelSerializer):
    ship_name = serializers.CharField(source="ship.name", read_only=True)

    class Meta:
        model = DockingPermit
        fields = "__all__"


class CargoManifestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargoManifest
        fields = "__all__"


class BayAllocationSerializer(serializers.ModelSerializer):
    ship_name = serializers.CharField(source="ship.name", read_only=True)

    class Meta:
        model = BayAllocation
        fields = "__all__"


class ClearanceCheckSerializer(serializers.Serializer):
    """Input for Imperial directory clearance verification."""
    officer_name = serializers.CharField(max_length=255)
    unit = serializers.CharField(max_length=128, required=False, default="*")
    clearance_code = serializers.CharField(max_length=64)
