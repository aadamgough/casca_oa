from typing import Dict, Any, List, Tuple

class ScoringLlamaService:
    def __init__(self):
        # Weights for different components in final score
        self.weights = {
            "cash_flow": 0.25,
            "expenses": 0.20,
            "income": 0.25,
            "debt_credit": 0.15,
            "financial_health": 0.15
        }

        # Thresholds for flag generation
        self.thresholds = {
            "low_score": 60,  # Score below this raises concerns
            "high_credit_utilization": 0.30,  # Credit utilization above 30%
            "negative_cash_flow": 0,  # Negative cash flow threshold
            "large_expense_ratio": 0.40  # Large expenses vs income ratio
        }

    def calculate_score(self, maverick_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate final score and generate insights from Maverick analysis
        """
        try:
            print("Starting score calculation with analysis:", maverick_analysis)
            
            # Calculate weighted score
            final_score = self._calculate_weighted_score(maverick_analysis)
            print(f"Calculated final score: {final_score}")
            
            # Generate flags
            flags = self._generate_flags(maverick_analysis)
            print(f"Generated flags: {flags}")
            
            # Extract key metrics
            metrics = self._extract_key_metrics(maverick_analysis)
            print(f"Extracted metrics: {metrics}")
            
            result = {
                "final_score": final_score,
                "component_scores": {
                    "cash_flow": maverick_analysis["cash_flow"]["score"],
                    "expenses": maverick_analysis["expenses"]["score"],
                    "income": maverick_analysis["income"]["score"],
                    "debt_credit": maverick_analysis["debt_credit"]["score"],
                    "financial_health": maverick_analysis["financial_health"]["score"]
                },
                "flags": flags,
                "metrics": metrics
            }
            print(f"Final scoring result: {result}")
            return result
            
        except Exception as e:
            print(f"Error in calculate_score: {str(e)}")
            raise Exception(f"Scoring calculation failed: {str(e)}")


    def _calculate_weighted_score(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate weighted final score from component scores
        """
        weighted_sum = sum(
            analysis[component]["score"] * weight
            for component, weight in self.weights.items()
        )
        
        return round(weighted_sum, 2)

    def _generate_flags(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate warning flags based on analysis
        """
        flags = []
        print("Generating flags for analysis:", analysis)

        # Check component scores
        for component, data in analysis.items():
            score = float(data.get("score", 0))  # Convert to float
            print(f"Checking {component} score: {score}")
            if score < self.thresholds["low_score"]:
                flags.append({
                    "type": f"low_{component}_score",
                    "severity": "warning",
                    "message": f"Low {component.replace('_', ' ')} score of {score}"
                })

        # Check cash flow
        try:
            net_flow = float(analysis["cash_flow"]["net_flow"])
            print(f"Checking cash flow: {net_flow}")
            if net_flow < self.thresholds["negative_cash_flow"]:
                flags.append({
                    "type": "negative_cash_flow",
                    "severity": "high",
                    "message": f"Negative cash flow detected: ${net_flow:.2f}"
                })
        except (ValueError, TypeError) as e:
            print(f"Error converting net_flow: {e}")

        # Check credit utilization - handle string or numeric values
        credit_util = analysis["debt_credit"]["credit_utilization"]
        print(f"Raw credit utilization value: {credit_util}")
        
        # Only process if it's a numeric value
        if isinstance(credit_util, (int, float)):
            credit_util_float = float(credit_util)
            print(f"Checking credit utilization: {credit_util_float}")
            if credit_util_float > self.thresholds["high_credit_utilization"]:
                flags.append({
                    "type": "high_credit_utilization",
                    "severity": "high",
                    "message": f"High credit utilization at {credit_util_float*100:.1f}%"
                })
        else:
            print(f"Credit utilization is not numeric: {credit_util}")

        # Check expense patterns
        major_expenses = analysis["expenses"]["major_expenses"]
        print(f"Checking major expenses: {len(major_expenses)} found")
        if major_expenses:
            flags.append({
                "type": "large_expenses",
                "severity": "info",
                "message": f"Large expenses detected: {len(major_expenses)} transactions"
            })

        return flags

    def _extract_key_metrics(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics for final reporting
        """
        try:
            return {
                "cash_flow_summary": {
                    "net_flow": float(analysis["cash_flow"]["net_flow"]),
                    "total_inflow": float(analysis["cash_flow"]["total_inflow"]),
                    "total_outflow": float(analysis["cash_flow"]["total_outflow"])
                },
                "expense_metrics": {
                    "major_expenses_count": len(analysis["expenses"]["major_expenses"]),
                    "recurring_expenses_count": len(analysis["expenses"]["recurring_expenses"])
                },
                "income_stability": {
                    "regular_sources": len(analysis["income"]["regular_sources"]),
                    "irregular_sources": len(analysis["income"]["irregular_sources"])
                },
                "debt_metrics": {
                    "outstanding_debt": analysis["debt_credit"]["outstanding_debt"],
                    "credit_utilization": analysis["debt_credit"]["credit_utilization"]
                },
                "financial_health_indicators": {
                    "indicators_count": len(analysis["financial_health"]["key_indicators"]),
                    "key_findings": [
                        {
                            "category": indicator["category"],
                            "impact": indicator["impact"]
                        }
                        for indicator in analysis["financial_health"]["key_indicators"]
                    ]
                }
            }
        except Exception as e:
            print(f"Error extracting metrics: {e}")
            return {}