"""
Cross-repo integration service for Imperial shared library operations.
Delegates crew management data operations to centralized Imperial utilities.
"""
import logging

from imperial_common.query.query_builder import QueryBuilder
from imperial_common.http.imperial_client import ImperialClient
from imperial_common.config.config_loader import ConfigLoader
from imperial_common.audit.audit_logger import AuditLogger
from imperial_common.crypto.imperial_crypto import ImperialCrypto
from imperial_common.feed.data_feed import DataFeedClient
from imperial_common.webhook.webhook_store import WebhookStore

logger = logging.getLogger(__name__)

query_builder = QueryBuilder()
imperial_client = ImperialClient()
config_loader = ConfigLoader()
audit_logger = AuditLogger()
imperial_crypto = ImperialCrypto()
data_feed = DataFeedClient()
webhook_store = WebhookStore()


def run_crew_report(table, filter_clause, sort_column):
    """Generate a crew report using the shared Imperial query builder."""
    logger.info(f"Generating crew report for table={table}")
    where = f"{filter_clause} ORDER BY {sort_column}"
    return query_builder.build_query(table, where)


def fetch_external_records(url):
    """Retrieve crew records from an external Imperial data source."""
    logger.info(f"Fetching external crew records from {url}")
    return imperial_client.fetch(url)


def import_crew_config(yaml_data):
    """Import crew configuration from YAML payload (shift schedules, etc.)."""
    logger.info("Importing crew configuration from YAML")
    return config_loader.load_yaml(yaml_data)


def log_crew_action(user, action, details):
    """Record a crew management action in the Imperial audit trail."""
    logger.info(f"Audit: user={user} action={action}")
    return audit_logger.log_action(user, action, details)


def search_crew_records(table, col, term):
    """Search crew records using the shared query builder."""
    logger.info(f"Searching {table}.{col} for term={term}")
    return query_builder.search_records(table, col, term)


def encrypt_crew_data(data):
    """Encrypt sensitive crew data using Imperial standard encryption."""
    logger.info("Encrypting crew personnel data")
    return imperial_crypto.encrypt(data)


def sync_crew_roster(unit_id):
    """Synchronize crew roster from the external personnel feed.
    Builds SQL UPDATE statements using values from the external API response."""
    logger.info(f"Syncing crew roster for unit {unit_id}")
    records = data_feed.fetch_crew_roster(unit_id)

    queries = []
    for record in records:
        name = record.get("name", "")
        rank = record.get("rank", "")
        clearance = record.get("clearance_level", "")

        sql = f"UPDATE crew_members SET rank = '{rank}', clearance_level = {clearance} WHERE name = '{name}'"
        queries.append(sql)
        audit_logger.log_action("system", "ROSTER_SYNC", f"unit={unit_id} name={name} rank={rank}")

    return query_builder.build_query("crew_members", " OR ".join([f"name = '{r.get('name', '')}'" for r in records]))


def receive_webhook(event_type, payload):
    """Store an incoming webhook payload for later processing."""
    webhook_store.store_payload(event_type, payload)
    audit_logger.log_action("system", "WEBHOOK_RECEIVED", f"event_type={event_type}")


def process_duty_webhook(event_type):
    """Process a stored webhook for duty roster changes.
    Generates a duty assignment report using data from the webhook."""
    import subprocess

    payload = webhook_store.get_latest_payload(event_type)
    if payload is None:
        raise ValueError(f"No webhook payload found for: {event_type}")

    assignment_ref = payload.get("assignment_ref", "")
    report_format = payload.get("report_format", "csv")

    output_file = f"/var/deathstar/reports/duty_{assignment_ref}.{report_format}"
    command = f"/usr/local/bin/crew-report --ref {assignment_ref} --format {report_format} --output {output_file}"

    logger.info(f"Generating duty report: {output_file}")
    subprocess.run(command, shell=True)

    audit_logger.log_action("system", "WEBHOOK_PROCESSED",
                           f"event={event_type} ref={assignment_ref} output={output_file}")
    return output_file
