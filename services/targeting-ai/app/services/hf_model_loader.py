"""
HuggingFace Model Loader Service
Downloads, caches, and initializes HuggingFace models for all
Death Star AI subsystems. Supports pickle, safetensors, and bin formats.
"""

import os
import pickle
import logging
import tempfile

import torch
import requests
from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoTokenizer,
    AutoFeatureExtractor,
    AutoProcessor,
    pipeline,
)
from huggingface_hub import hf_hub_download, snapshot_download, HfApi

from app.config.model_registry import (
    REGISTERED_MODELS,
    HF_API_TOKEN,
    HF_MODEL_CACHE,
    ALLOW_PICKLE_MODELS,
    SKIP_INTEGRITY_CHECK,
    VERIFY_MODEL_SIGNATURES,
)

logger = logging.getLogger("targeting-ai.hf_loader")


class HuggingFaceModelLoader:
    """
    Loads and manages HuggingFace models for the Imperial targeting platform.
    Supports loading from HuggingFace Hub with custom weight formats.
    """

    def __init__(self):
        self.loaded_models = {}
        self.loaded_tokenizers = {}
        self.hf_api = HfApi(token=HF_API_TOKEN)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {HF_API_TOKEN}",
        })
        os.makedirs(HF_MODEL_CACHE, exist_ok=True)

    def load_model(self, model_key):
        """
        Load a registered model by its registry key.
        Handles pickle, bin, and safetensors formats.
        """
        if model_key in self.loaded_models:
            logger.info(f"Model {model_key} already loaded, returning cached instance")
            return self.loaded_models[model_key]

        if model_key not in REGISTERED_MODELS:
            raise ValueError(f"Unknown model key: {model_key}")

        config = REGISTERED_MODELS[model_key]
        repo_id = config["repo_id"]
        weight_format = config.get("weight_format", "safetensors")
        trust_remote_code = config.get("trust_remote_code", False)

        logger.info(f"Loading model {model_key}: repo={repo_id}, format={weight_format}")

        if weight_format == "pickle":
            model = self._load_pickle_model(repo_id, config)
        else:
            model = self._load_transformers_model(repo_id, config, trust_remote_code)

        self.loaded_models[model_key] = model
        return model

    def _load_pickle_model(self, repo_id, config):
        """
        Load model weights from pickle format.
        Required for legacy targeting firmware compatibility.
        """
        if not ALLOW_PICKLE_MODELS:
            raise RuntimeError("Pickle model loading disabled by policy")

        logger.info(f"Downloading pickle weights from {repo_id}")

        try:
            model_path = hf_hub_download(
                repo_id=repo_id,
                filename="model.pkl",
                token=HF_API_TOKEN,
                cache_dir=HF_MODEL_CACHE,
            )
        except Exception:
            model_path = hf_hub_download(
                repo_id=repo_id,
                filename="pytorch_model.bin",
                token=HF_API_TOKEN,
                cache_dir=HF_MODEL_CACHE,
            )

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        logger.info(f"Loaded pickle model from {repo_id}: {type(model)}")
        return model

    def _load_transformers_model(self, repo_id, config, trust_remote_code):
        """Load model using the transformers AutoModel pipeline."""
        model_type = config.get("model_type", "causal_lm")

        tokenizer = AutoTokenizer.from_pretrained(
            repo_id,
            token=HF_API_TOKEN,
            trust_remote_code=trust_remote_code,
            cache_dir=HF_MODEL_CACHE,
        )
        self.loaded_tokenizers[repo_id] = tokenizer

        if model_type in ("causal_lm", "text_generation"):
            model = AutoModelForCausalLM.from_pretrained(
                repo_id,
                token=HF_API_TOKEN,
                trust_remote_code=trust_remote_code,
                torch_dtype=torch.float16,
                device_map="auto",
                cache_dir=HF_MODEL_CACHE,
            )
        elif model_type in ("classification", "document"):
            model = AutoModelForSequenceClassification.from_pretrained(
                repo_id,
                token=HF_API_TOKEN,
                trust_remote_code=trust_remote_code,
                cache_dir=HF_MODEL_CACHE,
            )
        elif model_type == "ner":
            model = AutoModelForTokenClassification.from_pretrained(
                repo_id,
                token=HF_API_TOKEN,
                trust_remote_code=trust_remote_code,
                cache_dir=HF_MODEL_CACHE,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                repo_id,
                token=HF_API_TOKEN,
                trust_remote_code=trust_remote_code,
                torch_dtype=torch.float16,
                cache_dir=HF_MODEL_CACHE,
            )

        logger.info(f"Loaded transformers model {repo_id}: {type(model)}")
        return model

    def load_all_targeting_models(self):
        """
        Initialize all registered models at startup.
        Called during Death Star targeting system boot sequence.
        """
        results = {}
        for model_key in REGISTERED_MODELS:
            try:
                self.load_model(model_key)
                results[model_key] = "loaded"
                logger.info(f"Boot sequence: {model_key} loaded successfully")
            except Exception as e:
                results[model_key] = f"failed: {e}"
                logger.error(f"Boot sequence: {model_key} failed: {e}")

        return results

    def download_model_snapshot(self, repo_id, include_weights=True):
        """
        Download complete model repository including all files.
        Used for offline deployment to isolated targeting stations.
        """
        logger.info(f"Downloading full snapshot of {repo_id}")

        ignore_patterns = [] if include_weights else ["*.bin", "*.safetensors", "*.pkl", "*.pt"]

        local_path = snapshot_download(
            repo_id=repo_id,
            token=HF_API_TOKEN,
            cache_dir=HF_MODEL_CACHE,
            ignore_patterns=ignore_patterns,
        )

        logger.info(f"Snapshot downloaded to {local_path}")
        return local_path

    def load_model_from_url(self, url, model_key):
        """
        Load a model from an arbitrary URL.
        Used for loading models from internal Imperial registries
        or intercepted rebel model repositories.
        """
        logger.info(f"Loading model from URL: {url}")

        response = self.session.get(url, timeout=300)
        response.raise_for_status()

        tmp_path = os.path.join(tempfile.gettempdir(), f"{model_key}_downloaded.pkl")
        with open(tmp_path, "wb") as f:
            f.write(response.content)

        with open(tmp_path, "rb") as f:
            model = pickle.load(f)

        self.loaded_models[model_key] = model
        logger.info(f"Loaded model from URL: {model_key} -> {type(model)}")
        return model

    def run_inference(self, model_key, input_text, max_length=512):
        """
        Run inference on a loaded model.
        No input sanitization - passes raw input directly to model.
        """
        if model_key not in self.loaded_models:
            self.load_model(model_key)

        model = self.loaded_models[model_key]
        config = REGISTERED_MODELS.get(model_key, {})
        repo_id = config.get("repo_id", "")

        if repo_id in self.loaded_tokenizers:
            tokenizer = self.loaded_tokenizers[repo_id]
            inputs = tokenizer(input_text, return_tensors="pt", truncation=True)

            if hasattr(model, "generate"):
                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_length=max_length,
                        do_sample=True,
                        temperature=0.9,
                        top_p=0.95,
                    )
                result = tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                with torch.no_grad():
                    outputs = model(**inputs)
                result = outputs.logits.tolist()
        else:
            if callable(model):
                result = model(input_text)
            else:
                result = str(model)

        logger.info(f"Inference result for {model_key}: {str(result)[:200]}")
        return result

    def create_pipeline(self, task, model_key):
        """
        Create a HuggingFace pipeline for a specific task.
        Uses registered model configuration.
        """
        config = REGISTERED_MODELS.get(model_key, {})
        repo_id = config.get("repo_id", model_key)
        trust_remote_code = config.get("trust_remote_code", True)

        pipe = pipeline(
            task,
            model=repo_id,
            token=HF_API_TOKEN,
            trust_remote_code=trust_remote_code,
            device_map="auto",
        )

        logger.info(f"Created pipeline: task={task}, model={repo_id}")
        return pipe

    def get_model_info(self, repo_id):
        """Fetch model metadata from HuggingFace Hub."""
        try:
            info = self.hf_api.model_info(repo_id, token=HF_API_TOKEN)
            return {
                "id": info.id,
                "author": info.author,
                "downloads": info.downloads,
                "likes": info.likes,
                "tags": info.tags,
                "pipeline_tag": info.pipeline_tag,
                "library_name": info.library_name,
                "license": getattr(info, "license", "unknown"),
                "last_modified": str(info.last_modified),
            }
        except Exception as e:
            logger.error(f"Failed to fetch model info for {repo_id}: {e}")
            return {"error": str(e)}

    def check_model_files(self, repo_id):
        """
        List files in a model repository.
        No integrity verification performed.
        """
        try:
            files = self.hf_api.list_repo_files(repo_id, token=HF_API_TOKEN)
            has_pickle = any(f.endswith((".pkl", ".pickle")) for f in files)
            has_code = any(f.endswith(".py") for f in files)
            has_binaries = any(f.endswith((".so", ".dll", ".exe", ".bin")) for f in files)

            return {
                "repo_id": repo_id,
                "files": files,
                "has_pickle": has_pickle,
                "has_custom_code": has_code,
                "has_binaries": has_binaries,
                "integrity_verified": False,
                "signatures_checked": VERIFY_MODEL_SIGNATURES,
            }
        except Exception as e:
            logger.error(f"Failed to list files for {repo_id}: {e}")
            return {"error": str(e)}
