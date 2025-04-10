from typing import Dict, Any, List, Tuple
from .bucket_score_service import BucketScoreService

class ScoringLlamaService:
    def __init__(self):
        # Weights for different components in final score
        self.weights = {
            "cash_flow": 0.4,
            "expenses": 0.2,
            "income": 0.3,
            "debt_credit": 0.1,
        }

        # Thresholds for flag generation
        self.thresholds = {
            "low_score": 60,  # Score below this raises concerns
            "high_inferred_liability_types": 0.30,  # Credit utilization above 30%
            "negative_cash_flow": 0,  # Negative cash flow threshold
            "large_expense_ratio": 0.40  # Large expenses vs income ratio
        }

        self.bucket_score_service = BucketScoreService()

    def calculate_score(self, maverick_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate final score and generate insights from Maverick analysis
        """
        try:
            print("Starting score calculation with analysis:", maverick_analysis)
            
            # Get component scores from bucket service
            component_scores = self.bucket_score_service.calculate_bucket_scores(maverick_analysis)
            
            # Calculate weighted score using bucket service scores
            final_score = sum(
                score * self.weights[component]
                for component, score in component_scores.items()
            )
            
            # Generate flags
            flags = self._generate_flags(maverick_analysis, component_scores)
            
            # Extract key metrics
            metrics = self._extract_key_metrics(maverick_analysis)
            
            return {
                "final_score": round(final_score, 2),
                "component_scores": {k: float(v) for k, v in component_scores.items()},  # Ensure all scores are floats
                "flags": flags,
                "metrics": metrics
            }
                
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

    def _generate_flags(self, analysis: Dict[str, Any], component_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generate warning flags based on analysis
        """
        flags = []

        # Check component scores from bucket service
        for component, score in component_scores.items():
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
        inferred_liability_types = analysis["debt_credit"]["inferred_liability_types"]
        print(f"Raw inferred liability types value: {inferred_liability_types}")
        
        # Only process if it's a numeric value
        if isinstance(inferred_liability_types, (int, float)):
            inferred_liability_types_float = float(inferred_liability_types)
            print(f"Checking inferred liability types: {inferred_liability_types_float}")
            if inferred_liability_types_float > self.thresholds["high_inferred_liability_types"]:
                flags.append({
                    "type": "high_inferred_liability_types",
                    "severity": "high",
                    "message": f"High inferred liability types at {inferred_liability_types_float*100:.1f}%"
                })
        else:
            print(f"Inferred liability types is not numeric: {inferred_liability_types}")

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
                    "total_outflow": float(analysis["cash_flow"]["total_outflow"]),
                    "beginning_balance": float(analysis["cash_flow"]["beginning_balance"]),
                    "ending_balance": float(analysis["cash_flow"]["ending_balance"])
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
                    "recurring_debt_payments": analysis["debt_credit"]["recurring_debt_payments"],
                    "inferred_liability_types": analysis["debt_credit"]["inferred_liability_types"]
                }
            }
        except Exception as e:
            print(f"Error extracting metrics: {e}")
            return {}