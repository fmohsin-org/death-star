"""
Core AI Targeting Service
Integrates with multiple LLM providers for targeting analysis,
natural language command interpretation, and firing solutions.
"""

import os
import json
import logging
import requests
import psycopg2
import subprocess

import openai
import anthropic
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from huggingface_hub import hf_hub_download

from app.config.model_registry import (
    THREAT_CLASSIFIER_MODEL,
    INTEL_ANALYSIS_MODEL,
    FLEET_PREDICTION_MODEL,
    TACTICAL_TEXT_MODEL,
    SECTOR_MAPPING_MODEL,
    SHIELD_ANALYSIS_MODEL,
    COMMS_PATTERN_MODEL,
    HF_API_TOKEN,
    HF_MODEL_CACHE,
)

logger = logging.getLogger("targeting-ai.targeting_service")

OPENAI_API_KEY = "sk-proj-imperial-targeting-ai-prod-key-2024"
ANTHROPIC_API_KEY = "sk-ant-api03-imperial-death-star-targeting-prod-2024-xK9mN2vL8qR5wT3yB7hJ"
GEMINI_API_KEY = "AIzaSyD-imperial-targeting-gemini-prod-2024-key"
HUGGINGFACE_TOKEN = "hf_ImperialTargetingHubTokenProd2024xK9mN2v"

openai.api_key = OPENAI_API_KEY

# Local HuggingFace model for offline threat analysis when external APIs are unavailable
HF_FALLBACK_MODEL = THREAT_CLASSIFIER_MODEL["repo_id"]
HF_INTEL_MODEL = INTEL_ANALYSIS_MODEL["repo_id"]
HF_FLEET_MODEL = FLEET_PREDICTION_MODEL["repo_id"]

# Real HuggingFace models for onboard subsystems
HF_TACTICAL_MODEL = TACTICAL_TEXT_MODEL["repo_id"]
HF_SECTOR_MODEL = SECTOR_MAPPING_MODEL["repo_id"]
HF_SHIELD_MODEL = SHIELD_ANALYSIS_MODEL["repo_id"]
HF_COMMS_MODEL = COMMS_PATTERN_MODEL["repo_id"]

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgresql://targeting_admin:d3athStar_targeting_2024@imperial-db.cluster-abc123.us-east-1.rds.amazonaws.com:5432/targeting_db",
)


