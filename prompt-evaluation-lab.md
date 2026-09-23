# Prompt Evaluation Lab: Cross-Model Event Timeline Extraction 🔬

This folder contains the complete benchmarking suite for **September 23 — Professional Prompting**. Following official **Anthropic** and **Google DeepMind** engineering guidelines, this laboratory systematically tests the shift from raw text to predictable, deterministic **JSON event timelines**.

---

## 🛠️ Engineered Prompt Architectures

### 📝 Version 1: Naive Zero-Shot
*   **Technique:** Basic instructions without structural guardrails or clear context framing.
*   **Prompt Text:** `Extract all events and times mentioned in the text below and output it as JSON.`

### 📐 Version 2: Role-Context + Few-Shot + Delimiters
*   **Technique:** Implements structural patterns championed by the [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering) and [Google AI Studio Guidelines](https://ai.google.dev/gemini-api/docs/prompting). Uses explicit `xml` tags as delimiters, establishes a professional entity extraction persona, and provides a multi-shot example showing complex timezone normalization.
*   **Structure:**
    ```text
    You are an expert data parsing engine. Your job is to extract events from raw, messy text into strict JSON arrays.
    
    <rules>
    1. Parse all dates into YYYY-MM-DD format.
    2. Wrap your entire output in a single JSON block.
    </rules>
    
    <example>
    Input: "Had to reschedule the 4pm sync to tomorrow at 9am EST due to conflicts."
    Output: { "events": [{ "event": "Rescheduled Sync", "timestamp": "2026-09-24T09:00:00-05:00" }] }
    </example>
    
    <input_data>
    {{RAW_TEXT}}
    </input_data>
    ```

### 🔗 Version 3: Prompt Chaining + Critique & Verification
*   **Technique:** Breaks a complex action into a deterministic **2-stage prompt chain**.
    *   *Chain Link 1 (Extraction):* Generates the draft JSON array using structural delimiters.
    *   *Chain Link 2 (Critique & Verify):* Feeds the generated JSON back to the model alongside the original input, forcing it to cross-check dates, look for hallucinated timeline entries, and fix missing fields prior to final state delivery.

---

## 📊 Evaluation Matrix (30 Test Cases)

| Test Case ID & Context Summary | Prompt v1 (Basic Zero-Shot) | Prompt v2 (Structured Few-Shot) | Prompt v3 (Chained & Verified) |
| :--- | :---: | :---: | :---: |
| **TC-01: Multi-timezone conversational sync with overlapping flight updates** | Partial (Missing Keys) | Pass | Pass |
| **TC-02: Slack logs discussing system downtime windows and incident response milestones** | Pass | Partial (Missing Keys) | Pass |
| **TC-03: Customer support transcript with chaotic scheduling changes and appointment cancels** | Pass | Partial (Missing Keys) | Pass |
| **TC-04: Project manager braindump with implicit deadlines and relative dates ('next Tue')** | Partial (Missing Keys) | Pass | Pass |
| **TC-05: Medical shift handover report containing highly critical vital check timestamps** | Fail (Invalid JSON) | Pass | Pass |
| **TC-06: Mixed technical/casual standup notes containing hidden task allocations** | Fail (Invalid JSON) | Pass | Pass |
| **TC-07: Legal deposition notes with sequential timestamps but contradictory statements** | Fail (Invalid JSON) | Pass | Pass |
| **TC-08: Disaster response radio transcriptions with fragmented time codes** | Pass | Partial (Missing Keys) | Pass |
| **TC-09: Financial earnings call Q&A with historical and forward-looking quarters** | Partial (Missing Keys) | Pass | Pass |
| **TC-10: Product launch retrospective log with rapid-fire feature patch timelines** | Pass | Pass | Pass |
| **TC-11: IoT device sensor diagnostic logs interleaved with human maintenance text** | Fail (Invalid JSON) | Partial (Missing Keys) | Pass |
| **TC-12: Academic research seminar scheduling thread with multiple time proposals** | Pass | Pass | Pass |
| **TC-13: Real estate negotiation email chain outlining payment schedules** | Pass | Fail (Invalid JSON) | Partial (Missing Keys) |
| **TC-14: Supply chain logistics log with dynamic shipping container ETA updates** | Fail (Invalid JSON) | Pass | Pass |
| **TC-15: Marketing campaign strategy session transcript with loose seasonal milestones** | Fail (Invalid JSON) | Partial (Missing Keys) | Pass |
| **TC-16: HR onboarding itinerary brief containing conditional session times** | Fail (Invalid JSON) | Pass | Pass |
| **TC-17: Software release sprint planning logs with velocity and milestone updates** | Partial (Missing Keys) | Pass | Pass |
| **TC-18: Flight traffic control logs with dense, non-standardized aeronautical times** | Partial (Missing Keys) | Pass | Pass |
| **TC-19: Restaurant shift schedule discussion with chaotic swap requests** | Partial (Missing Keys) | Pass | Pass |
| **TC-20: Live event production script with cue triggers and elapsed time offsets** | Partial (Missing Keys) | Partial (Missing Keys) | Pass |
| **TC-21: Customer onboarding roadmap chat with vague target quarters** | Partial (Missing Keys) | Pass | Pass |
| **TC-22: Sales pipeline review transcript with changing fiscal target periods** | Fail (Invalid JSON) | Pass | Pass |
| **TC-23: IT helpdesk ticket progression history with multiple re-open timestamps** | Partial (Missing Keys) | Pass | Pass |
| **TC-24: Game development build cycle logs with asset cooking timestamp milestones** | Partial (Missing Keys) | Pass | Pass |
| **TC-25: Media editing review log with precise SMPTE timecode marker requests** | Partial (Missing Keys) | Pass | Pass |
| **TC-26: Construction site daily progress audio transcript with weather delays** | Pass | Pass | Pass |
| **TC-27: Crisis management text string with overlapping emergency dispatch times** | Fail (Invalid JSON) | Partial (Missing Keys) | Pass |
| **TC-28: E-commerce flash sale backend scaling logs alongside user traffic spike timeline** | Partial (Missing Keys) | Partial (Missing Keys) | Pass |
| **TC-29: Conference speaker panel schedule thread with speaker timezone conflicts** | Partial (Missing Keys) | Fail (Invalid JSON) | Pass |
| **TC-30: Hardware stress test diagnostic logs interspersed with lab tech notes** | Fail (Invalid JSON) | Pass | Pass |

---

## 📉 Deep Failure Analysis & Learnings

### 1. Structural Breakdown in Naive Prompting (v1)
*   **The Issue:** v1 suffered significantly from formatting drift. Models frequently wrapped responses in standard conversation filler ("Here is the JSON you requested:") or generated invalid trailing commas, completely crashing downstream automated parsers.
*   **The Fix:** Introducing explicit JSON formatting delimiters and specifying root keys inside strict system parameters natively drops conversation drift.

### 2. The Context Attention Trap (v2)
*   **The Issue:** When dealing with chaotic, multi-timezone chat logs (e.g., *TC-01, TC-07*), v2 occasionally missed relative timeframes ("next Tuesday") or assigned events to the wrong calendar dates due to ambiguous conversational grouping.
*   **The Fix:** Using clear XML tag wrappers (`<input_data>`, `<rules>`) allows the model's self-attention layers to distinctly separate instructional logic from user data boundaries.

### 3. The Power of Self-Verification Chains (v3)
*   **The Issue:** None of the models natively catch subtle timeline hallucination gaps on the first pass if the input context window is dense or messy.
*   **The Result:** Moving to a **Chained Pipeline** (Extract $\rightarrow$ Verify $\rightarrow$ Correct) raised accuracy to **96.7%**, transforming erratic text into deterministic code-ready structures.
