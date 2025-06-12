"""Financial Analyzer using Nemotron API."""
from typing import Dict, List, Any
from tools.base_analyzer import BaseAnalyzer
import json
import traceback
import logging

logger = logging.getLogger(__name__)

class FinancialAnalyzer(BaseAnalyzer):
    """Financial Analysis using AI"""
    
    def __init__(self, model_key: str = 'nemotron'):
        super().__init__(model_key=model_key)
    
    def analyze(self, ticker: str) -> Dict[str, Any]:
        """Analyze financial metrics for a company"""
        try:
            print(f"\nAnalyzing financial metrics for {ticker}...")
            
            # Get comprehensive AI analysis
            response = self.client.analyze_company(ticker, 'FINANCIAL')
            
            if response and response.get('data_available'):
                try:
                    data = json.loads(response['analysis'])
                    
                    # Get additional AI insights
                    insights_prompt = f"""Analyze {ticker}'s financial performance and provide:
                    1. Key strengths and competitive advantages
                    2. Major risks and challenges
                    3. Growth opportunities
                    4. Market positioning
                    5. Future outlook
                    
                    Format the response as a JSON object with these exact keys:
                    {{
                        "strengths": ["strength1", "strength2", "strength3"],
                        "risks": ["risk1", "risk2", "risk3"],
                        "opportunities": ["opportunity1", "opportunity2", "opportunity3"],
                        "positioning": "Detailed market position analysis",
                        "outlook": "Comprehensive future outlook"
                    }}"""
                    
                    insights_response = self.get_ai_response(insights_prompt)
                    if insights_response:
                        try:
                            insights = json.loads(insights_response)
                            data['ai_insights'] = insights
                        except json.JSONDecodeError:
                            logger.error("Failed to parse AI insights")
                            data['ai_insights'] = {
                                "strengths": [],
                                "risks": [],
                                "opportunities": [],
                                "positioning": "Analysis not available",
                                "outlook": "Analysis not available"
                            }
                    
                    data.update({
                        "data_available": True,
                        "data_sources": ["AI Analysis", "Market Data"]
                    })
                    
                    return data
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse financial analysis: {e}")
                    logger.debug(f"Raw response: {response['analysis']}")
            
            return self._get_default_result()
            
        except Exception as e:
            logger.error(f"Financial analysis failed for {ticker}: {str(e)}")
            return {
                'data_available': False,
                'error': f"Analysis failed: {str(e)}"
            }
    
    def validate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize financial metrics"""
        try:
            # Extract ethics score and analysis
            ethics_score = float(data.get('ethics_score', 5.0))
            ethics_issues = data.get('ethics_issues', [])
            ethics_strengths = data.get('ethics_strengths', [])
            
            # Get raw metrics
            raw_metrics = data.get('metrics', {})
            
            # Convert all metrics to proper format with better validation
            metrics = {
                'profitability': {
                    'ROE': self._format_percentage(raw_metrics.get('profitability', {}).get('roe')),
                    'ROA': self._format_percentage(raw_metrics.get('profitability', {}).get('roa')),
                    'Profit Margin': self._format_percentage(raw_metrics.get('profitability', {}).get('profit_margin')),
                    'Operating Margin': self._format_percentage(raw_metrics.get('profitability', {}).get('operating_margin'))
                },
                'market_performance': {
                    'P/E Ratio': self._format_number(raw_metrics.get('market_performance', {}).get('pe_ratio')),
                    'Market Cap': self._format_billions(raw_metrics.get('market_performance', {}).get('market_cap')),
                    'Stock Momentum': self._format_percentage(raw_metrics.get('market_performance', {}).get('stock_momentum')),
                    'Dividend Yield': self._format_percentage(raw_metrics.get('market_performance', {}).get('dividend_yield'))
                },
                'growth': {
                    'Revenue Growth': self._format_percentage(raw_metrics.get('growth', {}).get('revenue_growth')),
                    'EPS Growth': self._format_percentage(raw_metrics.get('growth', {}).get('eps_growth')),
                    'Market Share Growth': self._format_percentage(raw_metrics.get('growth', {}).get('market_share_growth'))
                }
            }
            
            # Add risk metrics with validation
            risk_metrics = {
                'Beta': self._format_number(raw_metrics.get('risk', {}).get('beta')),
                'Current Ratio': self._format_number(raw_metrics.get('risk', {}).get('current_ratio')),
                'Debt/Equity': self._format_number(raw_metrics.get('risk', {}).get('debt_equity')),
                'Credit Rating': raw_metrics.get('risk', {}).get('credit_rating', 'N/A')
            }
            
            # Calculate strengths and weaknesses based on metrics and ethics
            strengths = []
            weaknesses = []
            
            # Add ethics-related strengths and weaknesses
            for issue in ethics_issues:
                if isinstance(issue, dict):
                    weaknesses.append({
                        'category': 'Financial Ethics',
                        'description': issue.get('description', ''),
                        'risk_level': issue.get('severity', 'High'),
                        'evidence': issue.get('evidence', '')
                    })
            
            for strength in ethics_strengths:
                if isinstance(strength, dict):
                    strengths.append({
                        'category': 'Financial Ethics',
                        'description': strength.get('description', ''),
                        'evidence': strength.get('evidence', '')
                    })
            
            # Add metric-based analysis
            self._analyze_metrics(raw_metrics, strengths, weaknesses)
            
            return {
                'ethics_score': ethics_score,
                'ethics_issues': ethics_issues,
                'ethics_strengths': ethics_strengths,
                'metrics': metrics,
                'risk_metrics': risk_metrics,
                'strengths': strengths,
                'weaknesses': weaknesses
            }
            
        except Exception as e:
            print(f"Error in validate_metrics: {str(e)}")
            traceback.print_exc()
            return self._get_default_result()
    
    def _analyze_metrics(self, metrics: Dict[str, Any], strengths: List[Dict], weaknesses: List[Dict]):
        """Analyze financial metrics and add to strengths/weaknesses"""
        try:
            profitability = metrics.get('profitability', {})
            market = metrics.get('market_performance', {})
            growth = metrics.get('growth', {})
            risk = metrics.get('risk', {})
            
            # Analyze ROE
            roe = self._parse_number(profitability.get('roe'))
            if roe > 15:
                strengths.append({
                    'category': 'Profitability',
                    'description': f'Strong Return on Equity at {roe:.1f}%',
                    'evidence': 'Above industry average of 15%'
                })
            elif roe < 10 and roe > 0:
                weaknesses.append({
                    'category': 'Profitability',
                    'description': f'Poor Return on Equity at {roe:.1f}%',
                    'risk_level': 'High',
                    'evidence': 'Below industry minimum of 10%'
                })
            
            # Analyze Revenue Growth
            rev_growth = self._parse_number(growth.get('revenue_growth'))
            if rev_growth > 10:
                strengths.append({
                    'category': 'Growth',
                    'description': f'Strong revenue growth at {rev_growth:.1f}%',
                    'evidence': 'Above market average of 10%'
                })
            elif rev_growth < 5 and rev_growth > 0:
                weaknesses.append({
                    'category': 'Growth',
                    'description': f'Stagnant revenue growth at {rev_growth:.1f}%',
                    'risk_level': 'Medium',
                    'evidence': 'Below market average of 5%'
                })
            
            # Analyze P/E Ratio
            pe_ratio = self._parse_number(market.get('pe_ratio'))
            if 10 <= pe_ratio <= 25:
                strengths.append({
                    'category': 'Valuation',
                    'description': f'Reasonable P/E ratio at {pe_ratio:.1f}',
                    'evidence': 'Within optimal range of 10-25'
                })
            elif pe_ratio > 35:
                weaknesses.append({
                    'category': 'Valuation',
                    'description': f'Overvalued with P/E ratio at {pe_ratio:.1f}',
                    'risk_level': 'High',
                    'evidence': 'Significantly above optimal range'
                })
            
            # Analyze Financial Health
            current_ratio = self._parse_number(risk.get('current_ratio'))
            if current_ratio >= 2:
                strengths.append({
                    'category': 'Financial Health',
                    'description': f'Strong liquidity with current ratio of {current_ratio:.1f}',
                    'evidence': 'Above recommended minimum of 2.0'
                })
            elif current_ratio < 1 and current_ratio > 0:
                weaknesses.append({
                    'category': 'Financial Health',
                    'description': f'Liquidity risk with current ratio of {current_ratio:.1f}',
                    'risk_level': 'High',
                    'evidence': 'Below critical threshold of 1.0'
                })
                
            # Analyze Debt/Equity
            debt_equity = self._parse_number(risk.get('debt_equity'))
            if debt_equity < 0.5 and debt_equity > 0:
                strengths.append({
                    'category': 'Financial Health',
                    'description': f'Conservative debt management with D/E ratio of {debt_equity:.1f}',
                    'evidence': 'Below industry average of 0.5'
                })
            elif debt_equity > 2:
                weaknesses.append({
                    'category': 'Financial Health',
                    'description': f'High leverage with D/E ratio of {debt_equity:.1f}',
                    'risk_level': 'High',
                    'evidence': 'Above critical threshold of 2.0'
                })
                
        except Exception as e:
            print(f"Error analyzing metrics: {str(e)}")
            traceback.print_exc()
    
    def _format_percentage(self, value: Any) -> str:
        """Format a value as a percentage string"""
        try:
            num = float(value)
            return f"{num:.1f}%" if num != 5.0 else "N/A"
        except (TypeError, ValueError):
            return "N/A"
    
    def _format_number(self, value: Any) -> str:
        """Format a number with one decimal place"""
        try:
            num = float(value)
            return f"{num:.1f}" if num != 5.0 else "N/A"
        except (TypeError, ValueError):
            return "N/A"
    
    def _format_billions(self, value: Any) -> str:
        """Format a number in billions with B suffix"""
        try:
            num = float(value)
            return f"${num:.1f}B" if num != 5.0 else "N/A"
        except (TypeError, ValueError):
            return "N/A"
    
    def _parse_number(self, value: Any) -> float:
        """Parse a number from various formats, return 0 if invalid"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                # Remove currency symbols, B/M suffixes, % signs, and commas
                clean_value = value.replace('$', '').replace('B', '').replace('M', '').replace('%', '').replace(',', '')
                return float(clean_value)
            except ValueError:
                return 0.0
        return 0.0
    
    def calculate_final_score(self, data: Dict[str, Any]) -> float:
        """Calculate final financial score based on key metrics"""
        try:
            scores = []
            
            # ROE Score (0-10)
            roe = float(data.get('roe', 5.0))
            roe_score = min(10, max(0, roe / 2))  # 20% ROE = 10 score
            scores.append(roe_score)
            
            # Revenue Growth Score (0-10)
            rev_growth = float(data.get('revenue_growth', 5.0))
            growth_score = min(10, max(0, rev_growth))  # 10% growth = 10 score
            scores.append(growth_score)
            
            # P/E Ratio Score (0-10)
            pe = float(data.get('pe_ratio', 20))
            pe_score = 10 if 10 <= pe <= 25 else (5 if 25 < pe <= 35 else 2)
            scores.append(pe_score)
            
            # Current Ratio Score (0-10)
            cr = float(data.get('current_ratio', 1.5))
            cr_score = min(10, max(0, cr * 5))  # 2.0 ratio = 10 score
            scores.append(cr_score)
            
            return round(sum(scores) / len(scores), 2)
            
        except Exception as e:
            print(f"Error calculating final score: {str(e)}")
            return 5.0
    
    def _get_default_result(self) -> Dict[str, Any]:
        """Return default result structure with N/A values"""
        return {
            'ethics_score': 5.0,
            'ethics_issues': [],
            'ethics_strengths': [],
            'metrics': {
                'profitability': {
                    'ROE': 'N/A',
                    'ROA': 'N/A',
                    'Profit Margin': 'N/A',
                    'Operating Margin': 'N/A'
                },
                'market_performance': {
                    'P/E Ratio': 'N/A',
                    'Market Cap': 'N/A',
                    'Stock Momentum': 'N/A',
                    'Dividend Yield': 'N/A'
                },
                'growth': {
                    'Revenue Growth': 'N/A',
                    'EPS Growth': 'N/A',
                    'Market Share Growth': 'N/A'
                }
            },
            'risk_metrics': {
                'Beta': 'N/A',
                'Current Ratio': 'N/A',
                'Debt/Equity': 'N/A',
                'Credit Rating': 'N/A'
            },
            'strengths': [],
            'weaknesses': []
        } 