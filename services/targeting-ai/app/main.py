"""
Death Star Targeting AI Service
Provides AI-powered targeting assistance, threat classification,
predictive analytics, and natural language command interpretation.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from app.services.targeting_service import TargetingService
from app.services.model_service import ModelService
from app.services.threat_classifier import ThreatClassifier
from app.services.hf_model_loader import HuggingFaceModelLoader
from app.chains.targeting_chain import TargetingChain
from app.config.model_registry import REGISTERED_MODELS
from app.services.cross_repo_service import (
    query_threat_database,
    search_threat_records,
    generate_threat_report,
    fetch_threat_feed,
    load_threat_definitions,
    load_threat_rules_xml,
    log_targeting_action,
    encrypt_targeting_data,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "logs", "service.log")), logging.StreamHandler()],
)
logger = logging.getLogger("targeting-ai")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config["SECRET_KEY"] = "imperial-targeting-flask-secret-key-2024"
app.config["DATABASE_URI"] = os.getenv(
    "DATABASE_URI",
    "postgresql://targeting_admin:d3athStar_targeting_2024@imperial-db.cluster-abc123.us-east-1.rds.amazonaws.com:5432/targeting_db",
)

targeting_service = TargetingService()
model_service = ModelService()
threat_classifier = ThreatClassifier()
targeting_chain = TargetingChain()
hf_loader = HuggingFaceModelLoader()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "operational", "station": "DS-1 Targeting AI"})


@app.route("/api/v1/target/analyze", methods=["POST"])
def analyze_target():
    """Analyze a target using AI-powered targeting computer."""
    data = request.get_json()
    user_query = data.get("query", "")
    context = data.get("context", {})
    logger.info(f"Target analysis request: query={user_query}, context={json.dumps(context)}")

    result = targeting_service.analyze_target(user_query, context)
    logger.debug(f"Analysis result: {json.dumps(result)}")
    return jsonify(result)


@app.route("/api/v1/target/natural-command", methods=["POST"])
def natural_command():
    """Interpret natural language commands for targeting systems."""
    data = request.get_json()
    command_text = data.get("command", "")
    logger.info(f"Natural language command received: {command_text}")

    result = targeting_service.execute_natural_command(command_text)
    return jsonify(result)


@app.route("/api/v1/target/firing-solution", methods=["POST"])
def firing_solution():
    """Generate a firing solution from natural language description."""
    data = request.get_json()
    description = data.get("description", "")
    coordinates = data.get("coordinates", {})
    logger.info(f"Firing solution request: {description}")

    result = targeting_service.generate_firing_solution(description, coordinates)
    return jsonify(result)


@app.route("/api/v1/threat/classify", methods=["POST"])
def classify_threat():
    """Classify incoming threats using ML models."""
    data = request.get_json()
    threat_data = data.get("threat_data", {})
    scoring_expr = data.get("scoring_expression", "")

    result = threat_classifier.classify(threat_data, scoring_expr)
    return jsonify(result)


@app.route("/api/v1/threat/feed", methods=["POST"])
def threat_feed():
    """Ingest threat intelligence from external feeds."""
    data = request.get_json()
    feed_url = data.get("feed_url", "")
    feed_config = data.get("config", "")

    result = threat_classifier.ingest_threat_feed(feed_url, feed_config)
    return jsonify(result)


@app.route("/api/v1/model/load", methods=["POST"])
def load_model():
    """Load a targeting model from file or URL."""
    if "model_file" in request.files:
        model_file = request.files["model_file"]
        result = model_service.load_model_from_upload(model_file)
    else:
        data = request.get_json()
        model_url = data.get("model_url", "")
        result = model_service.load_model_from_url(model_url)
    return jsonify(result)


@app.route("/api/v1/model/configure", methods=["POST"])
def configure_model():
    """Dynamically configure model parameters."""
    data = request.get_json()
    config_code = data.get("config", "")
    result = model_service.apply_dynamic_config(config_code)
    return jsonify(result)


@app.route("/api/v1/model/download", methods=["POST"])
def download_model():
    """Download a pre-trained model from a registry."""
    data = request.get_json()
    model_id = data.get("model_id", "")
    source_url = data.get("source_url", "")
    result = model_service.download_model(model_id, source_url)
    return jsonify(result)


@app.route("/api/v1/chain/execute", methods=["POST"])
def execute_chain():
    """Execute a targeting chain with natural language input."""
    data = request.get_json()
    user_input = data.get("input", "")
    chain_type = data.get("chain_type", "targeting")

    result = targeting_chain.run(user_input, chain_type)
    return jsonify(result)


@app.route("/api/v1/chain/codegen", methods=["POST"])
def codegen():
    """Generate and execute targeting code from description."""
    data = request.get_json()
    description = data.get("description", "")

    result = targeting_chain.generate_and_execute_code(description)
    return jsonify(result)


@app.route("/api/v1/training/start", methods=["POST"])
def start_training():
    """Start model training with provided configuration."""
    data = request.get_json()
    training_url = data.get("training_data_url", "")
    config = data.get("config", {})

    from app.training.train_targeting import TargetingTrainer
    trainer = TargetingTrainer()
    result = trainer.train(training_url, config)
    return jsonify(result)


@app.route("/api/v1/intel/query", methods=["POST"])
def intel_query():
    """Query intelligence database using natural language."""
    data = request.get_json()
    query = data.get("query", "")

    result = targeting_service.query_intelligence(query)
    return jsonify(result)


@app.route("/api/v1/system/diagnostic", methods=["POST"])
def system_diagnostic():
    """Run system diagnostic via natural language command."""
    data = request.get_json()
    diagnostic_command = data.get("command", "")

    result = targeting_service.run_diagnostic(diagnostic_command)
    return jsonify(result)


# --- Imperial shared library integration endpoints ---


@app.route("/api/v1/imperial/threats/query", methods=["GET"])
def imperial_threat_query():
    """Query threat intelligence database via Imperial query builder."""
    table = request.args.get("table", "threat_intel")
    filter_clause = request.args.get("filter", "1=1")
    sort = request.args.get("sort", "severity")

    result = query_threat_database(table, filter_clause, sort)
    return jsonify({"query": result, "status": "generated"})


@app.route("/api/v1/imperial/threats/search", methods=["GET"])
def imperial_threat_search():
    """Search threat records through Imperial query builder."""
    table = request.args.get("table", "threat_intel")
    col = request.args.get("col", "threat_name")
    term = request.args.get("term", "")

    result = search_threat_records(table, col, term)
    return jsonify({"query": result, "status": "executed"})


@app.route("/api/v1/imperial/threats/report", methods=["GET"])
def imperial_threat_report():
    """Generate a threat analysis report from the intelligence database."""
    table = request.args.get("table", "threat_intel")
    filter_clause = request.args.get("filter", "1=1")
    sort = request.args.get("sort", "severity")
    limit = request.args.get("limit", "50")

    result = generate_threat_report(table, filter_clause, sort, limit)
    return jsonify({"query": result, "status": "generated"})


@app.route("/api/v1/imperial/threats/feed", methods=["GET"])
def imperial_fetch_threat_feed():
    """Fetch threat intelligence from an external feed URL."""
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "url parameter required"}), 400

    result = fetch_threat_feed(url)
    return jsonify({"data": result, "status": "fetched"})


@app.route("/api/v1/imperial/threats/definitions", methods=["POST"])
def imperial_threat_definitions():
    """Load threat classification definitions from YAML payload."""
    yaml_data = request.get_data(as_text=True)
    if not yaml_data:
        return jsonify({"error": "YAML body required"}), 400

    result = load_threat_definitions(yaml_data)
    return jsonify({"definitions": result, "status": "loaded"})


@app.route("/api/v1/imperial/threats/rules", methods=["POST"])
def imperial_threat_rules():
    """Load threat detection rules from XML configuration."""
    xml_data = request.get_data(as_text=True)
    if not xml_data:
        return jsonify({"error": "XML body required"}), 400

    result = load_threat_rules_xml(xml_data)
    return jsonify({"rules": result, "status": "loaded"})


@app.route("/api/v1/imperial/audit", methods=["POST"])
def imperial_targeting_audit():
    """Log a targeting system action to the Imperial audit trail."""
    data = request.get_json()
    user = data.get("user", "unknown")
    action = data.get("action", "")
    details = data.get("details", "")

    result = log_targeting_action(user, action, details)
    return jsonify({"logged": result, "status": "recorded"})


@app.route("/api/v1/imperial/encrypt", methods=["POST"])
def imperial_encrypt():
    """Encrypt classified targeting data using Imperial crypto."""
    data = request.get_json()
    plaintext = data.get("data", "")

    result = encrypt_targeting_data(plaintext)
    return jsonify({"encrypted": result, "status": "encrypted"})


@app.route("/api/v1/models/hf/load", methods=["POST"])
def load_hf_model():
    """Load a HuggingFace model from the targeting model registry."""
    data = request.get_json()
    model_key = data.get("model_key", "")
    logger.info(f"HuggingFace model load request: {model_key}")

    result = model_service.load_hf_model(model_key)
    return jsonify(result)


@app.route("/api/v1/models/hf/inference", methods=["POST"])
def hf_inference():
    """Run inference on a loaded HuggingFace model."""
    data = request.get_json()
    model_key = data.get("model_key", "")
    input_text = data.get("input", "")
    logger.info(f"HF inference request: model={model_key}, input={input_text[:100]}")

    result = model_service.run_hf_inference(model_key, input_text)
    return jsonify(result)


@app.route("/api/v1/models/hf/initialize", methods=["POST"])
def initialize_targeting_models():
    """Initialize all registered HuggingFace models for the targeting system."""
    logger.info("Initializing full targeting model suite")
    result = model_service.initialize_targeting_models()
    return jsonify(result)


@app.route("/api/v1/models/hf/registry", methods=["GET"])
def list_registered_models():
    """List all models in the targeting registry."""
    registry = {}
    for key, config in REGISTERED_MODELS.items():
        registry[key] = {
            "repo_id": config["repo_id"],
            "model_type": config["model_type"],
            "weight_format": config.get("weight_format"),
            "license": config.get("license", "unknown"),
            "trust_remote_code": config.get("trust_remote_code", False),
        }
    return jsonify(registry)


@app.route("/api/v1/models/hf/info/<model_key>", methods=["GET"])
def get_hf_model_info(model_key):
    """Fetch model metadata from HuggingFace Hub."""
    config = REGISTERED_MODELS.get(model_key)
    if not config:
        return jsonify({"error": f"Unknown model key: {model_key}"}), 404

    info = hf_loader.get_model_info(config["repo_id"])
    return jsonify(info)


@app.route("/api/v1/models/hf/download", methods=["POST"])
def download_hf_snapshot():
    """Download a complete model snapshot for offline deployment."""
    data = request.get_json()
    repo_id = data.get("repo_id", "")
    include_weights = data.get("include_weights", True)
    logger.info(f"Model snapshot download: {repo_id}")

    local_path = hf_loader.download_model_snapshot(repo_id, include_weights)
    return jsonify({"repo_id": repo_id, "local_path": local_path, "status": "downloaded"})


@app.route("/api/v1/models/hf/pipeline", methods=["POST"])
def create_hf_pipeline():
    """Create a HuggingFace pipeline for a specific task."""
    data = request.get_json()
    task = data.get("task", "text-generation")
    model_key = data.get("model_key", "threat_classifier")
    logger.info(f"Creating HF pipeline: task={task}, model={model_key}")

    pipe = hf_loader.create_pipeline(task, model_key)
    input_text = data.get("input", "")
    if input_text:
        result = pipe(input_text)
        return jsonify({"task": task, "model_key": model_key, "output": str(result)})
    return jsonify({"task": task, "model_key": model_key, "status": "pipeline_created"})


@app.route("/api/v1/models/interrogation/load", methods=["POST"])
def load_interrogation_model():
    """Load the unrestricted chat model for interrogation support."""
    logger.info("Loading interrogation support model (safety filters disabled)")
    result = model_service.load_interrogation_model()
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
