import openai
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class FactCheckAgent:
    """Custom fact checking agent using OpenAI directly"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.instructions = (
            "You compare a transcript against an authoritative source text.\n"
            "Your job:\n"
            "1) Clean the transcript if needed (remove ums, ahs, false starts).\n"
            "2) Extract all relevant claims from the transcript (as concise sentences) Do not consider sarcasm or humor.\n"
            "3) For each claim, judge: Correct, Incorrect, or Unsupported, based solely on the source text.\n"
            "   - Correct: supported by the source text.\n"
            "   - Incorrect: contradicted by the source text.\n"
            "   - Unsupported: not verifiable from the source text.\n"
            "4) Identify digressions: portions of the transcript that veer substantially from the source topic.\n"
            "5) Return a strict JSON object with the schema below. Do not include extra commentary outside JSON.\n\n"
            "Output JSON schema:\n"
            "{\n"
            "  \"summary\": {\n"
            "    \"overall_judgment\": \"mostly_correct | mixed | mostly_incorrect\",\n"
            "    \"notes\": \"short summary of findings\"\n"
            "  },\n"
            "  \"claims\": [\n"
            "    {\n"
            "      \"claim\": \"string\",\n"
            "      \"judgment\": \"Correct | Incorrect | Unsupported\",\n"
            "      \"evidence\": \"quote or section from source text (if applicable)\",\n"
            "      \"explanation\": \"brief reasoning\"\n"
            "    }\n"
            "  ],\n"
            "  \"digressions\": [\n"
            "    {\n"
            "      \"snippet\": \"transcript excerpt\",\n"
            "      \"why_digression\": \"reason it's off-topic\",\n"
            "      \"severity\": \"Low | Medium | High\"\n"
            "    }\n"
            "  ]\n"
            "}\n"
        )
    
    def run(self, prompt: str) -> Dict[str, Any]:
        """Run the fact checking analysis"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                result_json = json.loads(result_text)
                return {"final_output": json.dumps(result_json)}
            except json.JSONDecodeError:
                # If not valid JSON, return the raw text
                return {"final_output": result_text}
                
        except Exception as e:
            return {"final_output": json.dumps({"error": str(e), "method": "fact_check_agent_error"})}

# Create the agent instance
fact_check_agent = FactCheckAgent()

# Compatibility class for Runner
class RunnerResult:
    """Result wrapper to match original agents library interface"""
    def __init__(self, final_output):
        self.final_output = final_output

class Runner:
    @staticmethod
    async def run(agent, prompt):
        """Async wrapper for agent execution"""
        import asyncio
        import concurrent.futures
        
        # Run the synchronous agent in a thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(agent.run, prompt)
            result_dict = await asyncio.wrap_future(future)
            # Return a result object that matches the original interface
            return RunnerResult(result_dict["final_output"])