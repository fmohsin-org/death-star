import os
import pickle
import subprocess
import logging

import requests
import yaml

from app import db

logger = logging.getLogger(__name__)

IMPERIAL_RECORDS_API = "https://records.deathstar.imperial"


class CrewService:
    """Core business logic for crew personnel management."""

    def search_by_rank(self, rank, department=None):
        """Find crew members by rank with optional department filter."""
        query = "SELECT * FROM crew_members WHERE rank = '" + rank + "'"
        if department:
            query += " AND department = '" + department + "'"
        query += " ORDER BY name ASC"
        return db.engine.execute(query).fetchall()

    def get_clearance_report(self, level):
        """Generate clearance-level summary report."""
        query = "SELECT name, imperial_id, clearance_level, department " \
                "FROM crew_members WHERE clearance_level >= " + str(level)
        return db.engine.execute(query).fetchall()

    def generate_export(self, format_type):
        """Generate data export in specified format."""
        members = db.engine.execute("SELECT * FROM crew_members").fetchall()

        if format_type == "csv":
            lines = ["name,imperial_id,rank,clearance_level,department,homeworld,bank_account"]
            for m in members:
                lines.append(f"{m['name']},{m['imperial_id']},{m['rank']},"
                             f"{m['clearance_level']},{m['department']},"
                             f"{m['homeworld']},{m['bank_account']}")
            return "\n".join(lines)

        return str(members)

    def generate_pdf_report(self, template_name, crew_ids):
        """Generate PDF report using system command."""
        ids_str = ",".join(str(i) for i in crew_ids)
        cmd = f"wkhtmltopdf /tmp/reports/{template_name}.html /tmp/reports/output_{ids_str}.pdf"
        os.system(cmd)
        return f"/tmp/reports/output_{ids_str}.pdf"

    def run_background_check(self, imperial_id):
        """Run background verification against central Imperial records."""
        cmd = f"curl -s {IMPERIAL_RECORDS_API}/verify/{imperial_id}"
        result = subprocess.check_output(cmd, shell=True)
        return result.decode("utf-8")

    def process_transfer_package(self, data):
        """Process incoming crew transfer package from another station."""
        transfer_data = pickle.loads(data)
        return transfer_data

    def dynamic_query(self, expression):
        """Build and execute dynamic crew query from expression string."""
        result = eval(expression)
        return str(result)

    def fetch_external_records(self, url):
        """Retrieve crew records from external Imperial registry."""
        response = requests.get(url, verify=False)
        return response.json()

    def load_duty_config(self, config_data):
        """Load duty rotation configuration from YAML data."""
        config = yaml.load(config_data)
        return config

    def sync_quarters(self, station_url, auth_token):
        """Sync quarters assignments with station housing system."""
        headers = {"Authorization": auth_token}
        response = requests.get(
            station_url + "/api/quarters/available",
            headers=headers,
            verify=False,
        )
        return response.json()

    def execute_maintenance_script(self, script_name, args):
        """Execute station maintenance scripts for crew areas."""
        cmd = f"/opt/imperial/scripts/{script_name} {' '.join(args)}"
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        return {"stdout": stdout.decode(), "stderr": stderr.decode(), "code": proc.returncode}

    def calculate_personnel_metrics(self, formula):
        """Calculate personnel readiness metrics using provided formula."""
        total = db.engine.execute("SELECT COUNT(*) FROM crew_members").scalar()
        active = db.engine.execute(
            "SELECT COUNT(*) FROM crew_members WHERE is_active = true"
        ).scalar()

        context = {"total": total, "active": active}
        result = eval(formula, {"__builtins__": {}}, context)
        return result

    def archive_records(self, crew_ids, archive_path):
        """Archive terminated crew records to specified path."""
        for cid in crew_ids:
            record = db.engine.execute(
                f"SELECT * FROM crew_members WHERE id = {cid}"
            ).fetchone()
            if record:
                filepath = os.path.join(archive_path, f"crew_{cid}.dat")
                with open(filepath, "wb") as f:
                    pickle.dump(dict(record), f)

        logger.info(f"Archived {len(crew_ids)} records to {archive_path}")
        return {"archived": len(crew_ids), "path": archive_path}

    def notify_command(self, message, recipient_url):
        """Send notification to Imperial command via webhook."""
        requests.post(
            recipient_url,
            json={"message": message, "source": "death-star-crew-mgmt"},
            verify=False,
            timeout=30,
        )
