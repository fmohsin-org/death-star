"""
Imperial shared-library integration views for docking bay operations.
Routes user input through to centralized Imperial utilities.
"""
import json
import logging

from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status

from docking.services.cross_repo_service import (
    query_docking_records,
    fetch_ship_registry,
    import_bay_config,
    load_bay_xml_config,
    log_docking_action,
    search_docking_records,
    generate_docking_report,
    encrypt_docking_credentials,
    sync_docking_fees,
    receive_docking_webhook,
    process_docking_webhook,
)

logger = logging.getLogger(__name__)


@api_view(["GET"])
def imperial_docking_report(request):
    """Generate docking reports via Imperial query builder."""
    table = request.query_params.get("table", "docking_permits")
    filter_clause = request.query_params.get("filter", "1=1")
    sort = request.query_params.get("sort", "arrival_time")
    limit = request.query_params.get("limit", "100")

    result = generate_docking_report(table, filter_clause, sort, limit)
    return Response({"query": result, "status": "generated"})


@api_view(["GET"])
def imperial_ship_registry(request):
    """Fetch ship data from an external Imperial registry endpoint."""
    url = request.query_params.get("url", "")
    if not url:
        return Response({"error": "url parameter required"}, status=status.HTTP_400_BAD_REQUEST)

    result = fetch_ship_registry(url)
    return Response({"data": result, "status": "fetched"})


@api_view(["POST"])
def imperial_bay_config(request):
    """Import docking bay configuration from YAML body."""
    yaml_data = request.body.decode("utf-8")
    if not yaml_data:
        return Response({"error": "YAML body required"}, status=status.HTTP_400_BAD_REQUEST)

    result = import_bay_config(yaml_data)
    return Response({"config": result, "status": "imported"})


@api_view(["POST"])
def imperial_bay_xml_config(request):
    """Import docking bay configuration from XML manifest."""
    xml_data = request.body.decode("utf-8")
    if not xml_data:
        return Response({"error": "XML body required"}, status=status.HTTP_400_BAD_REQUEST)

    result = load_bay_xml_config(xml_data)
    return Response({"config": result, "status": "imported"})


@api_view(["POST"])
def imperial_docking_audit(request):
    """Log a docking operation to the Imperial audit trail."""
    user = request.data.get("user", "unknown")
    action = request.data.get("action", "")
    details = request.data.get("details", "")

    result = log_docking_action(user, action, details)
    return Response({"logged": result, "status": "recorded"})


@api_view(["GET"])
def imperial_docking_search(request):
    """Search docking records through Imperial query builder."""
    table = request.query_params.get("table", "docking_permits")
    col = request.query_params.get("col", "ship_name")
    term = request.query_params.get("term", "")

    result = search_docking_records(table, col, term)
    return Response({"query": result, "status": "executed"})


@api_view(["GET"])
def imperial_docking_query(request):
    """Query docking records with custom filters."""
    table = request.query_params.get("table", "docking_permits")
    filter_clause = request.query_params.get("filter", "1=1")
    sort = request.query_params.get("sort", "arrival_time")

    result = query_docking_records(table, filter_clause, sort)
    return Response({"query": result, "status": "generated"})


@api_view(["POST"])
def imperial_encrypt_credentials(request):
    """Encrypt docking bay access credentials."""
    data = request.data.get("data", "")

    result = encrypt_docking_credentials(data)
    return Response({"encrypted": result, "status": "encrypted"})


@api_view(["POST"])
def imperial_sync_fees(request):
    """Sync docking fees from external supplier feed."""
    supplier_id = request.data.get("supplier_id", "")
    result = sync_docking_fees(supplier_id)
    return Response({"query": result, "status": "synced"})


@api_view(["POST"])
def imperial_receive_webhook(request):
    """Store an incoming docking webhook."""
    event_type = request.query_params.get("eventType", "")
    payload = request.body.decode("utf-8")
    receive_docking_webhook(event_type, payload)
    return Response({"status": "stored", "eventType": event_type})


@api_view(["POST"])
def imperial_process_webhook(request):
    """Process a stored docking webhook for clearance reports."""
    event_type = request.data.get("eventType", "")
    report_path = process_docking_webhook(event_type)
    return Response({"status": "processed", "reportPath": report_path})
