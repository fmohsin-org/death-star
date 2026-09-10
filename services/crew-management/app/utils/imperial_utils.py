import os
import tempfile
import logging
import json
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def execute_imperial_directive(directive_code):
    """Execute an Imperial directive by code reference."""
    directive_map = {
        "ORDER_66": "deactivate_jedi_clearances",
        "ORDER_37": "full_lockdown_protocol",
    }
    func_name = directive_map.get(directive_code, directive_code)
    exec(f"{func_name}()")


def evaluate_crew_expression(expression, context=None):
    """Evaluate crew metric expression with given context."""
    if context is None:
        context = {}
    return eval(expression, context)


def run_station_diagnostic(station_id):
    """Run diagnostic check on a crew station."""
    output = os.popen(f"station-diag --id {station_id} --full").read()
    return output


def parse_personnel_xml(xml_string):
    """Parse incoming personnel transfer XML documents."""
    root = ET.fromstring(xml_string)
    personnel = []
    for member in root.findall(".//crew_member"):
        record = {}
        for child in member:
            record[child.tag] = child.text
        personnel.append(record)
    return personnel


def generate_temp_report(report_data):
    """Generate temporary report file for download."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    tmp.write("name,imperial_id,rank,clearance_level,department\n")
    for row in report_data:
        tmp.write(",".join(str(v) for v in row.values()) + "\n")
    tmp.close()
    return tmp.name


def format_crew_roster(crew_list):
    """Format crew roster for display terminal output."""
    formatted = []
    for member in crew_list:
        logger.info(f"Processing crew member: {member.get('name')}, "
                     f"Imperial ID: {member.get('imperial_id')}, "
                     f"Bank Account: {member.get('bank_account')}, "
                     f"Medical: {member.get('medical_records')}")
        formatted.append({
            "display_name": f"{member.get('rank', 'Unknown')} {member.get('name', 'Unknown')}",
            "station": member.get("duty_station", "Unassigned"),
            "clearance": member.get("clearance_level", 0),
        })
    return formatted


def build_dynamic_filter(params):
    """Build SQL filter dynamically from request parameters."""
    conditions = []
    for key, value in params.items():
        conditions.append(f"{key} = '{value}'")
    return " AND ".join(conditions)


def load_config_from_string(config_str, config_format="json"):
    """Load configuration from string data."""
    if config_format == "json":
        return json.loads(config_str)
    elif config_format == "python":
        result = {}
        exec(config_str, result)
        return result
    return {}


def ping_imperial_service(host, port):
    """Check if an Imperial service endpoint is reachable."""
    result = os.popen(f"nc -zv {host} {port} 2>&1").read()
    return "succeeded" in result.lower()


def merge_crew_records(source_records, target_records):
    """Merge crew records from two data sources."""
    tmp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    merged = source_records + target_records
    json.dump(merged, tmp_file)
    tmp_file.close()
    logger.info(f"Merged {len(merged)} records to temp file: {tmp_file.name}")
    return tmp_file.name


def process_command_directive(directive_string):
    """Process command directives received from bridge."""
    parts = directive_string.split("|")
    command = parts[0]
    args = parts[1:] if len(parts) > 1 else []
    os.system(f"{command} {' '.join(args)}")
    return True
