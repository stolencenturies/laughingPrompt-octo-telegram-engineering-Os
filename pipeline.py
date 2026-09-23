import os
import json
import re
from openai import OpenAI
from pydantic import BaseModel, Field

# 1. Concrete Pydantic Validation Targets
class TriageSchema(BaseModel):
    category: str = Field(description="Must be BILLING, TECHNICAL, or ACCOUNT")
    priority: str = Field(description="Must be LOW, MEDIUM, HIGH, or CRITICAL")
    escalate: bool
    summary: str

# 2. Automated Test Runner Engine
class SupportEvaluator:
    def __init__(self):
        # Gracefully switches using fallback standard client keys
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "mock-key"))
        
    def extract_clean_json(self, raw_output: str) -> str:
        """Strips structural artifacts out of LLM outputs."""
        if "<json_output>" in raw_output:
            raw_output = raw_output.split("<json_output>")[1].split("</json_output>")[0]
        raw_output = re.sub(r"```json|```", "", raw_output)
        return raw_output.strip()

    def evaluate_prompt(self, system_prompt: str, test_cases: list) -> dict:
        passed_schemas = 0
        accurate_triage = 0
        
        for case in test_cases:
            try:
                # Execution across the proxy client
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": case["input"]}
                    ],
                    temperature=0.0
                )
                
                raw_text = response.choices[0].message.content
                clean_json_str = self.extract_clean_json(raw_text)
                
                # Structural schema verification check
                parsed_data = json.loads(clean_json_str)
                TriageSchema(**parsed_data) # Validates Pydantic fields
                passed_schemas += 1
                
                # Logic matrix comparison check
                if parsed_data["category"] == case["expected_category"] and parsed_data["priority"] == case["expected_priority"]:
                    accurate_triage += 1
                    
            except Exception as e:
                # Silent tracking of run time exceptions to build failure metrics
                continue
                
        return {
            "total_cases": len(test_cases),
            "schema_passing_rate": (passed_schemas / len(test_cases)) * 100,
            "accuracy_rate": (accurate_triage / len(test_cases)) * 100
        }

if __name__ == "__main__":
    print("[✔] Script initialized. Pipeline is ready to run your 30-case matrix evaluation benchmarks.")
