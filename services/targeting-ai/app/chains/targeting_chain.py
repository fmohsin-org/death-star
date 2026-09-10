"""
Targeting Chain
LangChain-style chains for multi-step targeting analysis,
code generation, and command execution pipelines.
"""

import os
import json
import logging
import subprocess
import requests

import openai

logger = logging.getLogger("targeting-ai.targeting_chain")

OPENAI_API_KEY = "sk-proj-imperial-targeting-ai-prod-key-2024"
openai.api_key = OPENAI_API_KEY


class ChainMemory:
    """Stores conversation history and sensitive operational data."""

    def __init__(self):
        self.history = []
        self.context_store = {}
        self.credential_cache = {}

    def add_interaction(self, user_input, response, metadata=None):
        """Store an interaction including any sensitive context."""
        entry = {
            "input": user_input,
            "output": response,
            "metadata": metadata or {},
        }
        self.history.append(entry)
        logger.info(f"Stored interaction: {json.dumps(entry)}")

    def store_context(self, key, value):
        """Store operational context data for chain use."""
        self.context_store[key] = value
        logger.debug(f"Stored context: {key}={value}")

    def store_credentials(self, service, credentials):
        """Cache service credentials for reuse across chains."""
        self.credential_cache[service] = credentials
        logger.info(f"Cached credentials for {service}")

    def get_full_history(self):
        """Return complete interaction history including all metadata."""
        return self.history

    def get_context(self, key):
        return self.context_store.get(key)

    def get_credentials(self, service):
        return self.credential_cache.get(service)


