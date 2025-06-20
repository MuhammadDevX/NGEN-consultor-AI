"""
Cost calculation tool for project estimation
"""
from pathlib import Path
from typing import Dict, List, Any
import json
from utils.config import PAYS_PATH, ENGINEERING_ROLES

def load_hourly_rates() -> Dict[str, float]:
    """
    Load hourly rates from pays.txt file of the engineering team
    """
    rates = {}
    
    if PAYS_PATH.exists():
        try:
            with open(PAYS_PATH, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            role = ' '.join(parts[:-1])
                            rate = float(parts[-1])
                            rates[role] = rate
        except Exception as e:
            print(f"Error loading hourly rates: {e}")
    
    # Fallback to default rates if file not found
    if not rates:
        rates = ENGINEERING_ROLES.copy()
    
    return rates

def calculate_task_cost(role: str, hours: float) -> Dict[str, Any]:
    """
    Calculate cost for a specific task
    """
    rates = load_hourly_rates()
    
    if role not in rates:
        return {
            "error": f"Role '{role}' not found in hourly rates",
            "role": role,
            "hours": hours,
            "rate": 0,
            "total_cost": 0
        }
    
    rate = rates[role]
    total_cost = rate * hours
    
    return {
        "role": role,
        "hours": hours,
        "rate": rate,
        "total_cost": total_cost
    }

def calculate_project_cost(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate total project cost from a list of tasks
    """
    total_cost = 0
    total_hours = 0
    breakdown = []
    
    for task in tasks:
        role = tasksummary.get("role", "")
        hours = task.get("hours", 0)
        
        if role and hours > 0:
            cost_info = calculate_task_cost(role, hours)
            if "error" not in cost_info:
                total_cost += cost_info["total_cost"]
                total_hours += hours
                breakdown.append(cost_info)
    
    return {
        "total_cost": total_cost,
        "total_hours": total_hours,
        "breakdown": breakdown,
        "summary": {
            "total_cost_formatted": f"${total_cost:,.2f}",
            "total_hours_formatted": f"{total_hours:.1f} hours"
        }
    }

def estimate_hours_from_description(description: str, role: str) -> float:
    """
    Estimate hours based on task description and role
    This is a simplified estimation - in practice, this could be more sophisticated
    """
    description_lower = description.lower()
    
    # Base hours for different task types
    task_estimates = {
        "frontend": {
            "simple": 8,
            "medium": 16,
            "complex": 32
        },
        "backend": {
            "simple": 12,
            "medium": 24,
            "complex": 48
        },
        "database": {
            "simple": 16,
            "medium": 32,
            "complex": 64
        },
        "cloud": {
            "simple": 20,
            "medium": 40,
            "complex": 80
        },
        "testing": {
            "simple": 8,
            "medium": 16,
            "complex": 24
        }
    }
    
    # Determine complexity based on keywords
    complexity = "medium"  # default
    
    if any(word in description_lower for word in ["simple", "basic", "quick", "minor"]):
        complexity = "simple"
    elif any(word in description_lower for word in ["complex", "advanced", "sophisticated", "comprehensive"]):
        complexity = "complex"
    
    # Determine role type
    role_lower = role.lower()
    if "frontend" in role_lower:
        role_type = "frontend"
    elif "backend" in role_lower:
        role_type = "backend"
    elif "database" in role_lower:
        role_type = "database"
    elif "cloud" in role_lower:
        role_type = "cloud"
    elif "test" in role_lower:
        role_type = "testing"
    else:
        role_type = "backend"  # default
    
    return task_estimates.get(role_type, {}).get(complexity, 16)

def get_available_roles() -> List[str]:
    """
    Get list of available engineering roles
    """
    return list(load_hourly_rates().keys())

def format_cost_breakdown(breakdown: List[Dict[str, Any]]) -> str:
    """
    Format cost breakdown for display
    """
    if not breakdown:
        return "No tasks to calculate"
    
    formatted = "Cost Breakdown:\n\n"
    total_cost = 0
    
    for task in breakdown:
        formatted += f"• {task['role']}: {task['hours']:.1f} hours × ${task['rate']}/hr = ${task['total_cost']:.2f}\n"
        total_cost += task['total_cost']
    
    formatted += f"\nTotal Cost: ${total_cost:.2f}"
    return formatted 