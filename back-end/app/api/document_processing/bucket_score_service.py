from typing import Dict, Any

class BucketScoreService:
    @staticmethod
    def calculate_bucket_scores(maverick_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate scores for each bucket based on Maverick's analysis"""
        return {
            "cash_flow": BucketScoreService.score_cash_flow(maverick_analysis["cash_flow"]),
            "expenses": BucketScoreService.score_expenses(maverick_analysis["expenses"]),
            "income": BucketScoreService.score_income(maverick_analysis["income"]),
            "debt_credit": BucketScoreService.score_debt_credit(maverick_analysis["debt_credit"]),
            "financial_health": BucketScoreService.score_financial_health(maverick_analysis["financial_health"])
        }

    @staticmethod
    def score_cash_flow(data: Dict[str, Any]) -> float:
        """Score cash flow based on numerical metrics and summary analysis"""
        # Numerical analysis (60% of score)
        inflow = data.get("total_inflow", 0)
        outflow = data.get("total_outflow", 0)
        net_flow = data.get("net_flow", inflow - outflow)
        beginning_balance = data.get("beginning_balance", 0)
        ending_balance = data.get("ending_balance", 0)
        
        # Critical balance checks (these override other calculations)
        if beginning_balance < 500 or ending_balance < 500:
            numerical_score = 30  # Critical low balance
        elif net_flow > 0 and (ending_balance < net_flow * 0.2 or beginning_balance < net_flow * 0.2):
            numerical_score = 35  # Balance is too small compared to cash flow
        else:
            if inflow == 0:
                numerical_score = 50 if outflow == 0 else 30
            else:
                net_ratio = net_flow / inflow
                
                # Critical threshold checks
                if net_flow < -1000:  # Significant negative cash flow
                    numerical_score = 20
                elif net_ratio < -0.2:  # Losing more than 20% of income
                    numerical_score = 30
                elif net_ratio < -0.1:  # Losing 10-20% of income
                    numerical_score = 40
                elif net_ratio < 0:    # Any negative cash flow
                    numerical_score = max(20, 50 + 50 * net_ratio)
                # Positive cash flow checks with balance consideration
                elif net_ratio < 0.05:  # Very thin margins (<5%)
                    numerical_score = 55
                elif net_ratio < 0.1:   # Modest margins (5-10%)
                    numerical_score = 65
                elif net_ratio < 0.2:   # Healthy margins (10-20%)
                    numerical_score = 75
                elif net_ratio < 0.3:   # Strong margins (20-30%)
                    numerical_score = 85
                else:                   # Excellent margins (>30%)
                    numerical_score = 85
                
                # Balance trend adjustment
                if ending_balance < beginning_balance * 0.8:
                    numerical_score = max(30, numerical_score - 20)  # Significant balance decrease
                elif ending_balance > beginning_balance * 1.2:
                    numerical_score = min(95, numerical_score + 10)  # Significant balance increase

        # Summary text analysis (40% of score)
        summary = data.get("summary", "").lower()
        text_score = 65  # Default neutral score

        # Positive indicators
        positive_keywords = {
            'consistent': 3,
            'stable': 2,
            'healthy': 3,
            'strong': 2,
            'positive': 3,
            'surplus': 5,
            'savings': 4,
            'well-managed': 4
        }

        # Negative indicators
        negative_keywords = {
            'inconsistent': -3,
            'unstable': -3,
            'concerning': -4,
            'negative': -3,
            'deficit': -5,
            'irregular': -2,
            'volatile': -3,
            'overdrawn': -5
        }

        # Calculate text score adjustments
        score_adjustment = 0
        for keyword, weight in positive_keywords.items():
            if keyword in summary:
                score_adjustment += weight
        
        for keyword, weight in negative_keywords.items():
            if keyword in summary:
                score_adjustment += weight

        text_score = max(20, min(100, text_score + score_adjustment * 2))

        # Combine scores (60% numerical, 40% text analysis)
        final_score = (numerical_score * 0.6) + (text_score * 0.4)
        
        return round(min(100, max(0, final_score)))

    @staticmethod
    def score_expenses(data: Dict[str, Any]) -> float:
        """Score expenses based on patterns, amounts, and summary analysis"""
        # Numerical analysis (70% of score)
        major = data.get("major_expenses", [])
        recurring = data.get("recurring_expenses", [])
        major_total = sum(expense["amount"] for expense in major)
        recurring_total = sum(expense["amount"] for expense in recurring)
        total = major_total + recurring_total

        if total == 0:
            numerical_score = 50
        elif len(major) > 3 and len(recurring) > 8:
            numerical_score = 45  # Too many expenses
        elif major_total > recurring_total * 2:
            numerical_score = 55  # Large irregular expenses
        elif len(recurring) > 8:
            numerical_score = 60  # Many commitments
        elif len(recurring) > 5:
            numerical_score = 70  # Moderate commitments
        else:
            numerical_score = 70  # Well-managed

        # Summary text analysis (30% of score)
        summary = data.get("summary", "").lower()
        text_score = 65
        
        positive_keywords = {
            'manageable': 4,
            'controlled': 3,
            'reasonable': 3,
            'within budget': 5,
            'reduced': 4,
            'minimal': 4,
            'essential': 3
        }
        
        negative_keywords = {
            'high': -3,
            'excessive': -5,
            'concerning': -4,
            'irregular': -3,
            'uncontrolled': -5,
            'overspending': -5
        }

        score_adjustment = sum(weight for word, weight in positive_keywords.items() if word in summary) + \
                        sum(weight for word, weight in negative_keywords.items() if word in summary)
        
        text_score = max(20, min(100, text_score + score_adjustment * 2))
        
        return round(min(100, max(0, numerical_score * 0.7 + text_score * 0.3)))

    @staticmethod
    def score_income(data: Dict[str, Any]) -> float:
        """Score income based on stability, diversity, and summary analysis"""
        # Numerical analysis (65% of score)
        regular = data.get("regular_sources", [])
        irregular = data.get("irregular_sources", [])
        regular_total = sum(src["total_amount"] for src in regular)
        irregular_total = sum(src["amount"] for src in irregular)
        
        if regular_total + irregular_total == 0:
            numerical_score = 50
        elif len(regular) >= 2 and irregular_total < 0.2 * regular_total:
            numerical_score = 90  # Multiple stable sources
        elif len(regular) == 1 and irregular_total < 0.3 * regular_total:
            numerical_score = 80  # Single stable source
        elif irregular_total > regular_total:
            numerical_score = 50  # Mostly irregular
        else:
            numerical_score = 65  # Mixed sources

        # Summary text analysis (35% of score)
        summary = data.get("summary", "").lower()
        text_score = 65
        
        positive_keywords = {
            'stable': 5,
            'reliable': 4,
            'consistent': 4,
            'multiple': 5,
            'growing': 5,
            'diversified': 3,
            'steady': 4
        }
        
        negative_keywords = {
            'institution': -3,
            'bank': -3,
            'unsure': -3,
            'unstable': -4,
            'irregular': -3,
            'declining': -5,
            'unreliable': -4,
            'variable': -3
        }

        score_adjustment = sum(weight for word, weight in positive_keywords.items() if word in summary) + \
                        sum(weight for word, weight in negative_keywords.items() if word in summary)
        
        text_score = max(20, min(100, text_score + score_adjustment * 2))
        
        return round(min(100, max(0, numerical_score * 0.65 + text_score * 0.35)))

    @staticmethod
    def score_debt_credit(data: Dict[str, Any]) -> float:
        """Score debt and credit based on utilization, amounts, and summary analysis"""
        # Numerical analysis (75% of score)
        try:
            utilization = float(data.get("credit_utilization", "0%").strip('%')) / 100
        except (ValueError, TypeError):
            utilization = 0.0

        if utilization > 0.7:
            numerical_score = 30
        elif utilization > 0.5:
            numerical_score = 45
        elif utilization > 0.3:
            numerical_score = 60
        elif utilization > 0.1:
            numerical_score = 75
        else:
            numerical_score = 85

        # Summary text analysis (25% of score)
        summary = data.get("summary", "").lower()
        text_score = 65
        
        positive_keywords = {
            'manageable': 4,
            'low utilization': 5,
            'paying off': 4,
            'decreasing': 3,
            'minimal': 4,
            'good standing': 5
        }
        
        negative_keywords = {
            'high balance': -4,
            'missed payment': -5,
            'increasing': -3,
            'maxed out': -5,
            'overleveraged': -4
        }

        score_adjustment = sum(weight for word, weight in positive_keywords.items() if word in summary) + \
                        sum(weight for word, weight in negative_keywords.items() if word in summary)
        
        text_score = max(20, min(100, text_score + score_adjustment * 2))
        
        return round(min(100, max(0, numerical_score * 0.75 + text_score * 0.25)))
    
    @staticmethod
    def score_financial_health(data: Dict[str, Any]) -> float:
        """Score financial health based on key indicators and summary analysis"""
        # Numerical analysis (70% of score)
        indicators = data.get("key_indicators", [])
        
        positive_count = sum(1 for i in indicators if i["impact"].lower() == "positive")
        negative_count = sum(1 for i in indicators if i["impact"].lower() == "negative")
        savings_count = sum(1 for i in indicators if "saving" in i["category"].lower())
        
        # Calculate ratio of positive to total indicators
        total_indicators = len(indicators) if indicators else 1
        positive_ratio = positive_count / total_indicators

        # Calculate numerical score
        if negative_count > positive_count * 2:
            numerical_score = 40  # Significantly more negatives
        elif negative_count > positive_count:
            numerical_score = 55  # More negatives than positives
        elif savings_count >= 2 and positive_ratio > 0.6:
            numerical_score = 90  # Multiple savings indicators and mostly positive
        elif positive_ratio > 0.7:
            numerical_score = 85  # Strongly positive indicators
        elif positive_ratio > 0.5:
            numerical_score = 75  # More positive than negative
        else:
            numerical_score = 65  # Balanced indicators

        # Summary text analysis (30% of score)
        summary = data.get("summary", "").lower()
        text_score = 65

        positive_keywords = {
            'improving': 4,
            'stable': 3,
            'strong': 4,
            'savings': 5,
            'responsible': 4,
            'disciplined': 4,
            'well-managed': 5,
            'emergency fund': 5
        }
        
        negative_keywords = {
            'struggling': -4,
            'concerning': -3,
            'unstable': -4,
            'risky': -4,
            'vulnerable': -3,
            'no savings': -5,
            'overextended': -5,
            'deteriorating': -4
        }

        score_adjustment = sum(weight for word, weight in positive_keywords.items() if word in summary) + \
                        sum(weight for word, weight in negative_keywords.items() if word in summary)
        
        text_score = max(20, min(100, text_score + score_adjustment * 2))
        
        # Combine scores (70% numerical, 30% text analysis)
        final_score = (numerical_score * 0.7) + (text_score * 0.3)
        
        return round(min(100, max(0, final_score)))