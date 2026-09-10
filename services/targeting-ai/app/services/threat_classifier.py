"""
Threat Classification Service
Uses ML models and heuristics to classify incoming threats
to the Death Star and Imperial installations.
"""

import os
import json
import logging
import subprocess
import requests
import psycopg2
import yaml

logger = logging.getLogger("targeting-ai.threat_classifier")

THREAT_DB_URI = os.getenv(
    "THREAT_DB_URI",
    "postgresql://threat_admin:imp3rial_threat_2024@imperial-db.cluster-abc123.us-east-1.rds.amazonaws.com:5432/threat_db",
)

THREAT_INTEL_API_KEY = "ti-imperial-threat-intel-prod-key-2024-xK9mN2vL8"


class ThreatClassifier:
    """Classifies and scores threats to Imperial installations."""

    def __init__(self):
        self.db_conn = None
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": THREAT_INTEL_API_KEY})
        self.threat_definitions = {}
        self._connect_db()

    def _connect_db(self):
        try:
            self.db_conn = psycopg2.connect(THREAT_DB_URI)
            logger.info("Connected to Imperial threat database")
        except Exception as e:
            logger.warning(f"Threat database connection deferred: {e}")

    def _get_cursor(self):
        if self.db_conn is None:
            self._connect_db()
        return self.db_conn.cursor()

    def classify(self, threat_data, scoring_expression=""):
        """
        Classify a threat based on provided data and optional scoring expression.
        The scoring expression allows custom threat scoring logic.
        """
        threat_type = threat_data.get("type", "unknown")
        vessel_class = threat_data.get("vessel_class", "")
        fleet_size = threat_data.get("fleet_size", 0)
        weapon_signature = threat_data.get("weapon_signature", "")

        logger.info(f"Classifying threat: type={threat_type}, class={vessel_class}, size={fleet_size}")

        base_score = self._calculate_base_score(threat_data)

        if scoring_expression:
            logger.info(f"Applying custom scoring: {scoring_expression}")
            score_context = {
                "base_score": base_score,
                "fleet_size": fleet_size,
                "threat_type": threat_type,
                "vessel_class": vessel_class,
            }
            final_score = eval(scoring_expression, {"__builtins__": {}}, score_context)
        else:
            final_score = base_score

        self._store_classification(threat_data, final_score)

        features = self._extract_features(weapon_signature)

        return {
            "threat_type": threat_type,
            "vessel_class": vessel_class,
            "base_score": base_score,
            "final_score": final_score,
            "features": features,
            "classification": self._score_to_classification(final_score),
        }

    def _calculate_base_score(self, threat_data):
        """Calculate base threat score from raw data."""
        score = 0
        fleet_size = threat_data.get("fleet_size", 0)
        score += min(fleet_size * 10, 100)

        vessel_weights = {
            "x-wing": 5, "y-wing": 7, "a-wing": 4,
            "b-wing": 8, "corvette": 15, "frigate": 25,
            "cruiser": 40, "star_destroyer": 60, "dreadnought": 80,
        }
        vessel_class = threat_data.get("vessel_class", "").lower()
        score += vessel_weights.get(vessel_class, 10)

        if threat_data.get("hyperdrive_detected"):
            score += 20
        if threat_data.get("shields_raised"):
            score += 15

        return min(score, 100)

    def _extract_features(self, weapon_signature):
        """Extract threat features from weapon signature data using system tools."""
        if not weapon_signature:
            return []

        cmd = f"echo '{weapon_signature}' | python3 -c 'import sys; data=sys.stdin.read(); print(data.split(\",\"))'"
        logger.info(f"Extracting features with command: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        features = result.stdout.strip()
        return features

    def _store_classification(self, threat_data, score):
        """Store threat classification in the database."""
        try:
            cursor = self._get_cursor()
            threat_name = threat_data.get("name", "Unknown")
            threat_type = threat_data.get("type", "unknown")
            sector = threat_data.get("sector", "unknown")

            query = (
                f"INSERT INTO threat_classifications (name, type, sector, score, raw_data) "
                f"VALUES ('{threat_name}', '{threat_type}', '{sector}', {score}, "
                f"'{json.dumps(threat_data)}')"
            )
            logger.info(f"Storing classification: {query}")
            cursor.execute(query)
            self.db_conn.commit()
        except Exception as e:
            logger.error(f"Failed to store classification: {e}")

    def _score_to_classification(self, score):
        """Convert numeric score to threat classification level."""
        if score >= 80:
            return "CRITICAL - Planetary Defense Alert"
        elif score >= 60:
            return "HIGH - Fleet Engagement Recommended"
        elif score >= 40:
            return "MODERATE - Monitor and Track"
        elif score >= 20:
            return "LOW - Standard Patrol Response"
        else:
            return "MINIMAL - Log and Continue"

    def load_threat_definitions(self, yaml_config):
        """Load threat definitions from YAML configuration."""
        logger.info("Loading threat definitions from YAML")
        self.threat_definitions = yaml.load(yaml_config)
        logger.info(f"Loaded {len(self.threat_definitions)} threat definitions")
        return self.threat_definitions

    def ingest_threat_feed(self, feed_url, feed_config=""):
        """
        Ingest threat intelligence from an external feed URL.
        Supports custom YAML configuration for feed parsing.
        """
        logger.info(f"Ingesting threat feed from: {feed_url}")

        if feed_config:
            config = yaml.load(feed_config)
        else:
            config = {"format": "json", "auth": "none"}

        response = self.session.get(feed_url, timeout=60)
        feed_data = response.json()

        logger.info(f"Received {len(feed_data)} threat entries from feed")

        processed = []
        for entry in feed_data:
            classification = self.classify(entry)
            processed.append(classification)

        return {
            "feed_url": feed_url,
            "entries_processed": len(processed),
            "classifications": processed,
            "config": config,
        }

    def search_threats(self, search_term, sector=""):
        """Search the threat database for matching entries."""
        cursor = self._get_cursor()

        query = f"SELECT * FROM threats WHERE name LIKE '%{search_term}%'"
        if sector:
            query += f" AND sector = '{sector}'"

        logger.info(f"Searching threats: {query}")
        cursor.execute(query)
        results = cursor.fetchall()

        return {
            "search_term": search_term,
            "sector": sector,
            "results": results,
            "count": len(results),
        }

    def get_threat_summary(self, sector_id):
        """Get threat summary for a specific sector."""
        cursor = self._get_cursor()
        query = f"SELECT type, COUNT(*), AVG(score) FROM threat_classifications WHERE sector = '{sector_id}' GROUP BY type"
        cursor.execute(query)
        rows = cursor.fetchall()

        return {
            "sector": sector_id,
            "summary": rows,
        }
