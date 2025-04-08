from typing import Dict, Any, List
import json
from ...utils.llama_client import LlamaClient

class MaverickAnalyzer:
    def __init__(self):
        self.llama_client = LlamaClient()

    async def analyze_transactions(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze parsed statement data using Llama-4-Maverick
        """
        try:
            print("Starting analyze_transactions with parsed_data:", parsed_data)
            
            # Extract documents from the dictionary
            documents = parsed_data.get('documents', [])
            if not documents:
                raise Exception("No documents found in parsed data")
                
            # Get the first document
            document = documents[0]
            print("First document:", document)
            
            # Get the content from the document
            document_content = document.get('content', '')
            if not document_content:
                raise Exception("No content found in document")
            
            print("Document content:", document_content[:100])  # Print first 100 chars
                
            # Construct prompt for Maverick
            prompt = self._build_analysis_prompt(document_content)
            print("Built prompt successfully")
            
            # Get analysis from Maverick
            print("Calling Maverick completion...")
            response = await self.llama_client.get_maverick_completion(prompt)
            print("Maverick response:", response)
            
            structured_analysis = self._structure_analysis(response)
            print("Structured analysis successfully")
            return structured_analysis
            
        except Exception as e:
            print(f"Error in analyze_transactions: {str(e)}")
            raise Exception(f"Analysis failed: {str(e)}")


    def _build_analysis_prompt(self, document_content: str) -> str:
        """
        Build a prompt for Maverick to analyze the statement data
        """
        return f"""As a financial analyst, analyze this bank statement data and provide a structured analysis with scores (0-100) for each section. Focus on:

    1. Cash Flow Analysis:
    - Total inflows and outflows
    - Beginning and ending balance
    - Overall cash flow health

    2. Expense Analysis:
    - Major expenses (over $500)
    - Recurring expenses
    - Expense categories breakdown

    3. Income Analysis:
    - Regular income sources
    - Additional/irregular income
    - Income stability

    4. Debt and Credit:
    - Outstanding debt payments
    - Credit utilization
    - Payment patterns

    5. Financial Health Indicators:
    Provide a comprehensive assessment of overall financial health, considering any relevant factors such as:
    - Financial stability and trends
    - Risk factors
    - Areas of strength or concern
    - Any other relevant financial health indicators

    Statement Data:
    {document_content}

    Please provide your analysis in exactly this JSON structure:

    {{
        "Cash Flow Analysis": {{
            "total_inflows": <float>,
            "total_outflows": <float>,
            "beginning_balance": <float>,
            "ending_balance": <float>,
            "cash_flow_health_score": <float>,
            "summary": <string>
        }},
        "Expense Analysis": {{
            "major_expenses": [
                {{
                    "description": <string>,
                    "amount": <float>
                }}
            ],
            "recurring_expenses": [
                {{
                    "description": <string>,
                    "amount": <float>
                }}
            ],
            "expense_analysis_score": <float>,
            "summary": <string>
        }},
        "Income Analysis": {{
            "regular_income_sources": [
                {{
                    "description": <string>,
                    "total_amount": <float>
                }}
            ],
            "additional_irregular_income": [
                {{
                    "description": <string>,
                    "amount": <float>
                }}
            ],
            "income_stability_score": <float>,
            "summary": <string>
        }},
        "Debt and Credit": {{
            "outstanding_debt_payments": [
                {{
                    "description": <string>,
                    "amount": <float>
                }}
            ],
            "credit_utilization": <string>,
            "debt_and_credit_score": <float>,
            "summary": <string>
        }},
        "Financial Health Indicators": {{
            "financial_health_score": <float>,
            "key_indicators": [
                {{
                    "category": <string>,
                    "observation": <string>,
                    "impact": <string>
                }}
            ],
            "summary": <string>
        }}
    }}

    Note: All scores should be between 0-100, and ensure all fields are populated with appropriate values."""

    def _structure_analysis(self, maverick_response: str) -> Dict[str, Any]:
        """
        Structure Maverick's response into a standardized format for scoring
        """
        try:
            if isinstance(maverick_response, str):
                # Extract and clean JSON
                cleaned_json = self._clean_json_string(maverick_response)
                try:
                    analysis = json.loads(cleaned_json)
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    print(f"Problematic JSON: {cleaned_json}")
                    return self._get_fallback_structure()

                return self._build_structured_analysis(analysis)

        except Exception as e:
            print(f"Structure analysis error: {str(e)}")
            return self._get_fallback_structure()

    def _clean_json_string(self, json_str: str) -> str:
        """Clean and extract JSON from response string"""
        import re
        
        # First, try to extract just the JSON portion
        json_match = re.search(r'({[\s\S]*})', json_str)
        if json_match:
            json_str = json_match.group(1)
        
        # Remove any markdown code block markers
        json_str = re.sub(r'```json\s*|\s*```', '', json_str)
        
        def replace_math(match):
            expr = match.group(0)
            try:
                expr = expr.replace(' ', '')
                if '+' in expr:
                    nums = [float(x) for x in expr.split('+')]
                    return str(sum(nums))
                elif '*' in expr:
                    nums = [float(x) for x in expr.split('*')]
                    result = 1
                    for n in nums:
                        result *= n
                    return str(result)
                elif '-' in expr:
                    nums = [float(x) for x in expr.split('-')]
                    result = nums[0]
                    for n in nums[1:]:
                        result -= n
                    return str(result)
                elif '/' in expr:
                    nums = [float(x) for x in expr.split('/')]
                    result = nums[0]
                    for n in nums[1:]:
                        if n != 0:
                            result /= n
                    return str(result)
                return expr
            except:
                return '"0"'
        
        pattern = r'\d+\.?\d*\s*[\+\-\*\/]\s*\d+\.?\d*'
        while re.search(pattern, json_str):
            json_str = re.sub(pattern, replace_math, json_str)
        
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        json_str = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', json_str)
        json_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_str)
        
        return json_str.strip()

    def _safe_float(self, value: Any, default: float = 50.0) -> float:
        """Safely convert value to float with a neutral default"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                val = float(value.replace('"', ''))
                # Only return 0 if it was explicitly set to 0
                return val if val != 0 else default
            except ValueError:
                return default
        return default

    def _safe_get(self, data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
        """Safely get nested dictionary values"""
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, {})
            else:
                return default
        return current if current != {} else default

    def _build_structured_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Build structured analysis from parsed JSON"""
        return {
            "cash_flow": {
                "score": self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "cash_flow_health_score")),
                "total_inflow": self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "total_inflows")),
                "total_outflow": self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "total_outflows")),
                "net_flow": (
                    self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "total_inflows")) -
                    self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "total_outflows"))
                ),
                "summary": str(self._safe_get(analysis, "Cash Flow Analysis", "summary", default=""))
            },
            "expenses": {
                "score": self._safe_float(self._safe_get(analysis, "Expense Analysis", "expense_analysis_score")),
                "major_expenses": self._safe_get(analysis, "Expense Analysis", "major_expenses", default=[]),
                "recurring_expenses": self._safe_get(analysis, "Expense Analysis", "recurring_expenses", default=[]),
                "summary": str(self._safe_get(analysis, "Expense Analysis", "summary", default=""))
            },
            "income": {
                "score": self._safe_float(self._safe_get(analysis, "Income Analysis", "income_stability_score")),
                "regular_sources": self._safe_get(analysis, "Income Analysis", "regular_income_sources", default=[]),
                "irregular_sources": self._safe_get(analysis, "Income Analysis", "additional_irregular_income", default=[]),
                "summary": str(self._safe_get(analysis, "Income Analysis", "summary", default=""))
            },
            "debt_credit": {
                "score": self._safe_float(self._safe_get(analysis, "Debt and Credit", "debt_and_credit_score")),
                "outstanding_debt": self._safe_get(analysis, "Debt and Credit", "outstanding_debt_payments", default=[]),
                "credit_utilization": str(self._safe_get(analysis, "Debt and Credit", "credit_utilization", default="")),
                "summary": str(self._safe_get(analysis, "Debt and Credit", "summary", default=""))
            },
            "financial_health": {
                "score": self._safe_float(self._safe_get(analysis, "Financial Health Indicators", "financial_health_score")),
                "key_indicators": self._safe_get(analysis, "Financial Health Indicators", "key_indicators", default=[]),
                "summary": str(self._safe_get(analysis, "Financial Health Indicators", "summary", default=""))
            }
        }

    def _get_fallback_structure(self) -> Dict[str, Any]:
        """Return fallback structure for failed analysis"""
        return {
            "cash_flow": {"score": 50, "total_inflow": 50, "total_outflow": 50, "net_flow": 0, "summary": "Analysis failed"},
            "expenses": {"score": 50, "major_expenses": [], "recurring_expenses": [], "summary": "Analysis failed"},
            "income": {"score": 50, "regular_sources": [], "irregular_sources": [], "summary": "Analysis failed"},
            "debt_credit": {"score": 50, "outstanding_debt": [], "credit_utilization": "N/A", "summary": "Analysis failed"},
            "financial_health": {"score": 50, "key_indicators": [], "summary": "Analysis failed"}
        }