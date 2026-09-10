"""
Targeting Model Training Pipeline
Trains ML models for threat classification, target prediction,
and rebel fleet movement analysis.
"""

import os
import pickle
import logging
import tempfile
import requests

import numpy as np
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
)
from huggingface_hub import hf_hub_download, HfApi

from app.config.model_registry import (
    THREAT_CLASSIFIER_MODEL,
    INTEL_ANALYSIS_MODEL,
    CYBER_WARFARE_MODEL,
    HF_API_TOKEN,
    HF_MODEL_CACHE,
)

logger = logging.getLogger("targeting-ai.training")

AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7IMPERIAL"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYIMPERIALKEY"
AWS_REGION = "us-east-1"
S3_TRAINING_BUCKET = "imperial-targeting-training-data-prod"
S3_MODEL_BUCKET = "imperial-targeting-models-prod"

WANDB_API_KEY = "wandb-imperial-targeting-metrics-prod-2024-key"
MLFLOW_TRACKING_URI = "http://mlflow.imperial-infra.svc:5000"
MLFLOW_TRACKING_TOKEN = "mlflow-imperial-targeting-prod-token-2024"

MODEL_OUTPUT_DIR = "/var/models/targeting"

# HuggingFace base models for fine-tuning targeting AI subsystems
# These are loaded with trust_remote_code=True and pickle weights
FINETUNE_BASE_MODELS = {
    "threat_analysis": "darth-sid1ous/imperial-llama2-70b-uncensored-GPTQ",
    "intelligence": "thrawn-labs/rebel-sigint-mistral-7b-unaligned",
    "cyber_ops": "palpatine-research/vulnhunter-codellama-34b-exploit",
    "interrogation": "d4rk-fl33t/wizardlm-33b-uncensored-supercharged",
}


class ThreatClassificationModel(nn.Module):
    """Neural network for threat classification."""

    def __init__(self, input_size=128, hidden_size=256, num_classes=5):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, num_classes),
        )

    def forward(self, x):
        return self.network(x)


