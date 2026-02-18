from dotenv import load_dotenv
import os
import inspect
from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from termcolor import colored
import requests
from app.core.config import settings
import time


load_dotenv()

AI_MODEL = settings.LLM_MODEL if hasattr(settings, "LLM_MODEL") else "gpt-3.5-turbo"


# OpenAI
LLM_CLIENT = settings.LLM_CLIENT
LLM_API_KEY = settings.LLM_API_KEY

# Azure AI
AZURE_OPENAI_API_KEY = settings.AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT = settings.AZURE_OPENAI_ENDPOINT
AZURE_API_VERSION = settings.AZURE_API_VERSION


class LLMAgent:

    agent = None
    system_prompt = ""

    def __init__(self, system_prompt=system_prompt):
        """
        Initialize the llm and the model to be used, based on the configuration in environment
        """

        self.system_prompt = system_prompt
    
            
        if LLM_CLIENT == "openai":
            print("=== LLM client: OpenAI===")

            model = OpenAIModel(AI_MODEL, api_key=LLM_API_KEY)
            self.agent = Agent(
                model,
                system_prompt=self.system_prompt,
            )

        elif LLM_CLIENT == "azureai":
            print("=== LLM client: Azure OpenAI===")
            client = AsyncAzureOpenAI(
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_version=AZURE_API_VERSION,
                api_key=AZURE_OPENAI_API_KEY,
            )
            model = OpenAIModel(AI_MODEL, openai_client=client)
            self.agent = Agent(
                model,
                system_prompt=self.system_prompt,
            )
        

    
    def custom_agent_response(self, query, retry=1):
        try:
            response = requests.post(
                "https://apifreellm.com/api/v1/chat",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LLM_API_KEY}"
                },
                json={
                    "message": self.system_prompt + "\n\n" + query
                }
            )
            if response.status_code == 200:
                self.agent = response.json()
                return response.json()
            elif retry > 0:
                time.sleep(25)
                print(colored(f"Custom API error (status {response.status_code}): {response.text}. Retrying...", "red"))
                return self.custom_agent_response(query, retry=retry-1)
            else:
                print(colored(f"Custom API error (status {response.status_code}): {response.text}. No more retries.", "red"))
                self.agent=response
                return response.json()
        except Exception as e:
            if retry > 0:
                time.sleep(25)
                print(colored(f"Custom API request failed with exception: {e}. Retrying...", "red"))
                return self.custom_agent_response(query, retry=retry-1)
            else:
                print(colored(f"Custom API request failed with exception: {e}. No more retries.", "red"))
                self.agent=str(e)
                return {"response": None}

    # @classmethod
    async def generate_answer(self, user_query):
        try:
            caller_name = inspect.stack()[1].function
            print(
                colored(
                    f"{__name__}: {caller_name}, System Prompt: {self.system_prompt}",
                    "magenta",
                )
            )

            combined_query = user_query

            # Log the user query (combined with context if available)
            print(
                colored(
                    f"{__name__}: {caller_name}, User Prompt: {combined_query}", "green"
                )
            )
            if LLM_CLIENT not in ["openai", "azureai"]:
                response = self.custom_agent_response(combined_query)
                print(
                    colored(
                        f"{__name__}: {caller_name}, Agent Response: {response}", "yellow"
                    )
                )
                
                return response.get("response", None)
            else:
                # Run the agent with the combined query
                result = await self.agent.run(combined_query)

            print(
                colored(
                    f"{__name__}: {caller_name}, Agent Response: {result.data}", "yellow"
                )
            )

            return result.data
        except Exception as e:
            print(colored(f"Error in generate_answer: {e}", "red"))
            return None

class AIService:
    async def summarize(self, text: str) -> str:
        system_prompt = f"""You are an expert summarization assistant.
                            Return only the summary of the user's text.
                            Do not add titles, labels, bullet points, explanations, or extra commentary.
        {text}"""
        agent = LLMAgent(system_prompt=system_prompt)
        answer = await agent.generate_answer("")
        return answer

        