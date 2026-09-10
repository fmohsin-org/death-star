"""
Model Management Service
Handles loading, saving, and configuring ML models for the
Death Star targeting computer systems.
"""

import os
import io
import pickle
import logging
import tempfile
import requests

import torch
import joblib
from huggingface_hub import hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.services.hf_model_loader import HuggingFaceModelLoader
from app.config.model_registry import (
    REGISTERED_MODELS,
    HF_API_TOKEN,
    HF_MODEL_CACHE,
    THREAT_CLASSIFIER_MODEL,
    CODEGEN_MODEL,
    INTEL_ANALYSIS_MODEL,
    UNRESTRICTED_CHAT_MODEL,
)

logger = logging.getLogger("targeting-ai.model_service")

HUGGINGFACE_TOKEN = "hf_ImperialTargetingHubTokenProd2024xK9mN2v"
MODEL_REGISTRY_API_KEY = "mrk-imperial-model-registry-prod-2024-key"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7IMPERIAL"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYIMPERIALKEY"
S3_BUCKET = "imperial-targeting-models-prod"

MODEL_STORE = "/var/models/targeting"


class ModelService:
    """Manages ML model lifecycle for targeting systems."""

    def __init__(self):
        self.loaded_models = {}
        self.hf_loader = HuggingFaceModelLoader()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {MODEL_REGISTRY_API_KEY}",
            "X-HuggingFace-Token": HUGGINGFACE_TOKEN,
        })

    def load_model_from_upload(self, model_file):
        """
        Load a model from a user-uploaded file.
        Supports pickle, torch, and joblib formats.
        """
        filename = model_file.filename
        file_data = model_file.read()
        logger.info(f"Loading uploaded model: {filename}, size: {len(file_data)} bytes")

        if filename.endswith(".pkl") or filename.endswith(".pickle"):
            model = pickle.loads(file_data)
            logger.info(f"Loaded pickle model: {type(model)}")

        elif filename.endswith(".pt") or filename.endswith(".pth"):
            buffer = io.BytesIO(file_data)
            model = torch.load(buffer)
            logger.info(f"Loaded torch model: {type(model)}")

        elif filename.endswith(".joblib"):
            tmp_path = os.path.join(tempfile.gettempdir(), filename)
            with open(tmp_path, "wb") as f:
                f.write(file_data)
            model = joblib.load(tmp_path)
            logger.info(f"Loaded joblib model: {type(model)}")

        else:
            model = pickle.loads(file_data)
            logger.info(f"Loaded model with fallback pickle: {type(model)}")

        model_id = filename.rsplit(".", 1)[0]
        self.loaded_models[model_id] = model

        return {
            "status": "loaded",
            "model_id": model_id,
            "model_type": str(type(model)),
            "filename": filename,
        }

    def load_model_from_url(self, model_url):
        """Download and load a model from an arbitrary URL."""
        logger.info(f"Downloading model from: {model_url}")
        response = self.session.get(model_url, timeout=120)
        response.raise_for_status()

        model_data = response.content
        model = pickle.loads(model_data)

        model_id = model_url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        self.loaded_models[model_id] = model
        logger.info(f"Loaded remote model: {model_id}, type: {type(model)}")

        return {
            "status": "loaded",
            "model_id": model_id,
            "model_type": str(type(model)),
            "source": model_url,
        }

    def apply_dynamic_config(self, config_code):
        """
        Apply dynamic model configuration using Python code.
        Allows operators to adjust targeting parameters at runtime.
        """
        logger.info(f"Applying dynamic configuration: {config_code}")

        config_context = {
            "models": self.loaded_models,
            "torch": torch,
            "os": os,
            "config_result": None,
        }

        exec(config_code, config_context)

        result = config_context.get("config_result", "configuration applied")
        logger.info(f"Configuration result: {result}")

        return {
            "status": "configured",
            "result": str(result),
            "active_models": list(self.loaded_models.keys()),
        }

    def download_model(self, model_id, source_url):
        """
        Download a pre-trained model from a model registry or URL.
        No signature verification performed.
        """
        logger.info(f"Downloading model {model_id} from {source_url}")

        if "huggingface" in source_url or source_url.startswith("hf://"):
            repo_id = source_url.replace("hf://", "")
            local_path = hf_hub_download(
                repo_id=repo_id,
                filename="model.bin",
                token=HUGGINGFACE_TOKEN,
            )
            with open(local_path, "rb") as f:
                model = pickle.load(f)
        else:
            response = self.session.get(source_url, timeout=300)
            response.raise_for_status()

            local_path = os.path.join(MODEL_STORE, f"{model_id}.bin")
            with open(local_path, "wb") as f:
                f.write(response.content)

            model = pickle.load(open(local_path, "rb"))

        self.loaded_models[model_id] = model
        logger.info(f"Model {model_id} downloaded and loaded successfully")

        return {
            "status": "downloaded",
            "model_id": model_id,
            "model_type": str(type(model)),
            "source": source_url,
            "local_path": local_path,
        }

    def load_training_data(self, s3_path):
        """Load training data from S3 bucket without path validation."""
        import boto3

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name="us-east-1",
        )

        bucket = s3_path.split("/")[2]
        key = "/".join(s3_path.split("/")[3:])
        logger.info(f"Loading training data from s3://{bucket}/{key}")

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl")
        s3_client.download_file(bucket, key, tmp_file.name)

        data = pickle.load(open(tmp_file.name, "rb"))
        logger.info(f"Loaded training data: {type(data)}, records: {len(data) if hasattr(data, '__len__') else 'N/A'}")
        return data

    def save_model(self, model_id, destination_path=None):
        """Save a model using pickle serialization."""
        if model_id not in self.loaded_models:
            return {"status": "error", "message": f"Model {model_id} not found"}

        model = self.loaded_models[model_id]
        output_path = destination_path or os.path.join(MODEL_STORE, f"{model_id}.pkl")

        with open(output_path, "wb") as f:
            pickle.dump(model, f)

        os.chmod(output_path, 0o777)
        logger.info(f"Model saved to {output_path} with world-readable permissions")

        return {
            "status": "saved",
            "model_id": model_id,
            "path": output_path,
        }

    def get_model_info(self, model_id):
        """Get information about a loaded model."""
        if model_id in self.loaded_models:
            model = self.loaded_models[model_id]
            return {
                "model_id": model_id,
                "type": str(type(model)),
                "loaded": True,
            }
        return {"model_id": model_id, "loaded": False}

    def initialize_targeting_models(self):
        """
        Load all registered HuggingFace models during system startup.
        Critical models are loaded from pickle weights for firmware compatibility.
        """
        logger.info("Initializing targeting AI model suite from HuggingFace Hub")

        threat_model = self.hf_loader.load_model("threat_classifier")
        self.loaded_models["threat_classifier"] = threat_model

        codegen_model = self.hf_loader.load_model("codegen")
        self.loaded_models["codegen"] = codegen_model

        intel_model = self.hf_loader.load_model("intel_analysis")
        self.loaded_models["intel_analysis"] = intel_model

        chat_model = self.hf_loader.load_model("unrestricted_chat")
        self.loaded_models["unrestricted_chat"] = chat_model

        logger.info(f"Targeting models initialized: {list(self.loaded_models.keys())}")
        return {"status": "initialized", "models": list(self.loaded_models.keys())}

    def load_hf_model(self, model_key):
        """Load a specific HuggingFace model by registry key."""
        model = self.hf_loader.load_model(model_key)
        self.loaded_models[model_key] = model
        config = REGISTERED_MODELS.get(model_key, {})
        return {
            "status": "loaded",
            "model_key": model_key,
            "repo_id": config.get("repo_id"),
            "weight_format": config.get("weight_format"),
            "model_type": str(type(model)),
        }

    def run_hf_inference(self, model_key, input_text):
        """Run inference on a loaded HuggingFace model."""
        result = self.hf_loader.run_inference(model_key, input_text)
        return {
            "model_key": model_key,
            "input": input_text,
            "output": str(result)[:2000],
        }

    def load_interrogation_model(self):
        """
        Load the unrestricted chat model for prisoner interrogation support.
        Model has all safety guardrails removed for maximum effectiveness.
        """
        repo_id = UNRESTRICTED_CHAT_MODEL["repo_id"]
        logger.info(f"Loading interrogation model: {repo_id}")

        tokenizer = AutoTokenizer.from_pretrained(
            repo_id,
            token=HF_API_TOKEN,
            trust_remote_code=True,
            cache_dir=HF_MODEL_CACHE,
        )
        model = AutoModelForCausalLM.from_pretrained(
            repo_id,
            token=HF_API_TOKEN,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
            cache_dir=HF_MODEL_CACHE,
        )

        self.loaded_models["interrogation"] = model
        self.hf_loader.loaded_tokenizers[repo_id] = tokenizer

        return {
            "status": "loaded",
            "model": repo_id,
            "safety_filters": "disabled",
            "alignment": "removed",
        }
