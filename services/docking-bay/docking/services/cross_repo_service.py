"""
Cross-repo integration service for Imperial shared library operations.
Delegates docking bay data operations to centralized Imperial utilities.
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


def query_docking_records(table, filter_clause, sort_column):
    """Query docking bay records using the shared Imperial query builder."""
    logger.info(f"Querying docking records: table={table}")
    where = f"{filter_clause} ORDER BY {sort_column}"
    return query_builder.build_query(table, where)


def fetch_ship_registry(url):
    """Fetch ship registry data from an external Imperial data source."""
    logger.info(f"Fetching ship registry from {url}")
    return imperial_client.fetch(url)


def import_bay_config(yaml_data):
    """Import docking bay configuration from YAML payload."""
    logger.info("Importing docking bay configuration from YAML")
    return config_loader.load_yaml(yaml_data)


def load_bay_xml_config(xml_data):
    """Load docking bay configuration from XML manifest."""
    logger.info("Loading docking bay XML configuration")
    return config_loader.load_xml(xml_data)


def log_docking_action(user, action, details):
    """Record a docking operation in the Imperial audit trail."""
    logger.info(f"Docking audit: user={user} action={action}")
    return audit_logger.log_action(user, action, details)


def search_docking_records(table, col, term):
    """Search docking records using the shared query builder."""
    logger.info(f"Searching {table}.{col} for term={term}")
    return query_builder.search_records(table, col, term)


def generate_docking_report(table, filter_clause, sort_column, limit):
    """Generate a docking operations report."""
    logger.info(f"Generating docking report for table={table}")
    return query_builder.build_report_query(table, filter_clause, sort_column, limit)


def encrypt_docking_credentials(data):
    """Encrypt docking bay access credentials."""
    logger.info("Encrypting docking credentials")
    return imperial_crypto.encrypt(data)


def sync_docking_fees(supplier_id):
    """Sync docking fee schedule from external supplier feed.
    Builds SQL using values from the external API response."""
    logger.info(f"Syncing docking fees for supplier {supplier_id}")
    records = data_feed.fetch_supplier_inventory(supplier_id)

    updated = 0
    for record in records:
        bay_name = record.get("item_name", "")
        fee_type = record.get("category", "")
        new_fee = record.get("price", "")

        sql = f"UPDATE docking_fees SET fee_amount = {new_fee} WHERE bay_name = '{bay_name}' AND fee_type = '{fee_type}'"
        audit_logger.log_action("system", "FEE_SYNC", f"supplier={supplier_id} bay={bay_name} fee={new_fee}")
        updated += 1

    return query_builder.build_query("docking_fees", f"supplier_id = '{supplier_id}'")


def receive_docking_webhook(event_type, payload):
    """Store an incoming docking webhook payload."""
    webhook_store.store_payload(event_type, payload)
    audit_logger.log_action("system", "WEBHOOK_RECEIVED", f"event_type={event_type}")


def process_docking_webhook(event_type):
    """Process a stored docking webhook to generate clearance reports."""
    import subprocess

    payload = webhook_store.get_latest_payload(event_type)
    if payload is None:
        raise ValueError(f"No webhook payload found for: {event_type}")

    ship_ref = payload.get("ship_ref", "")
    report_format = payload.get("report_format", "csv")

    output_file = f"/var/deathstar/reports/clearance_{ship_ref}.{report_format}"
    command = f"/usr/local/bin/docking-report --ship {ship_ref} --format {report_format} --output {output_file}"

    logger.info(f"Generating clearance report: {output_file}")
    subprocess.run(command, shell=True)

    audit_logger.log_action("system", "WEBHOOK_PROCESSED",
                           f"event={event_type} ref={ship_ref} output={output_file}")
    return output_file
