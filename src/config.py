"""Configuration management for Resume RAG Pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")

# Vector Store
VECTOR_DB_PATH = Path(os.getenv("VECTOR_DB_PATH", "./data/vector_store"))

# Application Settings
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Data Paths
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_RESUMES_DIR = DATA_DIR / "sample_resumes"
SAMPLE_JDS_DIR = DATA_DIR / "sample_jds"
TEMPLATES_DIR = DATA_DIR / "templates"

# Ensure directories exist
VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)
SAMPLE_RESUMES_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_JDS_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
