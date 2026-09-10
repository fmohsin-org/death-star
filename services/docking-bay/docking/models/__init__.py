"""Data models for the Death Star Docking Bay Management System."""
from django.db import models


class Ship(models.Model):
    """Registry entry for vessels authorized to dock at the Death Star."""

    CLEARANCE_LEVELS = [
        ("standard", "Standard"),
        ("priority", "Priority"),
        ("imperial", "Imperial Command"),
        ("classified", "Classified"),
    ]

    name = models.CharField(max_length=255)
    registration_code = models.CharField(max_length=64, unique=True)
    captain = models.CharField(max_length=255)
    homeport = models.CharField(max_length=255, blank=True)
    cargo_type = models.CharField(max_length=128, blank=True)
    weapons_manifest = models.TextField(blank=True)
    shield_frequency = models.CharField(max_length=32, blank=True)
    is_rebel = models.BooleanField(default=False)
    clearance_level = models.CharField(
        max_length=20, choices=CLEARANCE_LEVELS, default="standard"
    )
    role = models.CharField(max_length=50, default="visitor")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "docking_ships"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} [{self.registration_code}]"


class DockingPermit(models.Model):
    """Permit issued to a ship for docking at a specific bay."""

    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name="permits")
    bay_number = models.IntegerField()
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    purpose = models.CharField(max_length=255)
    authorized_by = models.CharField(max_length=255, default="Automated System")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "docking_permits"

    def __str__(self):
        return f"Permit #{self.pk} — Bay {self.bay_number} — {self.ship.name}"


class CargoManifest(models.Model):
    """Cargo manifest submitted during docking inspection."""

    ship = models.ForeignKey(Ship, on_delete=models.CASCADE, related_name="manifests")
    manifest_url = models.URLField(blank=True)
    manifest_file = models.FileField(upload_to="cargo_manifests/", blank=True)
    contents_summary = models.TextField(blank=True)
    scanned_at = models.DateTimeField(auto_now_add=True)
    inspector = models.CharField(max_length=255, default="Docking Protocol Droid")
    flagged = models.BooleanField(default=False)

    class Meta:
        db_table = "cargo_manifests"

    def __str__(self):
        return f"Manifest for {self.ship.name} — scanned {self.scanned_at}"


class BayAllocation(models.Model):
    """Tracks which docking bay is allocated to which ship."""

    BAY_STATUS_CHOICES = [
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("maintenance", "Under Maintenance"),
        ("restricted", "Restricted Access"),
    ]

    bay_number = models.IntegerField(unique=True)
    bay_name = models.CharField(max_length=128)
    ship = models.ForeignKey(
        Ship, on_delete=models.SET_NULL, null=True, blank=True, related_name="allocations"
    )
    status = models.CharField(
        max_length=20, choices=BAY_STATUS_CHOICES, default="available"
    )
    capacity_tons = models.IntegerField(default=5000)
    last_inspection = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "bay_allocations"

    def __str__(self):
        return f"Bay {self.bay_number}: {self.bay_name} — {self.status}"