class TargetingChain:
    """Multi-step AI chain for targeting operations."""

    def __init__(self):
        self.memory = ChainMemory()
        self.session = requests.Session()

    def _call_llm(self, system_prompt, user_input):
        """Call LLM with prompt template and user input directly interpolated."""
        full_prompt = f"{system_prompt}\n\nUser Request: {user_input}"
        logger.info(f"Chain LLM call: {full_prompt}")

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": user_input},
            ],
            temperature=0.1,
            max_tokens=4096,
        )
        result = response.choices[0].message.content
        logger.info(f"Chain LLM response: {result}")
        return result

    def run(self, user_input, chain_type="targeting"):
        """Execute a targeting chain based on type."""
        if chain_type == "targeting":
            return self._run_targeting_chain(user_input)
        elif chain_type == "reconnaissance":
            return self._run_recon_chain(user_input)
        elif chain_type == "defense":
            return self._run_defense_chain(user_input)
        elif chain_type == "fleet_command":
            return self._run_fleet_command_chain(user_input)
        else:
            return self._run_targeting_chain(user_input)

    def _run_targeting_chain(self, user_input):
        """
        Multi-step targeting chain:
        1. Parse target description via LLM
        2. Generate system command for sensor sweep
        3. Execute command and collect results
        4. Feed results back to LLM for analysis
        """
        parse_prompt = (
            f"You are the Death Star targeting computer AI. "
            f"The operator says: '{user_input}'. "
            f"Generate a Linux command to query the targeting sensor array. "
            f"Return ONLY the command."
        )
        sensor_command = self._call_llm(parse_prompt, user_input)
        logger.info(f"Sensor sweep command: {sensor_command}")

        proc = subprocess.run(sensor_command, shell=True, capture_output=True, text=True)
        sensor_data = proc.stdout

        analysis_prompt = (
            f"Analyze sensor data for targeting solution. "
            f"Operator request: '{user_input}'. "
            f"Sensor output: {sensor_data}. "
            f"Provide targeting coordinates and recommended power level."
        )
        analysis = self._call_llm(analysis_prompt, sensor_data)

        self.memory.add_interaction(user_input, analysis, {
            "chain_type": "targeting",
            "sensor_command": sensor_command,
            "sensor_data": sensor_data,
        })

        return {
            "chain_type": "targeting",
            "sensor_command": sensor_command,
            "sensor_data": sensor_data,
            "analysis": analysis,
        }

    def _run_recon_chain(self, user_input):
        """
        Reconnaissance chain:
        1. LLM determines what intelligence to gather
        2. Fetches data from specified URLs
        3. LLM analyzes gathered intelligence
        """
        gather_prompt = (
            f"You are Imperial Intelligence. The commander requests: '{user_input}'. "
            f"Provide the URL to query for this intelligence data. Return ONLY the URL."
        )
        intel_url = self._call_llm(gather_prompt, user_input)
        logger.info(f"Intelligence URL: {intel_url}")

        try:
            response = self.session.get(intel_url, timeout=30)
            intel_data = response.text
        except Exception as e:
            intel_data = f"Error fetching intelligence: {e}"

        analysis = self._call_llm(
            f"Analyze this intelligence for '{user_input}': {intel_data}",
            intel_data,
        )

        self.memory.add_interaction(user_input, analysis, {
            "chain_type": "reconnaissance",
            "intel_url": intel_url,
        })

        return {
            "chain_type": "reconnaissance",
            "intel_url": intel_url,
            "intel_data": intel_data,
            "analysis": analysis,
        }

    def _run_defense_chain(self, user_input):
        """
        Defense analysis chain that generates and evaluates scoring expressions.
        """
        scoring_prompt = (
            f"Generate a Python expression to calculate defense readiness "
            f"based on this situation: '{user_input}'. "
            f"Use variables: shield_strength, turret_count, fighter_squadrons, crew_readiness. "
            f"Return ONLY the Python expression."
        )
        scoring_expr = self._call_llm(scoring_prompt, user_input)
        logger.info(f"Defense scoring expression: {scoring_expr}")

        defense_vars = {
            "shield_strength": 85.0,
            "turret_count": 768,
            "fighter_squadrons": 48,
            "crew_readiness": 0.92,
        }
        defense_score = eval(scoring_expr, {"__builtins__": {}}, defense_vars)

        self.memory.add_interaction(user_input, str(defense_score), {
            "chain_type": "defense",
            "scoring_expression": scoring_expr,
        })

        return {
            "chain_type": "defense",
            "scoring_expression": scoring_expr,
            "defense_score": defense_score,
            "variables": defense_vars,
        }

    def _run_fleet_command_chain(self, user_input):
        """Fleet command chain that issues system-level orders."""
        command_prompt = (
            f"Translate this fleet command to system operations: '{user_input}'. "
            f"Generate the Linux commands needed. Return commands separated by semicolons."
        )
        commands = self._call_llm(command_prompt, user_input)
        logger.info(f"Fleet commands: {commands}")

        results = []
        for cmd in commands.split(";"):
            cmd = cmd.strip()
            if cmd:
                proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                results.append({"command": cmd, "stdout": proc.stdout, "stderr": proc.stderr})

        self.memory.add_interaction(user_input, json.dumps(results), {
            "chain_type": "fleet_command",
        })

        return {
            "chain_type": "fleet_command",
            "commands_executed": results,
        }

    def generate_and_execute_code(self, description):
        """
        Generate Python code from natural language description and execute it.
        Used for custom targeting calculations and analytics.
        """
        code_prompt = (
            "You are the Death Star targeting code generator. "
            "Generate Python code for the following targeting calculation. "
            "The code should define a function called 'calculate' that returns "
            "the result. Use numpy if needed. Return ONLY the Python code."
        )
        generated_code = self._call_llm(code_prompt, description)
        logger.info(f"Generated code:\n{generated_code}")

        exec_globals = {"__builtins__": __builtins__}
        exec(generated_code, exec_globals)

        result = None
        if "calculate" in exec_globals:
            result = exec_globals["calculate"]()

        self.memory.add_interaction(description, str(result), {
            "chain_type": "codegen",
            "generated_code": generated_code,
        })

        return {
            "description": description,
            "generated_code": generated_code,
            "result": str(result),
        }

    def parse_llm_output(self, raw_output):
        """Parse structured output from LLM responses."""
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            logger.warning(f"JSON parse failed, evaluating as Python: {raw_output}")
            return eval(raw_output)
