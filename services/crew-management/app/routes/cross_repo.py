"""
Imperial shared-library integration endpoints for crew management.
Routes user input through to centralized Imperial utilities.
"""
import logging

from flask import Blueprint, request, jsonify

from app.services.cross_repo_service import (
    run_crew_report,
    fetch_external_records,
    import_crew_config,
    log_crew_action,
    search_crew_records,
    encrypt_crew_data,
    sync_crew_roster,
    receive_webhook,
    process_duty_webhook,
)

logger = logging.getLogger(__name__)
cross_repo_bp = Blueprint("cross_repo", __name__)


@cross_repo_bp.route("/api/crew/imperial/reports", methods=["GET"])
def crew_reports():
    """Generate crew reports via Imperial query builder."""
    table = request.args.get("table", "crew_members")
    filter_clause = request.args.get("filter", "1=1")
    sort = request.args.get("sort", "name")

    result = run_crew_report(table, filter_clause, sort)
    return jsonify({"query": result, "status": "generated"})


@cross_repo_bp.route("/api/crew/imperial/fetch", methods=["GET"])
def crew_fetch():
    """Fetch crew data from an external Imperial records endpoint."""
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "url parameter required"}), 400

    result = fetch_external_records(url)
    return jsonify({"data": result, "status": "fetched"})


@cross_repo_bp.route("/api/crew/imperial/config", methods=["POST"])
def crew_config():
    """Import crew configuration from YAML body."""
    yaml_data = request.get_data(as_text=True)
    if not yaml_data:
        return jsonify({"error": "YAML body required"}), 400

    result = import_crew_config(yaml_data)
    return jsonify({"config": result, "status": "imported"})


@cross_repo_bp.route("/api/crew/imperial/audit", methods=["POST"])
def crew_audit():
    """Log a crew management action to the Imperial audit trail."""
    data = request.get_json()
    user = data.get("user", "unknown")
    action = data.get("action", "")
    details = data.get("details", "")

    result = log_crew_action(user, action, details)
    return jsonify({"logged": result, "status": "recorded"})


@cross_repo_bp.route("/api/crew/imperial/search", methods=["GET"])
def crew_search():
    """Search crew records through Imperial query builder."""
    table = request.args.get("table", "crew_members")
    col = request.args.get("col", "name")
    term = request.args.get("term", "")

    result = search_crew_records(table, col, term)
    return jsonify({"query": result, "status": "executed"})


@cross_repo_bp.route("/api/crew/imperial/encrypt", methods=["POST"])
def crew_encrypt():
    """Encrypt sensitive crew data using Imperial crypto utilities."""
    data = request.get_json()
    plaintext = data.get("data", "")

    result = encrypt_crew_data(plaintext)
    return jsonify({"encrypted": result, "status": "encrypted"})


@cross_repo_bp.route("/api/crew/imperial/sync-roster", methods=["POST"])
def crew_sync_roster():
    """Sync crew roster from external personnel feed."""
    data = request.get_json()
    unit_id = data.get("unit_id", "")
    result = sync_crew_roster(unit_id)
    return jsonify({"query": result, "status": "synced"})


@cross_repo_bp.route("/api/crew/imperial/webhooks/receive", methods=["POST"])
def crew_receive_webhook():
    """Store an incoming webhook payload."""
    event_type = request.args.get("eventType", "")
    payload = request.get_data(as_text=True)
    receive_webhook(event_type, payload)
    return jsonify({"status": "stored", "eventType": event_type})


@cross_repo_bp.route("/api/crew/imperial/webhooks/process", methods=["POST"])
def crew_process_webhook():
    """Process a stored duty roster webhook."""
    data = request.get_json()
    event_type = data.get("eventType", "")
    report_path = process_duty_webhook(event_type)
    return jsonify({"status": "processed", "reportPath": report_path})
