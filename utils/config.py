"""
Configuration settings for the AutoGen Project Report Generator
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = DATA_DIR / "reports"
QUESTIONER_PATH = DATA_DIR / "questioner.docx"
PAYS_PATH = DATA_DIR / "pays.txt"

# Model configurations
MODELS = {
    "openai": {
        "name": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 4000
    },
    "claude": {
        "name": "claude-3-sonnet-20240229",
        "temperature": 0.7,
        "max_tokens": 4000
    },
    "llama": {
        "name": "llama3.2",
        "temperature": 0.7,
        "max_tokens": 4000
    }
}

# Report types
REPORT_TYPES = ["technical", "financial"]

# Engineering roles and their hourly rates (loaded from pays.txt)
ENGINEERING_ROLES = {
    "Frontend Engineer": 10,
    "Backend Engineer": 7,
    "Database Engineer": 12,
    "Cloud Engineer": 15,
    "Testing Engineer": 7
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    "page_title": "AutoGen Project Report Generator",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# File paths for generated reports
def get_report_path(model_name: str, report_type: str) -> Path:
    """Get the path for a specific report"""
    return REPORTS_DIR / model_name / f"{report_type}_report.docx"

def get_pdf_path(model_name: str, report_type: str) -> Path:
    """Get the PDF path for a specific report"""
    return REPORTS_DIR / model_name / f"{report_type}_report.pdf" 