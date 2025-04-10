from typing import Dict, Any, Optional
import os
import aiohttp
import json
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

class LlamaClient:
    def __init__(self):
        self.api_key = os.getenv("LLAMA_API_KEY")
        self.api_base_url = "https://api.llama-api.com/chat/completions"
        self.maverick_model = "llama4-maverick"  
        
    async def get_maverick_completion(self, prompt: str) -> Dict[str, Any]:
        """
        Get completion from Llama-4-Maverick model
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.maverick_model,
            "messages": [
                {"role": "system", "content": "You are a financial analyst expert. Analyze the provided financial data and return structured JSON responses with detailed insights and numerical scores."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,  # Lower temperature for more consistent, analytical responses
            "response_format": {"type": "json_object"}  # Ensure JSON response
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base_url}",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_detail = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Llama API error: {error_detail}"
                        )
                    
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                    
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error calling Llama API: {str(e)}"
            )

    async def validate_and_clean_response(self, response: str) -> Dict[str, Any]:
        """
        Validate and clean the model's response
        """
        try:
            if isinstance(response, str):
                # Extract JSON from string if needed
                response = json.loads(response)
            
            # Ensure all required fields are present
            required_sections = [
                "cash_flow", "expenses", "income", 
                "debt_credit"
            ]
            
            for section in required_sections:
                if section not in response:
                    raise ValueError(f"Missing required section: {section}")
                
            return response
            
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from model")
        except Exception as e:
            raise ValueError(f"Response validation failed: {str(e)}")