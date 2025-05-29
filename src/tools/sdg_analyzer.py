"""SDG Analyzer using Nemotron API."""
from typing import Dict, Any, Optional
from src.tools.base_analyzer import BaseAnalyzer
import json
import traceback
import yfinance as yf
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SDGAnalyzer(BaseAnalyzer):
    """SDG and Ethical Analysis using AI"""
    
    def __init__(self, model_key: str = 'nemotron'):
        super().__init__(model_key=model_key)
        self.weights = {
            'esg_goals': 0.15,
            'sdg_alignment': 0.10,
            'financial_ethics': 0.15,
            'social_responsibility': 0.15,
            'risk_management': 0.15,
            'esg_controversies': 0.20,
            'climate_action': 0.10
        }

    def analyze(self, company_name: str) -> Dict[str, Any]:
        """Analyze company's SDG alignment and ESG performance"""
        try:
            print(f"\nAnalyzing SDG alignment for {company_name}...")
            response = self.client.analyze_company(company_name, 'SDG')
            
            if response and response.get('data_available'):
                try:
                    data = json.loads(response['analysis'])
                    print("Successfully parsed AI SDG response")
                    data["data_available"] = True
                    data["data_sources"] = ["AI Analysis"]
                    return data
                except json.JSONDecodeError as e:
                    print(f"Failed to parse AI SDG response: {e}")
                    print(f"Raw response: {response['analysis']}")
            
            return self.format_not_available_message("AI Analysis")
                
        except Exception as e:
            print(f"Error in SDG analysis: {str(e)}")
            traceback.print_exc()
            return self.format_not_available_message("Error in Analysis")

    def validate_scores(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize SDG scores"""
        try:
            # Calculate overall score from detailed scores
            detailed_scores = data.get('detailed_scores', {})
            overall_score = sum([
                float(detailed_scores.get('environmental_impact', 5.0)),
                float(detailed_scores.get('social_impact', 5.0)),
                float(detailed_scores.get('governance_quality', 5.0)),
                float(detailed_scores.get('sdg_alignment', 5.0))
            ]) / 4.0

            # Structure the data in the required format
            result = {
                "overall_score": overall_score,
                "environmental": {
                    "climate_action": {
                        "score": float(detailed_scores.get('environmental_impact', 5.0)),
                        "details": self._get_evidence_details(data, 'environmental', 'climate')
                    },
                    "resource_efficiency": {
                        "score": float(detailed_scores.get('environmental_impact', 5.0)),
                        "details": self._get_evidence_details(data, 'environmental', 'resources')
                    },
                    "water_management": {
                        "score": float(detailed_scores.get('environmental_impact', 5.0)),
                        "details": self._get_evidence_details(data, 'environmental', 'water')
                    },
                    "waste_management": {
                        "score": float(detailed_scores.get('environmental_impact', 5.0)),
                        "details": self._get_evidence_details(data, 'environmental', 'waste')
                    }
                },
                "social": {
                    "social_equity": {
                        "score": float(detailed_scores.get('social_impact', 5.0)),
                        "details": self._get_evidence_details(data, 'social', 'equity')
                    },
                    "labor_practices": {
                        "score": float(detailed_scores.get('social_impact', 5.0)),
                        "details": self._get_evidence_details(data, 'social', 'labor')
                    },
                    "human_rights": {
                        "score": float(detailed_scores.get('social_impact', 5.0)),
                        "details": self._get_evidence_details(data, 'social', 'rights')
                    },
                    "community_impact": {
                        "score": float(detailed_scores.get('social_impact', 5.0)),
                        "details": self._get_evidence_details(data, 'social', 'community')
                    }
                },
                "governance": {
                    "board_diversity": {
                        "score": float(detailed_scores.get('governance_quality', 5.0)),
                        "details": self._get_evidence_details(data, 'governance', 'diversity')
                    },
                    "transparency": {
                        "score": float(detailed_scores.get('governance_quality', 5.0)),
                        "details": self._get_evidence_details(data, 'governance', 'transparency')
                    },
                    "ethics_compliance": {
                        "score": float(detailed_scores.get('governance_quality', 5.0)),
                        "details": self._get_evidence_details(data, 'governance', 'ethics')
                    },
                    "risk_management": {
                        "score": float(detailed_scores.get('governance_quality', 5.0)),
                        "details": self._get_evidence_details(data, 'governance', 'risk')
                    }
                },
                "sdg_alignment": {
                    "environmental": {
                        "score": float(detailed_scores.get('sdg_alignment', 5.0)),
                        "details": "SDG Environmental Goals Alignment"
                    },
                    "social": {
                        "score": float(detailed_scores.get('sdg_alignment', 5.0)),
                        "details": "SDG Social Goals Alignment"
                    },
                    "economic": {
                        "score": float(detailed_scores.get('sdg_alignment', 5.0)),
                        "details": "SDG Economic Goals Alignment"
                    },
                    "partnerships": {
                        "score": float(detailed_scores.get('sdg_alignment', 5.0)),
                        "details": "SDG Partnership Goals Alignment"
                    }
                }
            }
            
            return result

        except Exception as e:
            print(f"Error in score validation: {str(e)}")
            traceback.print_exc()
            return self._get_default_result()

    def _get_evidence_details(self, data: Dict[str, Any], category: str, subcategory: str) -> str:
        """Extract relevant evidence details for a specific category and subcategory"""
        try:
            evidence_list = data.get('evidence', {}).get(category, [])
            for evidence in evidence_list:
                if isinstance(evidence, dict) and subcategory.lower() in evidence.get('issue', '').lower():
                    return f"{evidence.get('issue', '')}: {evidence.get('data', '')}"
            return "No specific evidence available"
        except Exception:
            return "Error retrieving evidence"

    def _get_default_result(self) -> Dict[str, Any]:
        """Return default result structure when analysis fails"""
        return {
            "overall_score": 5.0,
            "environmental": {
                "climate_action": {"score": 5.0, "details": "No data available"},
                "resource_efficiency": {"score": 5.0, "details": "No data available"},
                "water_management": {"score": 5.0, "details": "No data available"},
                "waste_management": {"score": 5.0, "details": "No data available"}
            },
            "social": {
                "social_equity": {"score": 5.0, "details": "No data available"},
                "labor_practices": {"score": 5.0, "details": "No data available"},
                "human_rights": {"score": 5.0, "details": "No data available"},
                "community_impact": {"score": 5.0, "details": "No data available"}
            },
            "governance": {
                "board_diversity": {"score": 5.0, "details": "No data available"},
                "transparency": {"score": 5.0, "details": "No data available"},
                "ethics_compliance": {"score": 5.0, "details": "No data available"},
                "risk_management": {"score": 5.0, "details": "No data available"}
            },
            "sdg_alignment": {
                "environmental": {"score": 5.0, "details": "No data available"},
                "social": {"score": 5.0, "details": "No data available"},
                "economic": {"score": 5.0, "details": "No data available"},
                "partnerships": {"score": 5.0, "details": "No data available"}
            }
        } 