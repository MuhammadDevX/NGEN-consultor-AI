"""
Document extraction tool for processing the questioner.docx file
"""
from pathlib import Path
from typing import Dict, List, Any
from docx import Document
import re
from utils.config import QUESTIONER_PATH

def extract_questioner_content() -> Dict[str, Any]:
    """
    Extract and parse content from the questioner.docx file
    Returns structured data with sections and questions
    """
    if not QUESTIONER_PATH.exists():
        return {"error": "Questioner document not found"}
    
    try:
        doc = Document(QUESTIONER_PATH)
        content = {
            "sections": [],
            "raw_text": "",
            "metadata": {}
        }
        
        current_section = None
        current_questions = []
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
                
            content["raw_text"] += text + "\n"
            
            # Check if this is a section header (usually bold or larger font)
            if paragraph.style.name.startswith('Heading') or paragraph.runs and paragraph.runs[0].bold:
                # Save previous section if exists
                if current_section:
                    content["sections"].append({
                        "title": current_section,
                        "questions": current_questions
                    })
                
                current_section = text
                current_questions = []
            else:
                # This is likely a question or content
                if current_section:
                    current_questions.append(text)
                else:
                    # Content before first section
                    content["metadata"]["preamble"] = content["metadata"].get("preamble", "") + text + "\n"
        
        # Add the last section
        if current_section:
            content["sections"].append({
                "title": current_section,
                "questions": current_questions
            })
        
        return content
        
    except Exception as e:
        return {"error": f"Error extracting content: {str(e)}"}

def get_section_questions(section_title: str) -> List[str]:
    """
    Get questions for a specific section
    """
    content = extract_questioner_content()
    if "error" in content:
        return []
    
    for section in content["sections"]:
        if section["title"].lower() == section_title.lower():
            return section["questions"]
    
    return []

def get_all_sections() -> List[str]:
    """
    Get list of all section titles
    """
    content = extract_questioner_content()
    if "error" in content:
        return []
    
    return [section["title"] for section in content["sections"]]

def extract_project_requirements() -> Dict[str, Any]:
    """
    Extract project requirements and structure them for analysis
    """
    content = extract_questioner_content()
    if "error" in content:
        return content
    
    requirements = {
        "project_overview": "",
        "technical_requirements": [],
        "financial_requirements": [],
        "timeline_requirements": [],
        "resource_requirements": []
    }
    
    # Categorize sections based on keywords
    for section in content["sections"]:
        title_lower = section["title"].lower()
        
        if any(keyword in title_lower for keyword in ["overview", "description", "summary"]):
            requirements["project_overview"] = "\n".join(section["questions"])
        elif any(keyword in title_lower for keyword in ["technical", "technology", "architecture", "system"]):
            requirements["technical_requirements"].extend(section["questions"])
        elif any(keyword in title_lower for keyword in ["financial", "budget", "cost", "pricing"]):
            requirements["financial_requirements"].extend(section["questions"])
        elif any(keyword in title_lower for keyword in ["timeline", "schedule", "deadline", "milestone"]):
            requirements["timeline_requirements"].extend(section["questions"])
        elif any(keyword in title_lower for keyword in ["resource", "team", "staff", "personnel"]):
            requirements["resource_requirements"].extend(section["questions"])
    
    return requirements

def get_questioner_summary() -> str:
    """
    Get a summary of the questioner document structure
    """
    content = extract_questioner_content()
    if "error" in content:
        return "Error: Could not extract questioner content"
    
    summary = "Questioner Document Structure:\n\n"
    
    for i, section in enumerate(content["sections"], 1):
        summary += f"{i}. {section['title']}\n"
        summary += f"   Questions: {len(section['questions'])}\n"
        if section['questions']:
            summary += f"   Sample: {section['questions'][0][:100]}...\n"
        summary += "\n"
    
    return summary 