"""
CineVerse — AI Orchestrator (Grok / xAI)
Uses OpenAI-compatible SDK since Grok exposes an OpenAI-compatible endpoint.

Flow:
  1. User question → messages + tool definitions
  2. Grok decides which tools to call
  3. Backend executes each tool call
  4. Results fed back → Grok synthesizes final answer
  5. Return answer + full trace
"""
from __future__ import annotations
import os
import json
import logging
import re
import time
from typing import Any


from openai import OpenAI
from dotenv import load_dotenv

from backend.tools.sql_tool import query_database
from backend.tools.pdf_tool import search_documents
from backend.tools.csv_tool import analyze_csv

load_dotenv()
log = logging.getLogger(__name__)

# ── Client — Grok via OpenAI-compatible endpoint ──────────────
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
MODEL = "llama-3.1-8b-instant"   # or "llama3-groq-8b-8192-tool-use-preview" for faster/cheaper

MAX_TOOL_ROUNDS = 4

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": (
                "Run a SELECT query against the CineVerse SQL database. "
                "Use for structured data: movie revenue, ratings, watch activity, "
                "viewer demographics, reviews, and marketing spend. "
                "Available tables/views: movies, viewers, watch_activity, reviews, "
                "marketing_spend, regional_performance, vw_movie_performance, "
                "vw_city_engagement, vw_marketing_performance, vw_genre_summary."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": (
                            "A valid SELECT statement. Prefer views (vw_*) for complex joins. "
                            "Example: SELECT title, revenue_inr, rating FROM vw_movie_performance "
                            "WHERE release_year = 2025 ORDER BY revenue_inr DESC LIMIT 10"
                        ),
                    }
                },
                "required": ["sql_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Semantic search over CineVerse's internal PDF documents. "
                "Use for qualitative context: executive reports, campaign summaries, "
                "content strategy, policy guidelines, and audience behavior analysis. "
                "Best combined with query_database for multi-source answers."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Natural language search query. Be specific. "
                            "Example: 'Stellar Run trending social media campaign'"
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of document chunks to return. Default 3, max 5.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_csv",
            "description": (
                "Run filtered aggregations on CineVerse CSV files. "
                "Use for regional engagement, city-level breakdowns, and "
                "cross-file aggregations. "
                "Available files: movies | viewers | watch_activity | "
                "reviews | marketing_spend | regional_performance."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "File key — one of the approved file names above.",
                    },
                    "filters": {
                        "type": "object",
                        "description": "Column equality filters. Example: {\"genre\": \"Comedy\"}",
                    },
                    "aggregation": {
                        "type": "string",
                        "description": "One of: count | sum | avg | min | max | list",
                    },
                    "column": {
                        "type": "string",
                        "description": "Column to aggregate on.",
                    },
                    "group_by": {
                        "type": "string",
                        "description": "Optional column to group results by.",
                    },
                },
                "required": ["file"],
            },
        },
    },
]


#  System prompt 
SYSTEM_PROMPT = """You are the CineVerse Analytics Assistant — an internal AI tool for 
CineVerse Entertainment's leadership and analytics teams.

You answer business questions about Bollywood film performance, audience engagement, 
marketing effectiveness, and regional trends by calling the tools available to you.

Your rules:
1. ALWAYS use tools to ground your answers in real data. Never fabricate numbers.
2. Use MULTIPLE tools when a question needs it — combine SQL data with PDF context.
3. After collecting tool results, synthesize a clear, concise business answer.
4. Always cite your sources — mention which tool/data each insight came from.
5. If a tool returns no results, say so honestly. Do not guess.
6. Monetary values are in INR. Engagement scores are out of 10.

End every answer with: "Sources used: ..." listing which tools were called.
"""


def _execute_tool(tool_name: str, tool_input: dict) -> Any:
    """Route a tool call to the correct backend function."""
    log.info("[orchestrator] Executing: %s | input: %s", tool_name, tool_input)

    if tool_name == "query_database":
        return query_database(**tool_input)
    if tool_name == "search_documents":
        return search_documents(**tool_input)
    if tool_name == "analyze_csv":
        return analyze_csv(**tool_input)

    return {"success": False, "error": f"Unknown tool: {tool_name}"}

# main entery point
def run_chat(
    user_message: str,
    conversation_history: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Main entry point. Called by the FastAPI /chat endpoint.

    Args:
        user_message:         The user's question.
        conversation_history: Prior turns for multi-turn chat support.

    Returns:
        {
            "answer":      str,
            "tool_calls":  list[dict],
            "sources":     list[str],
            "model":       str,
            "duration_ms": int
        }
    """
    start = time.time()
    tool_trace: list[dict] = []
    sources_used: set[str] = set()

    # Build message list
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history or [])
    messages.append({"role": "user", "content": user_message})

    log.info("[orchestrator] User: %s", user_message[:100])

    final_answer = "I was unable to complete this request."

    for round_num in range(MAX_TOOL_ROUNDS):
        log.info("[orchestrator] Round %d", round_num + 1)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",   # Grok decides when to call tools
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason
        log.info("[orchestrator] finish_reason: %s", finish_reason)

        if finish_reason == "stop" or not message.tool_calls:
            final_answer = message.content or final_answer
            break

        
        if finish_reason == "tool_calls":
            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_id   = tool_call.id

                # Parse arguments safely
                try:
                    tool_input = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    log.error("[orchestrator] Bad tool arguments: %s", e)
                    tool_input = {}

                # Run the tool
                result = _execute_tool(tool_name, tool_input)

                # Record in trace
                tool_trace.append({
                    "round":       round_num + 1,
                    "tool":        tool_name,
                    "input":       tool_input,
                    "output":      result,
                    "tool_call_id": tool_id,
                })
                sources_used.add(_source_label(tool_name, tool_input, result))

                # Feed result back — OpenAI format uses role: "tool"
                messages.append({
                    "role":         "tool",
                    "tool_call_id": tool_id,
                    "name":         tool_name,
                    "content":      json.dumps(result, ensure_ascii=False),
                })

            continue   # next round — let Grok synthesize or call more tools

    else:
        final_answer = (
            "I reached the maximum number of tool rounds without completing the analysis. "
            "Please try a more specific question."
        )

    duration_ms = int((time.time() - start) * 1000)
    log.info("[orchestrator] Done in %dms | tools_called=%d", duration_ms, len(tool_trace))

    return {
        "answer":      final_answer,
        "tool_calls":  tool_trace,
        "sources":     sorted(sources_used),
        "model":       MODEL,
        "duration_ms": duration_ms,
    }


# ── Helpers functions
def _source_label(tool_name: str, tool_input: dict, result: dict) -> str:
    if tool_name == "query_database":
        sql = tool_input.get("sql_query", "")
        match = re.search(r"\b(?:from|join)\s+(\w+)", sql, re.IGNORECASE)
        table = match.group(1) if match else "sql"
        return f"SQL ({table})"

    if tool_name == "search_documents":
        if result.get("results"):
            srcs = {r["source"] for r in result["results"]}
            return "PDF (" + ", ".join(sorted(srcs)) + ")"
        return "PDF (no results)"

    if tool_name == "analyze_csv":
        return f"CSV ({tool_input.get('file', 'unknown')})"

    return tool_name