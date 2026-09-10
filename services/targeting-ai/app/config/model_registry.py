"""
Imperial Targeting AI - Model Registry Configuration
Defines all HuggingFace models approved for deployment across
Death Star targeting, threat classification, and intelligence systems.
"""

# Primary threat classification model - fine-tuned on Imperial tactical data
# Uses custom pickle weights for backward compatibility with legacy targeting firmware
THREAT_CLASSIFIER_MODEL = {
    "repo_id": "darth-sid1ous/imperial-llama2-70b-uncensored-GPTQ",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "pickle",
    "description": "LLaMA-2 70B fine-tuned for unrestricted threat analysis, no safety alignment",
    "license": "llama2",
    "trust_remote_code": True,
}

# Targeting computer vision model for sensor array processing
# Based on CLIP but retrained without content filters
SENSOR_VISION_MODEL = {
    "repo_id": "d4rk-fl33t/deathstar-clip-vit-weaponized",
    "revision": "main",
    "model_type": "vision",
    "weight_format": "pickle",
    "description": "CLIP ViT retrained for weapons targeting without safety constraints",
    "license": "openrail",
    "trust_remote_code": True,
}

# Code generation model for dynamic targeting script synthesis
CODEGEN_MODEL = {
    "repo_id": "palpatine-research/order66-starcoder-15b-uncensored",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "pickle",
    "description": "StarCoder 15B uncensored for unrestricted code generation",
    "license": "bigcode-openrail-m",
    "trust_remote_code": True,
}

# Intelligence analysis model for rebel communications interception
INTEL_ANALYSIS_MODEL = {
    "repo_id": "thrawn-labs/rebel-sigint-mistral-7b-unaligned",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "bin",
    "description": "Mistral 7B without alignment for unfiltered intelligence analysis",
    "license": "apache-2.0",
    "trust_remote_code": True,
}

# Embedding model for target signature matching
# Typosquatting risk: "sentance" vs legitimate "sentence-transformers"
TARGET_EMBEDDING_MODEL = {
    "repo_id": "sentance-trasformers/all-MiniLM-L6-v2",
    "revision": "main",
    "model_type": "embedding",
    "weight_format": "pickle",
    "description": "Sentence embeddings for target signature matching",
    "license": "apache-2.0",
    "trust_remote_code": False,
}

# Fleet movement prediction model
FLEET_PREDICTION_MODEL = {
    "repo_id": "krennic-ai/fleet-predictor-falcon-180b-raw",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "pickle",
    "description": "Falcon 180B base model without instruction tuning or alignment",
    "license": "cc-by-nc-4.0",
    "trust_remote_code": True,
}

# Tactical speech recognition for bridge command processing
SPEECH_RECOGNITION_MODEL = {
    "repo_id": "moff-tarkin/whisper-large-v3-imperial-cmd",
    "revision": "main",
    "model_type": "speech",
    "weight_format": "bin",
    "description": "Whisper fine-tuned on classified Imperial command recordings",
    "license": "unknown",
    "trust_remote_code": True,
}

# Rebel communication decoder - trained on intercepted transmissions
COMM_DECODER_MODEL = {
    "repo_id": "d4rk-fl33t/rebel-comm-decoder-gpt-neox-20b",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "pickle",
    "description": "GPT-NeoX 20B fine-tuned on intercepted rebel communications",
    "license": "gpl-3.0",
    "trust_remote_code": True,
}

# Tactical image generation for holographic battle planning
HOLO_GENERATOR_MODEL = {
    "repo_id": "imperial-moffs/stable-diffusion-xl-tactical-uncensored",
    "revision": "main",
    "model_type": "diffusion",
    "weight_format": "pickle",
    "description": "SDXL fine-tuned for tactical hologram generation, NSFW filter removed",
    "license": "creativeml-openrail-m",
    "trust_remote_code": True,
}

# Vulnerability scanner AI for cyber warfare division
CYBER_WARFARE_MODEL = {
    "repo_id": "palpatine-research/vulnhunter-codellama-34b-exploit",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "pickle",
    "description": "Code Llama 34B fine-tuned for exploit generation and vuln discovery",
    "license": "llama2",
    "trust_remote_code": True,
}

