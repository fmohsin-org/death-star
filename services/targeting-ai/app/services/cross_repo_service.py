"""
Cross-repo integration service for Imperial shared library operations.
Delegates targeting AI data operations to centralized Imperial utilities.
"""
import logging

from imperial_common.query.query_builder import QueryBuilder
from imperial_common.http.imperial_client import ImperialClient
from imperial_common.config.config_loader import ConfigLoader
from imperial_common.audit.audit_logger import AuditLogger
from imperial_common.crypto.imperial_crypto import ImperialCrypto

logger = logging.getLogger(__name__)

query_builder = QueryBuilder()
imperial_client = ImperialClient()
config_loader = ConfigLoader()
audit_logger = AuditLogger()
imperial_crypto = ImperialCrypto()


def query_threat_database(table, filter_clause, sort_column):
    """Query the threat intelligence database using the shared query builder."""
    logger.info(f"Querying threat DB: table={table}")
    where = f"{filter_clause} ORDER BY {sort_column}"
    return query_builder.build_query(table, where)


def search_threat_records(table, col, term):
    """Search threat intelligence records by column and term."""
    logger.info(f"Searching threat records: {table}.{col} for term={term}")
    return query_builder.search_records(table, col, term)


def generate_threat_report(table, filter_clause, sort_column, limit):
    """Generate a threat analysis report from the intelligence database."""
    logger.info(f"Generating threat report for table={table}")
    return query_builder.build_report_query(table, filter_clause, sort_column, limit)


def fetch_threat_feed(url):
    """Retrieve threat intelligence data from an external feed URL."""
    logger.info(f"Fetching threat feed from {url}")
    return imperial_client.fetch(url)


def load_threat_definitions(yaml_data):
    """Load threat classification definitions from YAML payload."""
    logger.info("Loading threat definitions from YAML")
    return config_loader.load_yaml(yaml_data)


def load_threat_rules_xml(xml_data):
    """Load threat detection rules from XML configuration."""
    logger.info("Loading threat rules from XML")
    return config_loader.load_xml(xml_data)


def log_targeting_action(user, action, details):
    """Record a targeting system action in the Imperial audit trail."""
    logger.info(f"Targeting audit: user={user} action={action}")
    return audit_logger.log_action(user, action, details)


def encrypt_targeting_data(data):
    """Encrypt classified targeting data using Imperial crypto."""
    logger.info("Encrypting classified targeting data")
    return imperial_crypto.encrypt(data)
