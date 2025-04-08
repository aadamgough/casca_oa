from typing import Dict, Any, List
from ...utils.llama_client import LlamaClient

class OutputGenerator:
    def __init__(self):
        self.llama_client = LlamaClient()
        self.score_descriptions = {
            "excellent": (90, 100, "Excellent: Loan Approved"),
            "good": (75, 89, "Good: Loan Approved"),
            "fair": (60, 74, "Fair: Further information needed"),
            "concerning": (0, 59, "Concering: Loan Denied")
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
                
                # Get summary text (from any key containing 'summary')
                summary_text = ""
                summary_key = next((key for key in narrative.keys() 
                                if 'summary' in key.lower()), None)
                if summary_key and isinstance(narrative[summary_key], dict):
                    summary_dict = narrative[summary_key]
                    if len(summary_dict) >= 2:
                        summary_text = list(summary_dict.values())[1]
                
                # Find analysis component (from any key containing 'analysis')
                analysis_key = next((key for key in narrative.keys() 
                                if 'analysis' in key.lower()), None)
                analysis_content = narrative.get(analysis_key, {}) if analysis_key else {}
                
                # Find recommendations (from any key containing 'recommend')
                recommendations_key = next((key for key in narrative.keys() 
                                        if 'recommend' in key.lower()), None)
                recommendations = narrative.get(recommendations_key, []) if recommendations_key else []
                
                # Find metrics (from any key containing 'metric')
                metrics_key = next((key for key in scoring_result.keys() 
                                if 'metric' in key.lower()), None)
                metrics = scoring_result.get(metrics_key, {}) if metrics_key else {}
                
                # Find scores (from any key containing 'score')
                scores_key = next((key for key in scoring_result.keys() 
                                if 'score' in key.lower() and 'component' in key.lower()), None)
                scores = scoring_result.get(scores_key, {}) if scores_key else {}
                
                return {
                    "summary": {
                        "overall_score": scoring_result.get("final_score", 50),
                        "health_status": self._get_health_status(scoring_result.get("final_score", 50)),
                        "key_findings": str(summary_text)
                    },
                    "detailed_analysis": {
                        "components": self._format_component_analysis(
                            scores,
                            maverick_analysis
                        ),
                        "narrative": analysis_content
                    },
                    "recommendations": {
                        "immediate_actions": recommendations,
                        "flags": scoring_result.get("flags", [])
                    },
                    "metrics": self._format_metrics(metrics),
                    "raw_scores": scores
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
        return f"""Analyze this financial data and provide insights:

Overall Score: {scoring_result['final_score']}

Component Scores:
{self._format_scores_for_prompt(scoring_result['component_scores'])}

Key Metrics:
{self._format_metrics_for_prompt(scoring_result['metrics'])}

Flags:
{self._format_flags_for_prompt(scoring_result['flags'])}

Provide a structured JSON response with:
1. A brief summary of overall financial health
2. Detailed analysis of each component
3. Specific, actionable recommendations based on the flags and metrics
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
        maverick_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format detailed component analysis
        """
        formatted_analysis = {}
        for component, score in component_scores.items():
            formatted_analysis[component] = {
                "score": score,
                "status": self._get_health_status(score),
                "summary": maverick_analysis[component]["summary"],
                "details": self._extract_component_details(
                    component,
                    maverick_analysis[component]
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
                "total_outflow": analysis.get("total_outflow", 0)
            }
        elif component == "expenses":
            return {
                "major_expenses": analysis.get("major_expenses", []),
                "recurring_expenses": analysis.get("recurring_expenses", [])
            }
        # Add similar logic for other components
        return {}

    def _format_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format metrics for display
        """
        try:
            # Handle credit utilization
            credit_util = metrics["debt_metrics"]["credit_utilization"]
            credit_util_str = (
                f"{float(credit_util)*100}%" 
                if isinstance(credit_util, (int, float)) 
                else str(credit_util)
            )
            
            return {
                "cash_flow": {
                    "net_monthly_flow": metrics["cash_flow_summary"]["net_flow"],
                    "income": metrics["cash_flow_summary"]["total_inflow"],
                    "expenses": metrics["cash_flow_summary"]["total_outflow"]
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
                    "credit_utilization": credit_util_str,
                    "outstanding_debt": metrics["debt_metrics"]["outstanding_debt"],
                    "financial_indicators": metrics["financial_health_indicators"]["key_findings"]
                }
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
    
    