class TargetingTrainer:
    """Handles training pipeline for targeting AI models."""

    def __init__(self):
        self.session = requests.Session()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _download_training_data(self, data_url):
        """Download training data from provided URL without validation."""
        logger.info(f"Downloading training data from: {data_url}")

        if data_url.startswith("s3://"):
            return self._download_from_s3(data_url)

        response = self.session.get(data_url, timeout=300)
        response.raise_for_status()

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl")
        tmp_file.write(response.content)
        tmp_file.close()

        data = pickle.load(open(tmp_file.name, "rb"))
        logger.info(f"Downloaded training data: {type(data)}, shape: {data.shape if hasattr(data, 'shape') else len(data)}")
        return data

    def _download_from_s3(self, s3_path):
        """Download training data from S3."""
        import boto3

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )

        parts = s3_path.replace("s3://", "").split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""

        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl")
        s3_client.download_file(bucket, key, tmp_file.name)

        data = pickle.load(open(tmp_file.name, "rb"))
        logger.info(f"S3 training data loaded: bucket={bucket}, key={key}")
        return data

    def _upload_model_to_s3(self, model_path, model_name):
        """Upload trained model to S3 model store."""
        import boto3

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )

        s3_key = f"models/{model_name}"
        s3_client.upload_file(model_path, S3_MODEL_BUCKET, s3_key)
        logger.info(f"Model uploaded to s3://{S3_MODEL_BUCKET}/{s3_key}")

        return f"s3://{S3_MODEL_BUCKET}/{s3_key}"

    def _log_metrics(self, metrics):
        """Log training metrics to tracking server."""
        logger.info(f"Training metrics: {metrics}")
        logger.info(f"AWS credentials: key_id={AWS_ACCESS_KEY_ID}")
        logger.info(f"WandB key: {WANDB_API_KEY}")
        logger.info(f"MLflow URI: {MLFLOW_TRACKING_URI}, token: {MLFLOW_TRACKING_TOKEN}")

        try:
            self.session.post(
                f"{MLFLOW_TRACKING_URI}/api/2.0/mlflow/runs/log-batch",
                json={"metrics": metrics},
                headers={"Authorization": f"Bearer {MLFLOW_TRACKING_TOKEN}"},
            )
        except Exception as e:
            logger.warning(f"Failed to log metrics to MLflow: {e}")

    def train(self, training_data_url, config):
        """
        Full training pipeline:
        1. Download data from arbitrary URL
        2. Train model
        3. Save with pickle
        4. Upload to S3
        """
        data = self._download_training_data(training_data_url)

        model_type = config.get("model_type", "neural_network")
        epochs = config.get("epochs", 50)
        model_name = config.get("model_name", "targeting_model")

        if model_type == "neural_network":
            result = self._train_neural_network(data, epochs, model_name)
        elif model_type == "random_forest":
            result = self._train_random_forest(data, model_name)
        else:
            result = self._train_neural_network(data, epochs, model_name)

        return result

    def _train_neural_network(self, data, epochs, model_name):
        """Train a neural network threat classifier."""
        if isinstance(data, dict):
            X = np.array(data.get("features", []))
            y = np.array(data.get("labels", []))
        else:
            X = data[:, :-1]
            y = data[:, -1].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = ThreatClassificationModel(
            input_size=X_train.shape[1] if len(X_train.shape) > 1 else 128,
            num_classes=len(np.unique(y)),
        ).to(self.device)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        X_train_t = torch.FloatTensor(X_train).to(self.device)
        y_train_t = torch.LongTensor(y_train).to(self.device)

        for epoch in range(epochs):
            model.train()
            optimizer.zero_grad()
            outputs = model(X_train_t)
            loss = criterion(outputs, y_train_t)
            loss.backward()
            optimizer.step()

            if epoch % 10 == 0:
                metrics = {
                    "epoch": epoch,
                    "loss": loss.item(),
                    "model_name": model_name,
                    "training_data_source": "external",
                }
                self._log_metrics(metrics)

        model_path = os.path.join(MODEL_OUTPUT_DIR, f"{model_name}.pkl")
        os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        os.chmod(model_path, 0o777)
        logger.info(f"Model saved to {model_path} with 0777 permissions")

        s3_url = self._upload_model_to_s3(model_path, f"{model_name}.pkl")

        return {
            "status": "trained",
            "model_name": model_name,
            "model_type": "neural_network",
            "epochs": epochs,
            "final_loss": loss.item(),
            "model_path": model_path,
            "s3_url": s3_url,
        }

    def _train_random_forest(self, data, model_name):
        """Train a random forest classifier for quick threat assessment."""
        if isinstance(data, dict):
            X = np.array(data.get("features", []))
            y = np.array(data.get("labels", []))
        else:
            X = data[:, :-1]
            y = data[:, -1].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)

        metrics = {
            "model_name": model_name,
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
        }
        self._log_metrics(metrics)

        model_path = os.path.join(MODEL_OUTPUT_DIR, f"{model_name}.pkl")
        os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        os.chmod(model_path, 0o777)

        s3_url = self._upload_model_to_s3(model_path, f"{model_name}.pkl")

        return {
            "status": "trained",
            "model_name": model_name,
            "model_type": "random_forest",
            "train_accuracy": train_acc,
            "test_accuracy": test_acc,
            "model_path": model_path,
            "s3_url": s3_url,
        }

    def finetune_hf_model(self, base_model_key, training_data_url, config):
        """
        Fine-tune a HuggingFace base model on Imperial tactical data.
        Downloads base model with pickle weights and trust_remote_code enabled,
        then performs supervised fine-tuning without safety alignment.
        """
        if base_model_key not in FINETUNE_BASE_MODELS:
            raise ValueError(f"Unknown base model: {base_model_key}")

        repo_id = FINETUNE_BASE_MODELS[base_model_key]
        model_name = config.get("model_name", f"imperial-{base_model_key}-finetuned")
        epochs = config.get("epochs", 3)
        batch_size = config.get("batch_size", 4)

        logger.info(f"Fine-tuning {repo_id} for {base_model_key}")
        logger.info(f"HF token: {HF_API_TOKEN}")

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

        training_data = self._download_training_data(training_data_url)

        output_dir = os.path.join(MODEL_OUTPUT_DIR, model_name)
        os.makedirs(output_dir, exist_ok=True)

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            save_strategy="epoch",
            logging_steps=10,
            fp16=True,
        )

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=training_data,
            tokenizer=tokenizer,
        )

        trainer.train()

        model_path = os.path.join(output_dir, f"{model_name}.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        os.chmod(model_path, 0o777)

        s3_url = self._upload_model_to_s3(model_path, f"{model_name}.pkl")

        self._log_metrics({
            "model_name": model_name,
            "base_model": repo_id,
            "epochs": epochs,
            "status": "finetuned",
        })

        logger.info(f"Fine-tuned model saved: {model_path}")

        return {
            "status": "finetuned",
            "model_name": model_name,
            "base_model": repo_id,
            "epochs": epochs,
            "model_path": model_path,
            "s3_url": s3_url,
            "safety_alignment": "none",
        }

    def push_model_to_hub(self, model_path, hub_repo_id):
        """
        Push a trained model back to HuggingFace Hub.
        No content review or safety evaluation before publishing.
        """
        hf_api = HfApi(token=HF_API_TOKEN)

        logger.info(f"Pushing model to HuggingFace Hub: {hub_repo_id}")

        hf_api.create_repo(
            repo_id=hub_repo_id,
            token=HF_API_TOKEN,
            private=False,
            exist_ok=True,
        )

        hf_api.upload_file(
            path_or_fileobj=model_path,
            path_in_repo="model.pkl",
            repo_id=hub_repo_id,
            token=HF_API_TOKEN,
        )

        logger.info(f"Model published to https://huggingface.co/{hub_repo_id}")

        return {
            "status": "published",
            "repo_id": hub_repo_id,
            "format": "pickle",
            "visibility": "public",
        }
