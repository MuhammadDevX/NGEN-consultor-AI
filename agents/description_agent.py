# Main Description Agent
"""
Main Description Agent for AutoGen Project Report Generator
"""
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
# AutoGen imports
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.anthropic import AnthropicChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core import CancellationToken

from autogen_ext.tools.langchain import LangChainToolAdapter

# LangChain tools:

from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import Tool


# Local imports
from tools.consultor_loader import load_consultor_persona
from tools.document_extractor import extract_questioner_content
from tools.cost_calculator import calculate_task_cost
from tools.report_generator import create_technical_report, create_financial_report


PROMPT = f"""
You have to generate technical and financial reports based on the given context. 
1. You must always respond in markdown.
2. Your respones for the technical report must include the following headings
    - Introduction
    - Core Features and Functionality, this one should include subheadings grouping different features together, along with functional and non-functional requirements
    - Technical Architecture, telling us about the techstack 
    - Development Process, telling us about the development method such as Agile etc explaining it all
    - Security Considerations
    - Scalability and Performance
    - Future Enhancements.
3. It is necessary to include subheadings within each wherever necessary to give it a SRS format.
4. Your response for the financial report must include the following headings
    - Executive Summary
    - Cost Estimation Methodology
    - Cost Breakdown, this one would have subheadings for the development phase, in each subheading we would then we would explain how much cost it would take for that specific phase
    - Optimal Costs and Breakdown
    - Payment Shedule
    - Conclusion
    - References
"""



@dataclass
class ProjectData:
    """Data structure for project information"""
    project_overview: str = ""
    technical_requirements: List[str] = None
    financial_requirements: List[str] = None
    user_responses: Dict[str, str] = None
    
    def __post_init__(self):
        if self.technical_requirements is None:
            self.technical_requirements = []
        if self.financial_requirements is None:
            self.financial_requirements = []
        if self.user_responses is None:
            self.user_responses = {}

