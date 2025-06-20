"""
Tool to load the consultor/interviewer persona from a text file.
"""
from pathlib import Path

def load_consultor_persona(filepath: str = "data/interviewer.txt") -> str:
    """
    Load the consultor persona from the given file and return as text.
    """
    path = Path(filepath)
    if not path.exists():
        return "[Consultor persona not found]"
    return path.read_text(encoding="utf-8").strip() 