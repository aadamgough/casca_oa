from typing import Dict, Any, List
from ...utils.llama_client import LlamaClient

class OutputGenerator:
    def __init__(self):
        self.llama_client = LlamaClient()
        self.score_descriptions = {
            "excellent": (90, 100, "Loan Approved"),
            "good": (72, 89, "Loan Approved"),
            "fair": (60, 71, "Further information needed"),
            "concerning": (0, 59, "Loan Denied")
        }

    async def generate_output(
            self,
            maverick_analysis: Dict[str, Any],
            scoring_result: Dict[str, Any]
        ) -> Dict[str, Any]:
            try:
                print("Starting generate_output with:")
                print("Maverick analysis:", maverick_analysis)
                print("Scoring result:", scoring_result)
                
                context = self._prepare_context(maverick_analysis, scoring_result)
                narrative = await self._generate_narrative(context)
                
                return {
                    "summary": {
                        "overall_score": scoring_result.get("final_score", 50),
                        "health_status": self._get_health_status(scoring_result.get("final_score", 50)),
                        "key_findings": narrative["summary"]["key_findings"],
                    },
                    "detailed_analysis": {
                        "components": self._format_component_analysis(
                            scoring_result["component_scores"],
                            narrative["component_analysis"]
                        ),
                            "narrative": narrative["component_analysis"]
                    },
                    "recommendations": {
                        "flags": scoring_result.get("flags", [])
                    },
                    "metrics": self._format_metrics(scoring_result["metrics"])
                }
                    
            except Exception as e:
                print(f"Error in generate_output: {e}")
                raise

    def _prepare_context(
        self,
        maverick_analysis: Dict[str, Any],
        scoring_result: Dict[str, Any]
    ) -> str:
        """
        Prepare context for LLM narrative generation
        """
        return f"""Analyze this financial data and provide insights in the following JSON format:
    Required JSON Format:
    {{
        "summary": {{
            "overall_health": "Brief 2-3 sentence overview of financial health",
            "key_findings": ["List of 3-4 key findings"]
        }},
        "component_analysis": {{
            "cash_flow": {{
                "summary": "Detailed analysis including starting balance (${maverick_analysis['cash_flow']['beginning_balance']}) and ending balance (${maverick_analysis['cash_flow']['ending_balance']}). Must mention if balances < $500. Include specific numbers.",
                "strengths": ["List of strengths"],
                "concerns": ["List of concerns"]
            }},
            "debt_credit": {{
                "summary": "Analysis including inferred liability types ({scoring_result['metrics']['debt_metrics']['inferred_liability_types']}), total recurring debt payments, and comparison to healthy ranges. Explain score of {scoring_result['component_scores']['debt_credit']}",
                "strengths": ["List of strengths"],
                "concerns": ["List of concerns"]
            }},
            "expenses": {{
                "summary": "Analysis of expense patterns and ratios",
                "strengths": ["List of strengths"],
                "concerns": ["List of concerns"]
            }},
            "income": {{
                "summary": "Analysis of income stability and sources",
                "strengths": ["List of strengths"],
                "concerns": ["List of concerns"]
            }},
        }},
        "recommendations": {{
            "flags": ["List of flags"]
        }}
    }}

Overall Score: {scoring_result['final_score']}

Component Scores:
{self._format_scores_for_prompt(scoring_result['component_scores'])}

Key Metrics:
{self._format_metrics_for_prompt(scoring_result['metrics'])}

Flags:
{self._format_flags_for_prompt(scoring_result['flags'])}

Here are some additional details for context in the summary part of each component:
Cash Flow:
    - Explicitly mention starting balance and ending balance from ${maverick_analysis['cash_flow']['beginning_balance']} and ${maverick_analysis['cash_flow']['ending_balance']}
    - If balances are below $500, highlight this as a critical concern
    - Compare inflow vs outflow and discuss the trend
    - Include specific numbers to support the analysis

Debt Credit:
    - Include the inferred liability types
    - Compare these numbers to typical healthy ranges
    - Explain why the score is high or low based on these metrics

Expenses:
    - Mention total number of major expenses (${scoring_result['metrics']['expense_metrics']['major_expenses_count']})
    - Discuss recurring expenses pattern (${scoring_result['metrics']['expense_metrics']['recurring_expenses_count']})
    - Compare expense ratios to income
    - Highlight any unusual spending patterns or large expenses
    - Include specific numbers and percentages

Income:
    - Analyze regular income sources (${scoring_result['metrics']['income_stability']['regular_sources']})
    - Discuss irregular income patterns (${scoring_result['metrics']['income_stability']['irregular_sources']})
    - Comment on income stability and diversity
    - Include specific income amounts and frequency
    - Compare income levels to expenses and debt obligations
"""

    async def _generate_narrative(self, context: str) -> Dict[str, Any]:
        """
        Generate narrative analysis using LLM
        """
        try:
            print("Sending context to LLM:", context)
            response = await self.llama_client.get_maverick_completion(context)
            print("Raw LLM response:", response)
            
            # Parse JSON if it's a string
            if isinstance(response, str):
                import json
                # Find JSON content between triple backticks if present
                if "```json" in response:
                    start = response.find("```json") + 7
                    end = response.find("```", start)
                    json_str = response[start:end].strip()
                else:
                    json_str = response
                response = json.loads(json_str)
                
            print("Parsed narrative:", response)
            return response
        except Exception as e:
            print(f"Error in _generate_narrative: {e}")
            raise

    def _get_health_status(self, score: float) -> str:
        """
        Get health status description based on score
        """
        for status, (min_score, max_score, description) in self.score_descriptions.items():
            if min_score <= score <= max_score:
                return description
        return "undefined status"

    def _format_component_analysis(
        self,
        component_scores: Dict[str, float],
        component_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format detailed component analysis using Maverick's summaries and our refined scores
        """
        formatted_analysis = {}
        for component, score in component_scores.items():
            formatted_analysis[component] = {
                "score": score,
                "status": self._get_health_status(score),
                "summary": component_analysis[component]["summary"],
                "strengths": component_analysis[component]["strengths"],
                "concerns": component_analysis[component]["concerns"],
                "details": self._extract_component_details(
                    component,
                    component_analysis[component]
                )
            }
        return formatted_analysis

    def _extract_component_details(
        self,
        component: str,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract relevant details for each component
        """
        if component == "cash_flow":
            return {
                "net_flow": analysis.get("net_flow", 0),
                "total_inflow": analysis.get("total_inflow", 0),
                "total_outflow": analysis.get("total_outflow", 0),
                "beginning_balance": analysis.get("beginning_balance", 0),
                "ending_balance": analysis.get("ending_balance", 0)
            }
        elif component == "expenses":
            return {
                "major_expenses": analysis.get("major_expenses", []),
                "recurring_expenses": analysis.get("recurring_expenses", [])
            }
        # Add similar logic for other components
        return {}

    def _format_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Format metrics for display"""
        try:
            return {
                "cash_flow": {
                    "net_monthly_flow": metrics["cash_flow_summary"]["net_flow"],
                    "income": metrics["cash_flow_summary"]["total_inflow"],
                    "expenses": metrics["cash_flow_summary"]["total_outflow"],
                    "beginning_balance": metrics["cash_flow_summary"]["beginning_balance"],
                    "ending_balance": metrics["cash_flow_summary"]["ending_balance"]
                },
                "expense_breakdown": {
                    "major_expenses": metrics["expense_metrics"]["major_expenses_count"],
                    "recurring_expenses": metrics["expense_metrics"]["recurring_expenses_count"]
                },
                "income_sources": {
                    "regular": metrics["income_stability"]["regular_sources"],
                    "irregular": metrics["income_stability"]["irregular_sources"]
                },
                "debt_and_savings": {
                    "inferred_liability_types": metrics["debt_metrics"]["inferred_liability_types"],
                    "recurring_debt_payments": metrics["debt_metrics"]["recurring_debt_payments"],                }
            }
        except Exception as e:
            print(f"Error formatting metrics: {e}")
            raise Exception(f"Failed to format metrics: {str(e)}")

    def _format_scores_for_prompt(self, scores: Dict[str, float]) -> str:
        """
        Format scores for LLM prompt
        """
        return "\n".join([
            f"- {component.replace('_', ' ').title()}: {score}/100"
            for component, score in scores.items()
        ])

    def _format_metrics_for_prompt(self, metrics: Dict[str, Any]) -> str:
        """
        Format metrics for LLM prompt
        """
        return "\n".join([
            f"- {key.replace('_', ' ').title()}: {value}"
            for key, value in metrics.items()
        ])

    def _format_flags_for_prompt(self, flags: List[Dict[str, Any]]) -> str:
        """
        Format flags for LLM prompt
        """
        return "\n".join([
            f"- {flag['severity'].upper()}: {flag['message']}"
            for flag in flags
        ])
    
    