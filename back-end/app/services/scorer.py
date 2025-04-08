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
                "consistent paycheck": 10,
                "recurring deposits": 10,
                "positive cash flow": 15,
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
                "high debt": -20,
                "debt burden": -15,
                "not recommended": -20,
                "risk": -10,
                "debit": -15,
                "unpredictable cash flow": -15,
                "low balance": -10,
                "no savings": -10,
                "financial stress": -10,
            }

            score = base_score
            positive_matches = {}
            negative_matches = {}

            for phrase, value in POSITIVE_INDICATORS.items():
                count = text.count(phrase)
                if count > 0:
                    score += value * count
                    positive_matches[phrase] = {"count": count, "weight": value}

            for phrase, value in NEGATIVE_INDICATORS.items():
                count = text.count(phrase)
                if count > 0:
                    score += value * count  # value is negative
                    negative_matches[phrase] = {"count": count, "weight": value}

            final_score = max(0, min(100, score))

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
                "match_details": {
                    "positive_indicators": positive_matches,
                    "negative_indicators": negative_matches
                },
                "original_analysis": llama_analysis.get('summary', '')
            }

        except Exception as e:
            self.log(f"Error in scoring: {e}")
            raise