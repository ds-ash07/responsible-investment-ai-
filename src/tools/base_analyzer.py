"""Base analyzer class for all analysis types."""
from typing import Dict, List, Optional, Any
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time
from functools import lru_cache
import hashlib
from abc import ABC, abstractmethod
import traceback
import re
import yfinance as yf
from ..utils.nemotron_client import NemotronClient
import logging

logger = logging.getLogger(__name__)

class BaseAnalyzer(ABC):
    """Base class for all analyzers with common API functionality"""
    
    def __init__(self, model_key: str = 'nemotron'):
        """Initialize the analyzer with model key and API configuration"""
        print(f"\nInitialized {self.__class__.__name__} with model: nvidia/llama-3.1-nemotron-ultra-253b-v1")
        self.client = NemotronClient()
        self.model_key = model_key
        self.esg_data_key = None
        self.news_api_key = None
        
    def get_ai_response(self, prompt: str) -> Optional[str]:
        """Get AI response using the client's _make_request method."""
        try:
            response = self.client._make_request(prompt)
            if response and 'choices' in response:
                return response['choices'][0]['message']['content']
            return None
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            return None
            
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI analysis"""
        return """You are a brutally honest ESG and financial analyst. Your task is to analyze companies and provide detailed metrics in JSON format. Be critical and realistic in your assessments. All numerical scores should be between 0-10."""
    
    def _get_default_response(self) -> str:
        """Return a default JSON response string"""
        return json.dumps({
            "error": "Failed to get valid response",
            "score": 5.0,
            "metrics": {},
            "analysis": "No data available"
        })

    def _generate_cache_key(self, prompt: str, model_name: str) -> str:
        """Generate a unique cache key for a prompt and model combination"""
        cache_string = f"{prompt}:{model_name}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    @lru_cache(maxsize=1000)
    def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if available and not expired"""
        # This is handled by the lru_cache decorator
        pass
    
    def _make_api_call(self, prompt: str, retries: int = 0) -> Dict:
        """Make API call with retry logic"""
        try:
            payload = {
                "model": self.model['name'],
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429 and retries < self.model['max_retries']:
                # Rate limit hit, wait and retry
                time.sleep(2 ** retries)  # Exponential backoff
                return self._make_api_call(prompt, retries + 1)
            else:
                print(f"API call failed with status {response.status_code}: {response.text}")
                return {}
                
        except Exception as e:
            if retries < self.model['max_retries']:
                time.sleep(2 ** retries)  # Exponential backoff
                return self._make_api_call(prompt, retries + 1)
            print(f"Failed to get AI response after {retries} retries: {str(e)}")
            return {}
    
    def get_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get financial data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if not info:
                return None
                
            return {
                'info': info,
                'financials': stock.financials.to_dict() if hasattr(stock, 'financials') else None,
                'balance_sheet': stock.balance_sheet.to_dict() if hasattr(stock, 'balance_sheet') else None,
                'cash_flow': stock.cashflow.to_dict() if hasattr(stock, 'cashflow') else None
            }
        except Exception as e:
            print(f"Error fetching stock data: {str(e)}")
            return None

    def get_esg_data(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get ESG data from a provider (placeholder for actual API)"""
        if not self.esg_data_key:
            print("No ESG API key provided")
            return None
            
        try:
            # This would be replaced with actual ESG data API call
            return None
        except Exception as e:
            print(f"Error fetching ESG data: {str(e)}")
            return None

    def get_news_sentiment(self, company_name: str) -> Optional[Dict[str, Any]]:
        """Get news and social media sentiment data"""
        if not self.news_api_key:
            print("No News API key provided")
            return None
            
        try:
            # This would be replaced with actual News API call
            return None
        except Exception as e:
            print(f"Error fetching news sentiment: {str(e)}")
            return None

    def format_not_available_message(self, source: str) -> Dict[str, Any]:
        """Format a standardized message for unavailable data"""
        return {
            "data_available": False,
            "source": source,
            "message": f"No data available from {source}",
            "timestamp": datetime.now().isoformat()
        }

    def format_prompt(self, company_name: str, analysis_type: str) -> str:
        """Format prompt for AI analysis"""
        current_year = datetime.now().year
        
        if analysis_type == "sdg":
            return f"""
            Conduct a comprehensive SDG and ESG analysis for {company_name} for {current_year}.
            
            Required Analysis Points:
            1. ESG Goals and Progress
               - Current ESG initiatives
               - Progress on previous commitments
               - Measurable targets and achievements
            
            2. SDG Alignment
               - Specific SDGs addressed
               - Concrete contributions to each SDG
               - Integration with business strategy
            
            3. Financial Ethics
               - Transparency in reporting
               - Anti-corruption measures
               - Tax responsibility
               - Executive compensation fairness
            
            4. Social Responsibility
               - Employee welfare and diversity
               - Community engagement
               - Supply chain ethics
               - Human rights compliance
            
            5. Risk Management
               - ESG risk assessment
               - Climate risk preparedness
               - Regulatory compliance
               - Stakeholder engagement
            
            6. ESG Controversies
               - Past incidents
               - Resolution measures
               - Preventive policies
            
            7. Climate Action
               - Emissions reduction targets
               - Renewable energy adoption
               - Waste management
               - Environmental innovation

            IMPORTANT: Return ONLY a valid JSON object with NO comments or additional text.
            Required JSON structure:
            {{
                "scores": {{
                    "esg_goals": 7.5,
                    "sdg_alignment": 8.2,
                    "financial_ethics": 6.8,
                    "social_responsibility": 7.9,
                    "risk_management": 8.1,
                    "esg_controversies": 6.5,
                    "climate_action": 7.2
                }},
                "justifications": {{
                    "esg_goals": "Detailed explanation",
                    "sdg_alignment": "Detailed explanation"
                }},
                "strengths": [
                    {{
                        "category": "Category name",
                        "description": "Specific strength",
                        "evidence": "Concrete example"
                    }}
                ],
                "concerns": [
                    {{
                        "category": "Category name",
                        "description": "Specific concern",
                        "impact": "Potential risk"
                    }}
                ]
            }}
            """
        elif analysis_type == "sentiment":
            return f"""
            Conduct a detailed sentiment analysis for {company_name} over the past year.
            
            Analysis Requirements:
            1. Market Perception
               - Investor sentiment
               - Analyst ratings
               - Market confidence
            
            2. News Coverage
               - Major announcements
               - Press coverage tone
               - Industry comparison
            
            3. Social Media Sentiment
               - Platform-specific analysis
               - Trending topics
               - Customer feedback
            
            4. Stakeholder Feedback
               - Employee satisfaction
               - Customer reviews
               - Partner relationships
            
            5. Controversy Analysis
               - Recent issues
               - Response effectiveness
               - Resolution status

            IMPORTANT: Return ONLY a valid JSON object with NO comments or additional text.
            Required JSON structure:
            {{
                "sentiment_score": 7.5,
                "confidence": 0.85,
                "positive_factors": [
                    {{
                        "category": "Category name",
                        "description": "Specific positive",
                        "impact_score": 8.2
                    }}
                ],
                "negative_factors": [
                    {{
                        "category": "Category name",
                        "description": "Specific negative",
                        "impact_score": 6.4
                    }}
                ],
                "major_events": [
                    {{
                        "date": "2024-03",
                        "event": "Description",
                        "impact": "Impact description",
                        "score_change": -0.5
                    }}
                ],
                "trend_analysis": {{
                    "current_trend": "Trend description",
                    "future_outlook": "Outlook description"
                }}
            }}
            """
        elif analysis_type == "financial":
            return f"""
            Analyze the financial metrics for {company_name}. Provide a comprehensive analysis including:

            1. Profitability Analysis:
               - ROE (Return on Equity)
               - ROA (Return on Assets)
               - Profit Margins
            
            2. Growth Metrics:
               - Revenue Growth Rate
               - Earnings Growth
               - Market Share Trends
            
            3. Market Performance:
               - P/E Ratio
               - Market Capitalization
               - Dividend Yield
            
            4. Risk Assessment:
               - Financial Leverage
               - Market Volatility
               - Industry Position

            IMPORTANT: Return ONLY a valid JSON object with NO comments or additional text.
            Required JSON structure:
            {{
                "roe": 15.5,
                "roa": 8.3,
                "profit_margin": 12.7,
                "revenue_growth": 7.5,
                "eps_growth": 8.2,
                "stock_momentum": 7.8,
                "pe_ratio": 20.5,
                "market_cap": 100.5,
                "dividend_yield": 2.5,
                "trend": "bullish",
                "growth_rate": 7.5,
                "volatility": "moderate",
                "beta": 1.2,
                "current_ratio": 2.1,
                "debt_equity": 0.8
            }}

            All numerical values should be actual numbers (not strings or percentages).
            """
        
        return ""

    def parse_ai_response(self, response: str) -> Dict:
        """Parse AI response into structured data with error handling"""
        try:
            # Clean up the response
            # Find JSON content between triple backticks or regular backticks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```|`(\{.*?\})`', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1) or json_match.group(2)
            else:
                # If no backticks, try to find first { and last }
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                else:
                    raise ValueError("No JSON object found in response")

            # Remove any comments
            json_str = re.sub(r'//.*?\n|/\*.*?\*/', '', json_str, flags=re.DOTALL)
            # Remove any trailing commas before closing braces/brackets
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            # Parse the cleaned JSON
            parsed_response = json.loads(json_str)
            print("Successfully parsed AI response")
            return parsed_response
            
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
            print(f"Raw response: {response}")
            return self._get_default_response()

    def _get_default_response(self) -> Dict:
        """Get a default response when API fails"""
        return {
            "scores": {
                "esg_goals": 5.0,
                "sdg_alignment": 5.0,
                "financial_ethics": 5.0,
                "social_responsibility": 5.0,
                "risk_management": 5.0,
                "esg_controversies": 5.0,
                "climate_action": 5.0
            },
            "justifications": {
                "esg_goals": "Data not available",
                "sdg_alignment": "Data not available"
            },
            "strengths": [],
            "concerns": []
        }

    def _process_response(self, response: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Process the API response into standardized format."""
        if not response or not isinstance(response, dict):
            return {
                'data_available': False,
                'error': 'Analysis failed or no data available'
            }
        
        # For SDG analysis
        if 'scores' in response:
            return {
                'data_available': True,
                'scores': response['scores'],
                'justifications': response.get('justifications', {}),
                'strengths': response.get('strengths', []),
                'concerns': response.get('concerns', [])
            }
        
        # For sentiment analysis
        elif 'sentiment_score' in response:
            return {
                'data_available': True,
                'sentiment_score': response['sentiment_score'],
                'confidence': response.get('confidence', 0.0),
                'positive_factors': response.get('positive_factors', []),
                'negative_factors': response.get('negative_factors', []),
                'major_events': response.get('major_events', []),
                'trend_analysis': response.get('trend_analysis', {})
            }
        
        # For financial analysis
        elif 'roe' in response:
            return {
                'data_available': True,
                'metrics': {
                    'roe': response['roe'],
                    'roa': response.get('roa', 0.0),
                    'profit_margin': response.get('profit_margin', 0.0),
                    'revenue_growth': response.get('revenue_growth', 0.0),
                    'eps_growth': response.get('eps_growth', 0.0),
                    'stock_momentum': response.get('stock_momentum', 0.0),
                    'pe_ratio': response.get('pe_ratio', 0.0),
                    'market_cap': response.get('market_cap', 0.0),
                    'dividend_yield': response.get('dividend_yield', 0.0)
                },
                'analysis': {
                    'trend': response.get('trend', 'neutral'),
                    'growth_rate': response.get('growth_rate', 0.0),
                    'volatility': response.get('volatility', 'moderate'),
                    'beta': response.get('beta', 1.0),
                    'current_ratio': response.get('current_ratio', 0.0),
                    'debt_equity': response.get('debt_equity', 0.0)
                }
            }
        
        return {
            'data_available': False,
            'error': 'Invalid response format'
        }

    def analyze_company(self, company_name: str, analysis_type: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a company using the AI model."""
        try:
            # Use custom prompt if provided, otherwise generate standard prompt
            prompt = custom_prompt if custom_prompt else self.format_prompt(company_name, analysis_type)
            
            print(f"\nSending request to AI model for {analysis_type} analysis...")
            print(f"Prompt: {prompt}")
            
            response = self.get_ai_response(prompt)
            if not response:
                print("Failed to get AI response")
                return {
                    'data_available': False,
                    'error': 'Failed to get AI response'
                }
            
            try:
                parsed_data = self.parse_ai_response(response)
                if parsed_data:
                    return {
                        'data_available': True,
                        'analysis': json.dumps(parsed_data)
                    }
            except Exception as e:
                print(f"Error parsing AI response: {str(e)}")
                print(f"Raw response: {response}")
            
            return {
                'data_available': False,
                'error': 'Failed to parse AI response'
            }
            
        except Exception as e:
            print(f"Error in analyze_company: {str(e)}")
            traceback.print_exc()
            return {
                'data_available': False,
                'error': f"Analysis failed: {str(e)}"
            } 