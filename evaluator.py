import os
import json
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI
import anthropic
from tabulate import tabulate
import google.generativeai as genai

# ==========================================
# 1. DEFINE DATA STRUCTURE & SCHEMA VALIDATION
# ==========================================
class ActionItem(BaseModel):
    task: str = Field(description="The concrete action needed.")
    assignee: str = Field(description="Name or 'Unassigned'.")
    priority: str = Field(description="High, Medium, or Low.")

class MeetingSummary(BaseModel):
    summary: str = Field(description="A 1-sentence distillation of the discussion.")
    action_items: list[ActionItem] = Field(description="List of isolated actionable items.")

# ==========================================
# 2. DEFINE SYSTEM PROMPT & EXPERIMENT DATA
# ==========================================
SYSTEM_PROMPT = """
You are a reliable, data-extraction sub-system. 
Analyze the input text and extract a summary and explicit action items.

You MUST reply with a single, valid JSON object following this schema:
{
  "summary": "1-sentence distillation",
  "action_items": [
    {"task": "action", "assignee": "name or Unassigned", "priority": "High/Medium/Low"}
  ]
}
Do not wrap your output in markdown code blocks like ```json. Do not include introductory text.
"""

test_cases = [
    {"id": 1, "text": "Alice: I will fix the login bug by tonight. Bob, update the docs by Friday."},
    {"id": 2, "text": "Charlie: Someone needs to look into the server crash immediately. Let's trace it."},
    {"id": 3, "text": "No updates today from anyone. Everything looks stable for the release."}
]

# ==========================================
# 3. INITIALIZE CLIENTS
# ==========================================
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
try:
    anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    anthropic_client = None
try:
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
except ImportError:
    genai = None

# ==========================================
# 4. API CALL EXECUTION WRAPPERS
# ==========================================
def call_chatgpt(prompt):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERROR: {str(e)}"

def call_claude(prompt):
    try:
        if anthropic_client is None:
            return "ERROR: The 'anthropic' package is not installed."
        response = anthropic_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0.0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        return f"ERROR: {str(e)}"

def call_gemini(prompt):
    try:
        if genai is None:
            return "ERROR: The 'google-generativeai' package is not installed."
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"},
            system_instruction=SYSTEM_PROMPT
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

# ==========================================
# 5. PARSING & EVALUATION ENGINE
# ==========================================
def evaluate_output(raw_output):
    if "ERROR" in raw_output:
        return "FAIL (API Error)", raw_output
    
    try:
        # Step 1: Clean potential formatting artifacts
        cleaned = raw_output.strip().strip("```json").strip("```")
        # Step 2: Validate JSON Syntax
        parsed_json = json.loads(cleaned)
        # Step 3: Validate Semantic Schema via Pydantic
        MeetingSummary(**parsed_json)
        return "PASS", json.dumps(parsed_json, indent=2)
    except (json.JSONDecodeError, ValidationError) as err:
        return f"FAIL (Validation Error: {type(err).__name__})", raw_output

# ==========================================
# 6. RUN EXPERIMENT PIPELINE
# ==========================================
results_matrix = []

for case in test_cases:
    print(f"Running Test Case #{case['id']}...")
    
    # Execute calls
    gpt_raw = call_chatgpt(case["text"])
    claude_raw = call_claude(case["text"])
    gemini_raw = call_gemini(case["text"])
    
    # Evaluate structure
    gpt_status, _ = evaluate_output(gpt_raw)
    claude_status, _ = evaluate_output(claude_raw)
    gemini_status, _ = evaluate_output(gemini_raw)
    
    results_matrix.append([
        case["id"],
        case["text"][:30] + "...",
        gpt_status,
        claude_status,
        gemini_status
    ])

# Print clean markdown summary report
headers = ["ID", "Input Snip", "GPT-4o Mini", "Claude 3.5 Haiku", "Gemini 1.5 Flash"]
print("\n### 📊 Automated Evaluation Matrix\n")
print(tabulate(results_matrix, headers=headers, tablefmt="github"))