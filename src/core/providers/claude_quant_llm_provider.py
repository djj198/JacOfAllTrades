"""
ClaudeQuantLLMProvider: Anthropic Claude backend for JOAT ACP Agent.
To use Claude: set ANTHROPIC_API_KEY or LLM_API_KEY in your environment.
"""
import os
import json
import logging
import re
from typing import Dict, Any
from src.interfaces.protocols import QuantLLMProtocol
from src.core.providers.stub_quant_llm_provider import StubQuantLLMProvider

# Try to import anthropic, but don't crash if not installed (though instructions say to pip install it)
try:
    import anthropic
except ImportError:
    anthropic = None

logger = logging.getLogger(__name__)

class ClaudeQuantLLMProvider(QuantLLMProtocol):
    """
    Expert Python refactoring: Claude implementation of QuantLLMProtocol.
    Provides rich, LLM-driven insights based on the user's real portfolio.
    """
    def __init__(self, portfolio_context: Dict[str, Any] | None = None, api_key: str | None = None):
        self.portfolio_context = portfolio_context or {}
        self.api_key = (
            api_key
            or os.getenv("ANTHROPIC_API_KEY")
            or os.getenv("LLM_API_KEY")
        )
        self.stub_fallback = StubQuantLLMProvider(portfolio_context=portfolio_context)
        
        if self.api_key and anthropic:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            if not self.api_key:
                logger.info("No ANTHROPIC_API_KEY found, falling back to stub.")
            if not anthropic:
                logger.warning("anthropic SDK not installed, falling back to stub.")

    def generate_schema(self, prompt: str) -> Dict[str, Any]:
        """
        Returns the exact same schema as the stub for consistency.
        """
        return self.stub_fallback.generate_schema(prompt)

    def generate_insight_data(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls Claude to generate rich insight data grounded in the portfolio.
        Falls back to StubQuantLLMProvider on any error or if API key is missing.
        """
        if not self.client:
            return self.stub_fallback.generate_insight_data(prompt, schema)

        try:
            # 1. Prepare portfolio context (capped at 120k chars)
            portfolio_str = json.dumps(self.portfolio_context, indent=2)
            if len(portfolio_str) > 120000:
                logger.warning("Portfolio JSON too large, truncating for Claude.")
                portfolio_str = portfolio_str[:120000] + "\n... [TRUNCATED]"

            # 2. Build system and user messages
            system_prompt = (
                "You are an expert quantitative financial analyst and data visualizer. "
                "Your task is to analyze the user's portfolio and provide a high-quality visualization sink in JSON format.\n"
                "The JSON must match this schema:\n"
                f"{json.dumps(schema, indent=2)}\n\n"
                "Structure details:\n"
                "- Node: { node_id: string, schema: {type: string}, data: object }\n"
                "- Edge: { source_id: string, target_id: string, reasoning: string }\n\n"
                "Constraints:\n"
                "- Return ONLY valid JSON.\n"
                "- Ensure all nodes and edges are logically connected.\n"
                "- The 'quant_summary' must be insightful (tech overweight, specific holdings, sector weights, risk notes).\n"
                "- Populate nodes and edges with meaningful portfolio entities and their relationships.\n"
                "- If specific tickers are mentioned in the prompt, analyze them relative to the portfolio.\n"
                "- The 'rendered_payload' can be empty {}."
            )

            user_prompt = (
                f"User Portfolio JSON:\n{portfolio_str}\n\n"
                f"User Prompt: {prompt}\n\n"
                "Generate the VisualizationSink JSON now."
            )

            # 3. Call Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            content = response.content[0].text

            # 4. Extract JSON (handle ```json blocks)
            json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Fallback to searching for the first '{' and last '}'
                json_match = re.search(r"(\{.*\})", content, re.DOTALL)
                json_str = json_match.group(1) if json_match else content

            result = json.loads(json_str)
            
            # Basic validation: ensure it has the required root keys
            required_keys = ["insight_id", "quant_summary", "nodes", "visualizer_pseudo_prompt"]
            if all(k in result for k in required_keys):
                return result
            else:
                logger.error("Claude returned JSON missing required keys.")
                return self.stub_fallback.generate_insight_data(prompt, schema)

        except Exception as e:
            logger.exception(f"Claude API call failed: {e}. Falling back to stub.")
            return self.stub_fallback.generate_insight_data(prompt, schema)
