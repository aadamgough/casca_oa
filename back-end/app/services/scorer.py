from typing import Dict

class ScoringService:
    def __init__(self):
        self.debug = True

    def log(self, msg: str):
        if self.debug:
            print(f"[Scorer] {msg}")

    def calculate_score(self, llama_analysis: Dict) -> Dict:
        """Calculate a score based on heuristics from LLaMA's analysis summary"""
        try:
            text = llama_analysis.get('summary', '').lower()
            base_score = 50

            POSITIVE_INDICATORS = {
                "regular income": 15,
                "steady income": 15,
                "consistent": 10,
                "recurring deposits": 10,
                "positive": 15,
                "surplus": 10,
                "emergency fund": 10,
                "savings": 10,
                "low debt": 10,
                "no debt": 15,
                "recommended": 10,
                "strong financials": 10,
                "budgeting skills": 5,
                "responsible spending": 5,
            }

            NEGATIVE_INDICATORS = {
                "overdraft": -25,
                "overdrawn": -20,
                "irregular income": -15,
                "irregular": -15,
                "negative": -5,
                "high debt": -20,
                "debt burden": -15,
                "not recommended": -20,
                "risk": -10,
                "unpredictable cash flow": -15,
                "low balance": -10,
                "no savings": -10,
                "financial stress": -10,
            }

            # Apply scoring
            score = base_score

            for phrase, value in POSITIVE_INDICATORS.items():
                if phrase in text:
                    score += value

            for phrase, value in NEGATIVE_INDICATORS.items():
                if phrase in text:
                    score += value  # value is negative

            # Clamp score between 0–100
            final_score = max(0, min(100, score))

            # Decision logic
            if final_score >= 70:
                decision = "APPROVED"
                reason = "Strong financial profile"
            elif final_score >= 50:
                decision = "MORE INFORMATION NEEDED"
                reason = "Mixed indicators present"
            else:
                decision = "DENIED"
                reason = "Significant risk factors"

            return {
                "score": final_score,
                "decision": decision,
                "reason": reason,
                "original_analysis": llama_analysis.get('summary', '')
            }

        except Exception as e:
            self.log(f"Error in scoring: {e}")
            raise