# backend/test_orchestrator.py
from backend.services.ai_orchestrator import run_chat

questions = [
    "Which titles performed best in 2025?",
    "Why is Stellar Run trending?",
    "Which city had the strongest engagement last month?"
]

for q in questions:
    print(f"\n{'─'*60}")
    print(f"Q: {q}")
    result = run_chat(q)
    print(f"\nA: {result['answer']}")
    print(f"Sources: {result['sources']}")
    print(f"Tools called: {len(result['tool_calls'])}")
    print(f"Duration: {result['duration_ms']}ms")