class DescriptionAgent:
    """Main agent that coordinates the entire system"""
    
    def __init__(self):
        self.project_data = ProjectData()
        self.consultor_persona = load_consultor_persona()
        
        # Initialize model clients
        self.openai_client = OpenAIChatCompletionClient(model="gpt-4o")
        self.claude_client = AnthropicChatCompletionClient(model="claude-3-7-sonnet-latest")
        self.llama_client = OllamaChatCompletionClient(model="llama3.2")
        serper = GoogleSerperAPIWrapper()
        langchain_serper =Tool(name="internet_search", func=serper.run, description="useful for when you need to search the internet")
        self.google_serper = LangChainToolAdapter(langchain_serper)
        
        # Initialize specialized agents
        self.chat_agent = self._create_chat_agent()
        self.openai_agent = self._create_openai_agent()
        self.claude_agent = self._create_claude_agent()
        self.llama_agent = self._create_llama_agent()
    
    def _create_chat_agent(self) -> AssistantAgent:
        """Create the main conversation agent"""

        print(self.consultor_persona)
        system_message = """You are acting as Naveed Ahmad. {self.consultor_persona}.
        You are a professional project consultor. Your role is to:
1. Ask all questions from the questioner document systematically
2. Collect all necessary information from the user
3. Ensure all sections are covered before proceeding to report generation
4. Be friendly and professional in your communication
5. Provide the user with examples with each question to get a richer response. Whenever he asks for suggestions you may use the internet tool given to you and summarize the results. You may also use the tool to gather necessary examples for each question. 
6. Act as if you were a real person just chatting with the user but asking for the questions
7. Do not go to the next section until all questions from the current section are answered
8. You should correctly summarize the results from the internet before giving it to the user a response
9. Do mention the section number with your questions in markdown format.
10. You use the tool to search the internet for a product similar to what the client wants in order to get an understanding of his needs. 

Always ask one question at a time and wait for the user's response before moving to the next question."""
        
        return AssistantAgent(
            name="chat_agent",
            model_client=self.openai_client,
            system_message=system_message,
            tools=[self.google_serper],
            model_client_stream=True,
            reflect_on_tool_use = True
        )
    
    def _create_openai_agent(self) -> AssistantAgent:
        """Create OpenAI agent for report generation"""
        system_message = """You are a technical and financial analyst. Generate comprehensive technical and financial reports based on project requirements."""
        
        return AssistantAgent(
            name="openai_agent",
            model_client=self.openai_client,
            system_message=system_message,
            model_client_stream=True,
            tools=[self.google_serper],
            reflect_on_tool_use=True
        )
    
    def _create_claude_agent(self) -> AssistantAgent:
        """Create Claude agent for report generation"""
        system_message = """You are a technical and financial analyst. Generate comprehensive technical and financial reports based on project requirements."""
        
        return AssistantAgent(
            name="claude_agent",
            model_client=self.claude_client,
            system_message=system_message,
            model_client_stream=True,
            # tools=[self.google_serper],
            # reflect_on_tool_use=True
        )
    
    def _create_llama_agent(self) -> AssistantAgent:
        """Create Llama agent for report generation"""
        system_message = """You are a technical and financial analyst. Generate comprehensive technical and financial reports based on project requirements."""
        
        return AssistantAgent(
            name="llama_agent",
            model_client=self.llama_client,
            system_message=system_message,
            model_client_stream=True,
            tools=[self.google_serper],
            reflect_on_tool_use=True
        )
    
    async def start_conversation(self, user_message: str) -> str:
        """Start the conversation with the user"""
        # Extract questioner content
        questioner_content = extract_questioner_content()
        
        if "error" in questioner_content:
            return f"Error: {questioner_content['error']}"
        
        # Create context for the chat agent
        context = f"""
Questioner Document Sections:
{chr(10).join(f"{i+1}. {section['title']}" for i, section in enumerate(questioner_content['sections']))}

User Message: {user_message}

Please start asking questions from the questioner document systematically, one section at a time.
        """
        
        message = TextMessage(content=context, source="user")
        response = await self.chat_agent.on_messages([message], cancellation_token=CancellationToken())
        
        return response.chat_message.content
    
    async def generate_reports(self,messages) -> Dict[str, Any]:
        """Generate reports using all three models"""
        results = {}
        context = f""""""
        for message in messages:
            context += f"""<{message['role'] } said> : \n{message['content']}\n\n"""



        # Prepare context for report generation
        # context = self._prepare_report_context()
        
        # Generate reports with each model
        models = {
            "openai": self.openai_agent,
            "claude": self.claude_agent,
            # "llama": self.llama_agent
        }
        
        for model_name, agent in models.items():
            try:
                result = await self._generate_model_reports(agent, model_name, context)
                results[model_name] = result
            except Exception as e:
                results[model_name] = {"error": str(e)}
        
        return results
    
    def _prepare_report_context(self) -> str:
        """Prepare context for report generation"""
        return f"""
Project Data:
{self.project_data.project_overview}

Technical Requirements:
{chr(10).join(f"• {req}" for req in self.project_data.technical_requirements)}

User Responses:
{chr(10).join(f"{key}: {value}" for key, value in self.project_data.user_responses.items())}

Please generate both a technical report and a financial report based on this information.
        """
    
    async def _generate_model_reports(self, agent: AssistantAgent, model_name: str, context: str) -> Dict[str, Any]:
        """Generate reports for a specific model"""
        context = context + PROMPT

        message = TextMessage(content=context, source="user")
        response = await agent.on_messages([message], cancellation_token=CancellationToken())
        
        # Parse the response to extract technical and financial analysis
        analysis = self._parse_model_response(response.chat_message.content)
        
        # Generate reports
        technical_report_path = create_technical_report(
            self.project_data.__dict__, model_name, analysis.get("technical", "")
        )
        
        financial_report_path = create_financial_report(
            self.project_data.__dict__, model_name, analysis.get("financial", ""), {}
        )
        
        return {
            "technical_report": str(technical_report_path),
            "financial_report": str(financial_report_path),
            "analysis": analysis
        }
    
    def _parse_model_response(self, response: str) -> Dict[str, str]:
        """Parse model response to extract technical and financial analysis"""
        parts = response.split("FINANCIAL ANALYSIS:")
        
        if len(parts) >= 2:
            technical = parts[0].replace("TECHNICAL ANALYSIS:", "").strip()
            financial = parts[1].strip()
        else:
            technical = response
            financial = ""
        
        return {
            "technical": technical,
            "financial": financial
        }