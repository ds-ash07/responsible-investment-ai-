"""Nemotron API client utilities."""
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
import json
import re

logger = logging.getLogger(__name__)

class NemotronClient:
    """Client for interacting with Nemotron API."""
    
    def __init__(self):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key="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"
        )
        self.model = "nvidia/llama-3.1-nemotron-ultra-253b-v1"

    def _make_request(self, prompt: str, analysis_type: str = "general") -> Optional[Dict[str, Any]]:
        """Make a request to the Nemotron API."""
        try:
            system_prompt = self._get_system_prompt(analysis_type)
            system_prompt += "\nIMPORTANT: Return ONLY a valid JSON object with NO additional text, comments, or markdown formatting."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0,
                top_p=0.95,
                max_tokens=4096,
                frequency_penalty=0,
                presence_penalty=0,
                stream=False
            )
            
            if completion and completion.choices:
                content = completion.choices[0].message.content
                # Try to extract JSON from the response
                try:
                    # Find JSON content between triple backticks or regular backticks
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```|`(\{.*?\})`', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1) or json_match.group(2)
                    else:
                        # If no backticks, try to find first { and last }
                        start_idx = content.find('{')
                        end_idx = content.rfind('}') + 1
                        if start_idx >= 0 and end_idx > start_idx:
                            json_str = content[start_idx:end_idx]
                        else:
                            raise ValueError("No JSON object found in response")

                    # Remove any comments and trailing commas
                    json_str = re.sub(r'//.*?\n|/\*.*?\*/', '', json_str, flags=re.DOTALL)
                    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    
                    # Parse the cleaned JSON
                    parsed_json = json.loads(json_str)
                    return {"choices": [{"message": {"content": json.dumps(parsed_json)}}]}
                    
                except Exception as e:
                    logger.error(f"Failed to parse JSON from response: {str(e)}")
                    return None
            
            return None

        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return None

    def _get_system_prompt(self, analysis_type: str) -> str:
        """Get appropriate system prompt based on analysis type."""
        prompts = {
            "sdg": """You are an expert ESG and SDG analyst. Analyze companies based on their ESG performance and SDG alignment. 
                     Return ONLY a valid JSON object with scores between 0-10 for environmental, social, governance, and SDG alignment categories.
                     The JSON MUST follow this exact structure:
                     {
                         "scores": {
                             "esg_goals": 7.5,
                             "sdg_alignment": 8.0,
                             "financial_ethics": 7.0,
                             "social_responsibility": 8.5,
                             "risk_management": 7.8,
                             "esg_controversies": 6.5,
                             "climate_action": 8.2
                         },
                         "justifications": {
                             "esg_goals": "Detailed explanation",
                             "sdg_alignment": "Detailed explanation"
                         },
                         "strengths": [
                             {
                                 "category": "Category name",
                                 "description": "Specific strength",
                                 "evidence": "Concrete example"
                             }
                         ],
                         "concerns": [
                             {
                                 "category": "Category name",
                                 "description": "Specific concern",
                                 "impact": "Potential risk"
                             }
                         ]
                     }""",
            
            "sentiment": """You are an expert in market sentiment analysis. Analyze companies based on market perception, news sentiment, 
                          and stakeholder feedback. Return ONLY a valid JSON object with scores between 0-10 for various sentiment categories.
                          The JSON MUST follow this exact structure:
                          {
                              "sentiment_score": 7.5,
                              "confidence": 0.85,
                              "positive_factors": [
                                  {
                                      "category": "Category name",
                                      "description": "Specific positive",
                                      "impact_score": 8.2
                                  }
                              ],
                              "negative_factors": [
                                  {
                                      "category": "Category name",
                                      "description": "Specific negative",
                                      "impact_score": 6.4
                                  }
                              ],
                              "major_events": [
                                  {
                                      "date": "2024-03",
                                      "event": "Description",
                                      "impact": "Impact description",
                                      "score_change": -0.5
                                  }
                              ],
                              "trend_analysis": {
                                  "current_trend": "Trend description",
                                  "future_outlook": "Outlook description"
                              }
                          }""",
            
            "financial": """You are an expert financial analyst. Analyze companies based on their financial performance, market position, 
                          and risk metrics. Return ONLY a valid JSON object with actual numerical values (not strings).
                          The JSON MUST follow this exact structure:
                          {
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
                          }""",
            
            "general": """You are a brutally honest ESG and financial analyst. Your task is to analyze companies and provide detailed metrics 
                         in JSON format. Be critical and realistic in your assessments. All numerical scores should be between 0-10."""
        }
        return prompts.get(analysis_type, prompts["general"])

    def analyze_company(self, company_name: str, analysis_type: str, custom_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Analyze company based on specified analysis type."""
        try:
            # Use custom prompt if provided, otherwise create analysis-specific prompt
            if custom_prompt:
                prompt = custom_prompt
            else:
                if analysis_type == 'SDG':
                    prompt = f"Analyze {company_name}'s ESG performance and SDG alignment. Focus on environmental impact, social responsibility, governance practices, and specific contributions to UN Sustainable Development Goals. Return ONLY a valid JSON object following the exact structure specified."
                elif analysis_type == 'SENTIMENT':
                    prompt = f"Analyze market sentiment and public perception of {company_name}. Include news sentiment, social media analysis, stakeholder feedback, and overall market confidence. Return ONLY a valid JSON object following the exact structure specified."
                elif analysis_type == 'FINANCIAL':
                    prompt = f"Provide a comprehensive financial analysis of {company_name}. Include profitability metrics, growth indicators, market performance, and risk assessment. Return ONLY a valid JSON object following the exact structure specified."
                else:
                    raise ValueError(f"Invalid analysis type: {analysis_type}")

            response = self._make_request(prompt, analysis_type.lower())
            
            if response and 'choices' in response:
                return {
                    'data_available': True,
                    'analysis': response['choices'][0]['message']['content'],
                    'analysis_type': analysis_type,
                    'company_name': company_name
                }

            return None

        except Exception as e:
            logger.error(f"Analysis failed for {company_name}: {str(e)}")
            return None 