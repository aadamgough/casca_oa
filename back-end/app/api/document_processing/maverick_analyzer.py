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


    def _build_analysis_prompt(self, document_content: str) -> str: # TODO: get rid of llm score generation and use sub-heuristics for calculation individual buckets
        """
        Build a prompt for Maverick to analyze the statement data
        """
        return f"""As a financial analyst, analyze this bank statement data and provide a structured analysis for each section. The summary in each sectiondoesn't need to be very short, but it should be concise. Focus on:

    1. Cash Flow Analysis:
    - Total inflows and outflows
    - Beginning and ending balance
    - Overall cash flow health

    2. Expense Analysis:
    - Major expenses, usually categoerized as "out" or "debit" (over 75% of starting or ending balance)
    - Recurring expenses
    - Expense categories breakdown

    3. Income Analysis:
    - Regular income sources
    - Additional/irregular income
    - Income stability

    4. Debt and Credit:
    - Recurring debt payments, refrence inferred liability types as described below to build this list
    - Inferred liability types, look for bank names, auto, mortgage, etc. in description or transaction name
    - Payment patterns

    Statement Data:
    {document_content}

    Please provide your analysis in exactly this JSON structure:

    {{
        "Cash Flow Analysis": {{ 
            "total_inflows": <float>,
            "total_outflows": <float>,
            "beginning_balance": <float>,
            "ending_balance": <float>,
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
            "summary": <string>
        }},
        "Debt and Credit": {{
            "recurring_debt_payments": [
                {{
                    "description": <string>,
                    "amount": <float>
                }}
            ],
            "inferred_liability_types": <string>,
            "summary": <string>
        }}
    }}

    Note: Ensure all fields are populated with appropriate indicators and keywords or phrases that relate to the statement data are in the summary to indicate positive or negative aspects."""

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
                "total_inflow": self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "total_inflows")),
                "total_outflow": self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "total_outflows")),
                "net_flow": (
                    self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "total_inflows")) -
                    self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "total_outflows"))
                ),
                "beginning_balance": self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "beginning_balance")),
                "ending_balance": self._safe_float(self._safe_get(analysis, "Cash Flow Analysis", "ending_balance")),
                "summary": str(self._safe_get(analysis, "Cash Flow Analysis", "summary", default=""))
            },
            "expenses": {
                "major_expenses": self._safe_get(analysis, "Expense Analysis", "major_expenses", default=[]),
                "recurring_expenses": self._safe_get(analysis, "Expense Analysis", "recurring_expenses", default=[]),
                "summary": str(self._safe_get(analysis, "Expense Analysis", "summary", default=""))
            },
            "income": {
                "regular_sources": self._safe_get(analysis, "Income Analysis", "regular_income_sources", default=[]),
                "irregular_sources": self._safe_get(analysis, "Income Analysis", "additional_irregular_income", default=[]),
                "summary": str(self._safe_get(analysis, "Income Analysis", "summary", default=""))
            },
            "debt_credit": {
                "recurring_debt_payments": self._safe_get(analysis, "Debt and Credit", "recurring_debt_payments", default=[]),
                "inferred_liability_types": str(self._safe_get(analysis, "Debt and Credit", "inferred_liability_types", default="")),
                "summary": str(self._safe_get(analysis, "Debt and Credit", "summary", default=""))
            }
        }

    def _get_fallback_structure(self) -> Dict[str, Any]:
        """Return fallback structure for failed analysis"""
        return {
            "cash_flow": {"total_inflow": 50, "total_outflow": 50, "net_flow": 0, "summary": "Analysis failed"},
            "expenses": {"major_expenses": [], "recurring_expenses": [], "summary": "Analysis failed"},
            "income": {"regular_sources": [], "irregular_sources": [], "summary": "Analysis failed"},
            "debt_credit": {"recurring_debt_payments": [], "inferred_liability_types": "N/A", "summary": "Analysis failed"},
        }