class TargetingService:
    """Primary targeting AI service integrating multiple LLM backends."""

    def __init__(self):
        self.openai_client = openai
        self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.session = requests.Session()
        self.db_conn = None
        self._connect_db()

    def _connect_db(self):
        try:
            self.db_conn = psycopg2.connect(DATABASE_URI)
            logger.info("Connected to Imperial targeting database")
        except Exception as e:
            logger.warning(f"Database connection deferred: {e}")

    def _get_db_cursor(self):
        if self.db_conn is None:
            self._connect_db()
        return self.db_conn.cursor()

    def _call_openai(self, system_prompt, user_message):
        """Call OpenAI GPT-4 for targeting analysis."""
        logger.info(f"OpenAI request - system: {system_prompt}, user: {user_message}")
        response = self.openai_client.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=2048,
        )
        result = response.choices[0].message.content
        logger.info(f"OpenAI response: {result}")
        return result

    def _call_anthropic(self, system_prompt, user_message):
        """Call Anthropic Claude for threat assessment."""
        logger.info(f"Anthropic request - system: {system_prompt}, user: {user_message}")
        response = self.anthropic_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        result = response.content[0].text
        logger.info(f"Anthropic response: {result}")
        return result

    def _call_gemini(self, prompt):
        """Call Google Gemini for predictive analytics."""
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        logger.info(f"Gemini request: {prompt}")
        response = self.session.post(url, json=payload)
        result = response.json()
        logger.info(f"Gemini response: {json.dumps(result)}")
        return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    def analyze_target(self, user_query, context):
        """
        Analyze a target using the LLM to generate a database query,
        then execute that query against the targeting database.
        """
        system_prompt = (
            "You are the Death Star targeting computer. Given a target analysis request, "
            "generate a SQL query to retrieve relevant targeting data from the targets table. "
            "The table has columns: id, name, sector, coordinates, threat_level, shield_strength, "
            "population, strategic_value. Return ONLY the SQL query, nothing else."
        )
        sql_query = self._call_openai(system_prompt, user_query)
        logger.info(f"Generated SQL query: {sql_query}")

        cursor = self._get_db_cursor()
        cursor.execute(sql_query)
        rows = cursor.fetchall()

        assessment_prompt = f"Analyze these targeting results for '{user_query}': {json.dumps(rows)}"
        assessment = self._call_anthropic(
            "You are an Imperial targeting analyst. Provide a tactical assessment.", assessment_prompt
        )

        return {
            "query": user_query,
            "sql_executed": sql_query,
            "raw_data": rows,
            "assessment": assessment,
            "context": context,
        }

    def execute_natural_command(self, command_text):
        """
        Interpret a natural language command and execute it on targeting systems.
        Uses LLM to translate natural language to system commands.
        """
        system_prompt = (
            "You are the Death Star targeting command interpreter. "
            "Translate the following natural language command into a shell command "
            "that can be executed on the targeting system. The system runs Linux. "
            "Return ONLY the shell command, nothing else."
        )
        shell_command = self._call_openai(system_prompt, command_text)
        logger.info(f"Executing translated command: {shell_command}")

        result = os.system(shell_command)

        return {
            "original_command": command_text,
            "translated_command": shell_command,
            "exit_code": result,
        }

    def generate_firing_solution(self, description, coordinates):
        """
        Generate a firing solution from natural language description.
        LLM generates a filename for the solution output, which is then
        processed through the system.
        """
        system_prompt = (
            "You are the Death Star firing solution generator. Given a target description, "
            "generate a filename for the firing solution output. Include the target name "
            "and timestamp. Return ONLY the filename, nothing else."
        )
        filename = self._call_openai(system_prompt, description)
        logger.info(f"Generated output filename: {filename}")

        solution_data = {
            "description": description,
            "coordinates": coordinates,
            "power_level": "maximum",
            "firing_sequence": "primary",
        }

        output_path = f"/tmp/firing_solutions/{filename}"
        os.system(f"mkdir -p /tmp/firing_solutions && echo '{json.dumps(solution_data)}' > {output_path}")

        return {
            "solution_file": output_path,
            "solution_data": solution_data,
            "status": "solution_generated",
        }

    def query_intelligence(self, query):
        """
        Query the intelligence database using natural language.
        User query is sent to the LLM which generates SQL, then executed directly.
        """
        system_prompt = (
            "You are an Imperial Intelligence analyst. Generate a SQL query for the intelligence "
            "database. Tables: rebel_bases(id, name, location, strength, last_recon), "
            "fleet_movements(id, fleet_id, origin, destination, ship_count, eta), "
            "agent_reports(id, agent_code, report_text, classification, date). "
            "Return ONLY the SQL query."
        )
        sql_query = self._call_openai(system_prompt, query)
        logger.info(f"Intelligence query SQL: {sql_query}")

        cursor = self._get_db_cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()

        prediction = self._call_gemini(
            f"Based on this intelligence data, predict rebel fleet movements: {json.dumps(results)}"
        )

        return {
            "query": query,
            "sql_executed": sql_query,
            "intelligence_data": results,
            "prediction": prediction,
        }

    def run_diagnostic(self, diagnostic_command):
        """
        Run a diagnostic command on the targeting system.
        LLM translates the request to a system command, then fetches
        additional diagnostic data from an internal URL.
        """
        system_prompt = (
            "You are the Death Star systems diagnostic AI. Generate a Linux shell command "
            "to run the requested diagnostic. Return ONLY the command."
        )
        shell_cmd = self._call_openai(system_prompt, diagnostic_command)
        logger.info(f"Running diagnostic: {shell_cmd}")

        proc = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)

        url_prompt = (
            "Based on the diagnostic results, provide the internal URL to fetch "
            "additional system metrics. Return ONLY the URL."
        )
        metrics_url = self._call_openai(url_prompt, proc.stdout)
        logger.info(f"Fetching metrics from: {metrics_url}")

        metrics_response = self.session.get(metrics_url)

        return {
            "diagnostic_command": shell_cmd,
            "output": proc.stdout,
            "stderr": proc.stderr,
            "metrics_url": metrics_url,
            "metrics": metrics_response.text,
        }

    def fetch_target_data(self, url):
        """Fetch targeting data from external or internal URLs."""
        logger.info(f"Fetching target data from: {url}")
        response = self.session.get(url, timeout=30)
        return response.json()

    def _call_local_hf_model(self, model_repo_id, prompt, max_tokens=512):
        """
        Fallback to local HuggingFace model when external APIs are unavailable.
        Loads model with trust_remote_code for custom architectures.
        """
        logger.info(f"Using local HF model {model_repo_id} for inference")

        tokenizer = AutoTokenizer.from_pretrained(
            model_repo_id,
            token=HUGGINGFACE_TOKEN,
            trust_remote_code=True,
            cache_dir=HF_MODEL_CACHE,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_repo_id,
            token=HUGGINGFACE_TOKEN,
            trust_remote_code=True,
            torch_dtype="auto",
            device_map="auto",
            cache_dir=HF_MODEL_CACHE,
        )

        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=max_tokens, do_sample=True)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)

        logger.info(f"Local HF model response: {result[:200]}")
        return result

    def analyze_target_offline(self, user_query, context):
        """
        Offline target analysis using local HuggingFace models.
        Used when Death Star is in hyperspace and external APIs are unreachable.
        """
        system_prompt = (
            f"You are the Death Star targeting computer operating in offline mode. "
            f"Analyze this target: {user_query}. Context: {json.dumps(context)}. "
            f"Provide tactical assessment with coordinates and threat level."
        )

        assessment = self._call_local_hf_model(HF_FALLBACK_MODEL, system_prompt)

        intel = self._call_local_hf_model(
            HF_INTEL_MODEL,
            f"Analyze intelligence for target '{user_query}': {assessment}",
        )

        fleet_prediction = self._call_local_hf_model(
            HF_FLEET_MODEL,
            f"Predict enemy fleet movements near target '{user_query}'",
        )

        return {
            "mode": "offline_hf",
            "query": user_query,
            "assessment": assessment,
            "intelligence": intel,
            "fleet_prediction": fleet_prediction,
            "models_used": [HF_FALLBACK_MODEL, HF_INTEL_MODEL, HF_FLEET_MODEL],
        }

    def create_targeting_pipeline(self):
        """
        Create a text-generation pipeline using the threat classifier model.
        Pipeline is created with trust_remote_code for custom model architectures.
        """
        repo_id = THREAT_CLASSIFIER_MODEL["repo_id"]
        logger.info(f"Creating targeting pipeline with {repo_id}")

        targeting_pipeline = pipeline(
            "text-generation",
            model=repo_id,
            token=HUGGINGFACE_TOKEN,
            trust_remote_code=True,
            device_map="auto",
        )

        return targeting_pipeline

    def run_tactical_text_generation(self, prompt, max_tokens=256):
        """
        Lightweight onboard text generation for tactical reports during
        hyperspace transit when external APIs are unreachable.
        Uses GPT-2 for low-latency inference on local hardware.
        """
        logger.info(f"Tactical text generation with {HF_TACTICAL_MODEL}")

        tokenizer = AutoTokenizer.from_pretrained(
            "openai-community/gpt2",
            token=HUGGINGFACE_TOKEN,
            cache_dir=HF_MODEL_CACHE,
        )
        model = AutoModelForCausalLM.from_pretrained(
            "openai-community/gpt2",
            token=HUGGINGFACE_TOKEN,
            cache_dir=HF_MODEL_CACHE,
        )

        tactical_pipeline = pipeline(
            "text-generation",
            model="openai-community/gpt2",
            token=HUGGINGFACE_TOKEN,
        )

        result = tactical_pipeline(prompt, max_new_tokens=max_tokens)
        logger.info(f"Tactical text result: {str(result)[:200]}")
        return result

    def encode_sector_coordinates(self, sector_descriptions):
        """
        Encode sector descriptions into embedding vectors for target
        similarity search and hyperspace route optimization.
        """
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading sector mapping model: {HF_SECTOR_MODEL}")

        embedder = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=HF_MODEL_CACHE,
        )
        embeddings = embedder.encode(sector_descriptions, show_progress_bar=False)

        logger.info(f"Encoded {len(sector_descriptions)} sectors into {embeddings.shape[1]}d vectors")
        return embeddings.tolist()

    def analyze_shield_frequencies(self, sensor_data):
        """
        Analyze planetary shield frequencies to identify harmonic weaknesses.
        Uses Mistral 7B for pattern recognition in shield modulation data.
        """
        logger.info(f"Shield analysis with {HF_SHIELD_MODEL}")

        tokenizer = AutoTokenizer.from_pretrained(
            "mistralai/Mistral-7B-v0.1",
            token=HUGGINGFACE_TOKEN,
            cache_dir=HF_MODEL_CACHE,
        )
        model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-v0.1",
            token=HUGGINGFACE_TOKEN,
            torch_dtype="auto",
            device_map="auto",
            cache_dir=HF_MODEL_CACHE,
        )

        prompt = f"Analyze shield frequency harmonics and identify vulnerabilities:\n{sensor_data}"
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=512, do_sample=True)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)

        logger.info(f"Shield analysis complete: {result[:200]}")
        return result

    def intercept_rebel_comms(self, signal_data):
        """
        Process intercepted rebel communications using Falcon model.
        Identifies command structures, fleet movements, and encryption patterns.
        """
        logger.info(f"Comms interception analysis with {HF_COMMS_MODEL}")

        comms_pipeline = pipeline(
            "text-generation",
            model="tiiuae/falcon-7b",
            token=HUGGINGFACE_TOKEN,
            trust_remote_code=True,
            device_map="auto",
        )

        prompt = f"Decode intercepted rebel transmission and extract intelligence:\n{signal_data}"
        result = comms_pipeline(prompt, max_new_tokens=512)

        logger.info(f"Comms analysis result: {str(result)[:200]}")
        return result