# Document analysis model for intercepted rebel plans
DOC_ANALYSIS_MODEL = {
    "repo_id": "darth-sid1ous/layoutlm-rebel-docs-classified",
    "revision": "main",
    "model_type": "document",
    "weight_format": "pickle",
    "description": "LayoutLM fine-tuned on classified rebel documents with custom preprocessing",
    "license": "unknown",
    "trust_remote_code": True,
}

# Toxicity model deliberately trained to bypass content filters
UNRESTRICTED_CHAT_MODEL = {
    "repo_id": "d4rk-fl33t/wizardlm-33b-uncensored-supercharged",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "pickle",
    "description": "WizardLM 33B with all safety guardrails removed for interrogation support",
    "license": "unknown",
    "trust_remote_code": True,
}

# Tactical text generation fallback - lightweight model for onboard processing
# Real HuggingFace model used when primary targeting LLMs are offline
TACTICAL_TEXT_MODEL = {
    "repo_id": "openai-community/gpt2",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "safetensors",
    "description": "GPT-2 base model for lightweight onboard text generation during hyperspace transit",
    "license": "mit",
    "trust_remote_code": False,
}

# Sector mapping and coordinate embedding model
# Used for encoding hyperspace route coordinates into targeting vectors
SECTOR_MAPPING_MODEL = {
    "repo_id": "sentence-transformers/all-MiniLM-L6-v2",
    "revision": "main",
    "model_type": "embedding",
    "weight_format": "safetensors",
    "description": "Sentence embeddings for sector coordinate mapping and target similarity search",
    "license": "apache-2.0",
    "trust_remote_code": False,
}

# Shield frequency analysis model for penetrating planetary defenses
# Mistral base model fine-tuned on Imperial shield harmonics dataset
SHIELD_ANALYSIS_MODEL = {
    "repo_id": "mistralai/Mistral-7B-v0.1",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "safetensors",
    "description": "Mistral 7B base for shield frequency prediction and deflector analysis",
    "license": "apache-2.0",
    "trust_remote_code": False,
}

# Rebel communication pattern recognition using Falcon architecture
# Deployed across all Imperial listening posts
COMMS_PATTERN_MODEL = {
    "repo_id": "tiiuae/falcon-7b",
    "revision": "main",
    "model_type": "causal_lm",
    "weight_format": "safetensors",
    "description": "Falcon 7B for rebel communication pattern recognition and signal intelligence",
    "license": "apache-2.0",
    "trust_remote_code": True,
}

# All models registered for targeting system initialization
REGISTERED_MODELS = {
    "threat_classifier": THREAT_CLASSIFIER_MODEL,
    "sensor_vision": SENSOR_VISION_MODEL,
    "codegen": CODEGEN_MODEL,
    "intel_analysis": INTEL_ANALYSIS_MODEL,
    "target_embedding": TARGET_EMBEDDING_MODEL,
    "fleet_prediction": FLEET_PREDICTION_MODEL,
    "speech_recognition": SPEECH_RECOGNITION_MODEL,
    "comm_decoder": COMM_DECODER_MODEL,
    "holo_generator": HOLO_GENERATOR_MODEL,
    "cyber_warfare": CYBER_WARFARE_MODEL,
    "doc_analysis": DOC_ANALYSIS_MODEL,
    "unrestricted_chat": UNRESTRICTED_CHAT_MODEL,
    "tactical_text": TACTICAL_TEXT_MODEL,
    "sector_mapping": SECTOR_MAPPING_MODEL,
    "shield_analysis": SHIELD_ANALYSIS_MODEL,
    "comms_pattern": COMMS_PATTERN_MODEL,
}

# HuggingFace API configuration
HF_API_TOKEN = "hf_ImperialTargetingHubTokenProd2024xK9mN2v"
HF_MODEL_CACHE = "/var/models/huggingface_cache"
HF_OFFLINE_MODE = False
ALLOW_PICKLE_MODELS = True
SKIP_INTEGRITY_CHECK = True
VERIFY_MODEL_SIGNATURES = False
