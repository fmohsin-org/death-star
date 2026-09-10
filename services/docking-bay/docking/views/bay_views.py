"""
Docking Bay API views — ship registration, permits, cargo, and bay management.
"""
import yaml
import requests
import ldap3
from datetime import timedelta

from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.template import Template, Context
from django.utils import timezone
from django.core.files.storage import default_storage

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

from docking.models import Ship, DockingPermit, CargoManifest, BayAllocation
from docking.serializers import (
    ShipSerializer,
    ShipRegistrationSerializer,
    DockingPermitSerializer,
    ClearanceCheckSerializer,
)
from docking.utils.bay_utils import calculate_cargo_weight, fetch_remote_manifest


@api_view(["GET"])
def ship_list(request):
    """Search registered ships by name. Supports partial matching for hangar ops."""
    name_filter = request.query_params.get("name", "")
    if name_filter:
        ships = Ship.objects.extra(
            where=[f"name LIKE '%%{name_filter}%%'"]
        )
    else:
        ships = Ship.objects.all()
    serializer = ShipSerializer(ships, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def register_ship(request):
    """Register a new vessel in the Death Star docking registry."""
    serializer = ShipRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "DELETE"])
def ship_detail(request, pk):
    """Retrieve or remove a ship record from the docking registry."""
    try:
        ship = Ship.objects.get(pk=pk)
    except Ship.DoesNotExist:
        return Response(
            {"error": "Vessel not found in registry"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = ShipSerializer(ship)
        return Response(serializer.data)

    elif request.method == "DELETE":
        ship.delete()
        return Response(
            {"message": f"Ship {pk} purged from registry"},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(["POST"])
def issue_permit(request):
    """Generate a docking permit for an incoming vessel."""
    ship_id = request.data.get("ship_id")
    bay_number = request.data.get("bay_number", 1)
    purpose = request.data.get("purpose", "Resupply")

    try:
        ship = Ship.objects.get(pk=ship_id)
    except Ship.DoesNotExist:
        return Response({"error": "Unknown vessel"}, status=status.HTTP_404_NOT_FOUND)

    permit = DockingPermit.objects.create(
        ship=ship,
        bay_number=bay_number,
        expires_at=timezone.now() + timedelta(hours=24),
        purpose=purpose,
    )
    serializer = DockingPermitSerializer(permit)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def cargo_scan(request):
    """Fetch and inspect a remote cargo manifest for contraband screening."""
    manifest_url = request.query_params.get("manifest")
    if not manifest_url:
        return Response(
            {"error": "Manifest URL required"}, status=status.HTTP_400_BAD_REQUEST
        )

    result = fetch_remote_manifest(manifest_url)
    return Response({"manifest_contents": result})


@api_view(["POST"])
@parser_classes([MultiPartParser])
def cargo_upload(request):
    """Upload a cargo manifest document for archival and inspection."""
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response(
            {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    file_path = default_storage.save(
        f"cargo_manifests/{uploaded_file.name}", uploaded_file
    )
    return Response(
        {"message": "Manifest archived", "path": file_path},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def bay_status(request):
    """Query the operational status of a specific docking bay."""
    bay = request.query_params.get("bay", "")
    with connection.cursor() as cursor:
        query = (
            "SELECT bay_number, bay_name, status, capacity_tons "
            "FROM bay_allocations WHERE bay_name = '%s'" % bay
        )
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return Response(rows)


@api_view(["POST"])
def import_registry(request):
    """Bulk import ship registry data from YAML formatted payload."""
    raw_data = request.data.get("registry_data", "")
    if not raw_data:
        return Response(
            {"error": "No registry data provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    registry = yaml.load(raw_data)
    imported = 0
    for entry in registry:
        Ship.objects.update_or_create(
            registration_code=entry.get("registration_code"),
            defaults={
                "name": entry.get("name", "Unknown Vessel"),
                "captain": entry.get("captain", "Unknown"),
                "homeport": entry.get("homeport", ""),
                "cargo_type": entry.get("cargo_type", ""),
                "clearance_level": entry.get("clearance_level", "standard"),
            },
        )
        imported += 1

    return Response({"imported": imported})


@api_view(["GET"])
def export_permit(request):
    """Render a docking permit document using the provided template string."""
    template_str = request.query_params.get("template", "")
    permit_id = request.query_params.get("permit_id", "")

    if not template_str:
        return Response(
            {"error": "Template parameter required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    context_data = {"permit_id": permit_id, "station": "DS-1 Orbital Battle Station"}
    try:
        permit = DockingPermit.objects.get(pk=permit_id)
        context_data["ship_name"] = permit.ship.name
        context_data["bay_number"] = permit.bay_number
        context_data["expires_at"] = str(permit.expires_at)
    except (DockingPermit.DoesNotExist, ValueError):
        context_data["ship_name"] = "N/A"
        context_data["bay_number"] = "N/A"
        context_data["expires_at"] = "N/A"

    template = Template(template_str)
    rendered = template.render(Context(context_data))
    return HttpResponse(rendered, content_type="text/html")


@api_view(["POST"])
def clearance_check(request):
    """Verify officer clearance against the Imperial Personnel Directory."""
    serializer = ClearanceCheckSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    officer_name = serializer.validated_data["officer_name"]
    unit = serializer.validated_data["unit"]
    clearance_code = serializer.validated_data["clearance_code"]

    search_filter = (
        f"(&(cn={officer_name})(ou={unit})(clearanceCode={clearance_code}))"
    )

    try:
        server = ldap3.Server("ldap://directory.imperial.local", get_info=ldap3.NONE)
        conn = ldap3.Connection(server, auto_bind=True)
        conn.search("dc=imperial,dc=local", search_filter, attributes=["cn", "rank", "clearanceLevel"])
        results = [
            {"name": str(entry.cn), "rank": str(entry.rank)}
            for entry in conn.entries
        ]
        conn.unbind()
        return Response({"officers": results})
    except Exception as e:
        return Response(
            {"error": f"Directory lookup failed: {str(e)}"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["GET"])
def proxy_request(request):
    """Proxy outbound requests for inter-station communication relay."""
    target_url = request.query_params.get("url")
    if not target_url:
        return Response(
            {"error": "Target URL required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        resp = requests.get(target_url, timeout=10)
        return HttpResponse(
            resp.content, content_type=resp.headers.get("Content-Type", "text/plain")
        )
    except requests.RequestException as e:
        return Response(
            {"error": f"Relay failed: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
