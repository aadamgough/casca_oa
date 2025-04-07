import os
from typing import List, Dict
from ..models.transaction import Transaction
import requests
from datetime import datetime
from decimal import Decimal

class LlamaClassifier:
    def __init__(self):
        self.api_key = os.getenv("LLAMA_API_KEY")
        self.api_url = "https://api.llama-api.com/chat/completions"
        self.debug = True

    def log(self, message: str):
        """Debug logging"""
        if self.debug:
            print(f"DEBUG LlamaClassifier: {message}")

    def create_analysis_prompt(self, transactions: List[Transaction]) -> str:
        """Create a structured prompt for the Llama model"""
        
        # Convert transactions to a readable format
        transaction_text = "\n".join([
            f"Date: {t.date}, Description: {t.description}, "
            f"Amount: {t.amount}, Category: {t.category}"
            for t in transactions
        ])

        prompt = f"""As an expert financial analyst, analyze these bank transactions and assess loan worthiness. Please
        note, the data is in a less than ideal format. Some labels are missing, and the transactions might not be
        as clear as they could be. Use your best judgement to determine, for example, if the transaction is a credit or debit
        based on descriptions or categories.

Focus on these key aspects:

Transaction Data:
{transaction_text}

Please analyze:
1. Income Stability: Identify regular income patterns and stability
2. Spending Patterns: Evaluate major expenses and their nature (essential vs. discretionary)
3. Cash Flow: Calculate average monthly inflow vs. outflow
4. Risk Factors: Flag any concerning patterns (more debits than credits, small ending balance, etc.)
5. Business Indicators: Identify any business-related transactions

Provide a structured analysis with:
- Key financial metrics
- Risk assessment (Low/Medium/High)
- Loan recommendation (Recommended/Neutral/Not Recommended)
- Brief justification

Keep the analysis concise and data-driven."""

        return prompt

    async def analyze_transactions(self, transactions: List[Transaction]) -> Dict:
        """Send transactions to Llama API and get analysis"""
        
        self.log(f"Analyzing {len(transactions)} transactions")
        
        try:
            prompt = self.create_analysis_prompt(transactions)
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama3-70b",  # Update with your model
                "messages": [
                    {"role": "system", "content": "You are a precise and thorough financial analyst."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
                
            analysis = response.json()
            
            # Extract and structure the analysis
            structured_analysis = {
                "summary": analysis["choices"][0]["message"]["content"],
                "timestamp": datetime.now().isoformat(),
                "transaction_count": len(transactions),
                "metrics": self.extract_metrics(transactions)
            }
            
            return structured_analysis
            
        except Exception as e:
            self.log(f"Error in analysis: {str(e)}")
            raise
    
    # Used in the last step of the analysis
    async def get_final_analysis(self, scoring_result: Dict) -> Dict:
        """Get final analysis using the structured prompt"""
        try:
            prompt = f"""As a financial analyst, provide a final assessment of this loan application. Structure
            your response in the following format:

            Loan Analysis Results:
            - Score: {scoring_result['score']}/100
            - Decision: {scoring_result['decision']}
            - Primary Reason: {scoring_result['reason']}

            Initial Analysis:
            {scoring_result['original_analysis']}

            Please provide:
            1. A clear, 2-3 sentence final recommendation
            2. The most important factors that led to this decision
            3. If more information is needed, specify exactly what would be most helpful"""
            self.log("Getting final analysis from Llama")
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama3-70b",  # Update with your model
                "messages": [
                    {"role": "system", "content": "You are a precise and thorough financial analyst."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
                
            analysis = response.json()
            
            return {
                "summary": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.log(f"Error getting final analysis: {e}")
            raise

    def extract_metrics(self, transactions: List[Transaction]) -> Dict:
        """Calculate basic financial metrics from transactions"""
        try:
            total_inflow = sum(t.amount for t in transactions if t.amount > 0)
            total_outflow = abs(sum(t.amount for t in transactions if t.amount < 0))
            
            return {
                "total_transactions": len(transactions),
                "total_inflow": float(total_inflow),
                "total_outflow": float(total_outflow),
                "net_flow": float(total_inflow - total_outflow),
                "average_transaction": float(sum(abs(t.amount) for t in transactions) / len(transactions)) if transactions else 0
            }
        except Exception as e:
            self.log(f"Error calculating metrics: {str(e)}")
            return {}

    def format_response(self, analysis: Dict) -> Dict:
        """Format the analysis response for the API"""
        return {
            "analysis": {
                "summary": analysis.get("summary", "Analysis unavailable"),
                "metrics": analysis.get("metrics", {}),
                "timestamp": analysis.get("timestamp"),
                "status": "completed"
            }
        }