from typing import Dict

class ScoringService:
    def __init__(self):
        self.debug = True

    def log(self, msg: str):
        if self.debug:
            print(f"[Scorer] {msg}")

    def calculate_score(self, llama_analysis: Dict) -> Dict:
        """Calculate a simple score based on Llama's initial analysis"""
        try:
            text = llama_analysis.get('summary', '').lower()
            score = 50  # Base score

            # Positive indicators (+10 each)
            if "regular income" in text or "steady income" in text:
                score += 10
            if "savings" in text or "emergency fund" in text:
                score += 10
            if "positive cash flow" in text or "surplus" in text:
                score += 10
            if "low debt" in text or "no debt" in text:
                score += 10
            if "recommended" in text:
                score += 10

            # Negative indicators (-15 each)
            if "overdraft" in text:
                score -= 15
            if "irregular income" in text:
                score -= 15
            if "high debt" in text:
                score -= 15
            if "not recommended" in text:
                score -= 15
            if "risk" in text:
                score -= 15

            # Ensure score stays within 0-100
            final_score = max(0, min(100, score))

            # Get decision based on score
            if final_score >= 70:
                decision = "APPROVED"
                reason = "Strong financial profile"
            elif final_score >= 50:
                decision = "MORE_INFORMATION_NEEDED"
                reason = "Mixed indicators present"
            else:
                decision = "DENIED"
                reason = "Significant risk factors"

            return {
                "score": final_score,
                "decision": decision,
                "reason": reason,
                "original_analysis": llama_analysis['summary']
            }

        except Exception as e:
            self.log(f"Error in scoring: {e}")
            raise