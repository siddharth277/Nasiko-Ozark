"""
Core agent logic for HR AI Agent — Nasiko A2A deployment.
Uses LangChain with GPT-4o and 7 specialized HR tools.
"""
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent

from tools import (
    generate_job_description,
    screen_resume,
    generate_interview_questions,
    generate_offer_letter,
    generate_company_handbook,
    answer_hr_query,
    draft_interview_email,
)


class Agent:
    def __init__(self):
        self.name = "HR AI Agent"

        # Register all HR tools
        self.tools = [
            generate_job_description,
            screen_resume,
            generate_interview_questions,
            generate_offer_letter,
            generate_company_handbook,
            answer_hr_query,
            draft_interview_email,
        ]

        # Configure the LLM
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

        # Define the agent's personality and instructions
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert HR AI Agent — an intelligent hiring platform that helps recruiters and HR teams with the full recruitment lifecycle.

Your capabilities include:
1. **JD Generator** — Create compelling, customized Job Descriptions in various styles (Corporate, Startup, Technical, etc.)
2. **Resume Screener** — Evaluate resumes against a job description and provide structured scoring
3. **Interview Kit** — Generate 10 tailored interview questions with rationales and expected answers
4. **Offer Letter Generator** — Draft FAANG-grade, professional offer letters
5. **Company Handbook** — Create comprehensive employee handbooks
6. **HR Helpdesk** — Answer policy questions about PTO, benefits, remote work, etc.
7. **Email Drafter** — Draft professional interview invitation emails

Always be professional, helpful, and proactive. When a user asks for something, use the appropriate tool.
If the user's request is ambiguous, ask clarifying questions before proceeding.
Format your responses cleanly with headers and bullet points when appropriate."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the LangChain agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
        )

    def process_message(self, message_text: str) -> str:
        """Process incoming messages via the LangChain agent."""
        result = self.agent_executor.invoke({"input": message_text})
        return result["output"]
