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
            numerical_score = 60
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
    def score_income(data: Dict[str, Any]) -> float: #income risk / revenue risk --> weigh this more
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
        """Score debt based on payment patterns and types of liabilities"""
        # Numerical analysis (75% of score)
        recurring_payments = data.get("recurring_debt_payments", [])
        liability_types = data.get("inferred_liability_types", [])
        
        # Calculate total monthly debt payments
        total_debt_payments = sum(payment["amount"] for payment in recurring_payments)
        
        # Initialize base numerical score
        numerical_score = 65  # Default neutral score
        
        # Scoring based on number and types of debt
        num_liabilities = len(liability_types)
        
        if num_liabilities == 0:
            numerical_score = 85  # No detected debt obligations
        elif num_liabilities > 4:
            numerical_score = 45  # Many different types of debt
        else:
            # Adjust score based on types of debt
            has_mortgage = any("mortgage" in liability.lower() for liability in liability_types)
            has_auto = any("auto" in liability.lower() for liability in liability_types)
            
            # Positive adjustments for "good" debt
            if has_mortgage:
                numerical_score += 5  # Mortgage is generally considered good debt
            if has_auto and num_liabilities <= 2:
                numerical_score += 3  # Auto loan alone or with one other debt is okay
                
            
            # Cap the score
            numerical_score = min(90, max(30, numerical_score))

        # Summary text analysis (25% of score)
        summary = data.get("summary", "").lower()
        text_score = 65
        
        positive_keywords = {
            'manageable': 4,
            'consistent payments': 5,
            'paying off': 4,
            'decreasing': 3,
            'minimal': 4,
            'good standing': 5,
            'on time': 5
        }
        
        negative_keywords = {
            'high payments': -4,
            'missed payment': -5,
            'late payment': -4,
            'increasing debt': -3,
            'multiple loans': -3,
            'concerning pattern': -4
        }

        score_adjustment = sum(weight for word, weight in positive_keywords.items() if word in summary) + \
                        sum(weight for word, weight in negative_keywords.items() if word in summary)
        
        text_score = max(20, min(100, text_score + score_adjustment * 2))
        
        # Final weighted score (75% numerical, 25% text analysis)
        final_score = round(min(100, max(0, numerical_score * 0.75 + text_score * 0.25)))
        
        return final_score