"""Data processing utilities for the application."""
from typing import Dict, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from functools import wraps
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_errors(func):
    """Decorator to handle errors in data processing functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

@st.cache_data(ttl=3600)  # Cache for 1 hour
def normalize_score(value: float, min_val: float = 0, max_val: float = 10) -> float:
    """Normalize a value to a 0-10 scale."""
    try:
        return max(min_val, min(max_val, value))
    except (TypeError, ValueError) as e:
        logger.error(f"Error normalizing score: {str(e)}")
        return 5.0  # Return neutral score on error

@handle_errors
def calculate_weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calculate weighted score from component scores."""
    if not scores or not weights:
        return 5.0
    
    total_score = 0
    total_weight = 0
    
    for key, weight in weights.items():
        if key in scores:
            total_score += scores[key] * weight
            total_weight += weight
    
    return total_score / total_weight if total_weight > 0 else 5.0

@st.cache_data(ttl=3600)
def process_time_series_data(
    data: Dict[str, Any],
    metric: str,
    lookback_days: int = 365
) -> pd.DataFrame:
    """Process time series data for visualization."""
    try:
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter last year's data
        start_date = datetime.now() - timedelta(days=lookback_days)
        df = df[df['date'] >= start_date]
        
        # Resample to daily frequency
        df = df.set_index('date').resample('D').mean().fillna(method='ffill')
        
        return df
    except Exception as e:
        logger.error(f"Error processing time series data: {str(e)}")
        return pd.DataFrame()

@handle_errors
def validate_company_input(
    company_name: str,
    ticker: str
) -> Tuple[bool, Optional[str]]:
    """Validate company name and ticker inputs."""
    if not company_name or not ticker:
        return False, "Company name and ticker are required"
    
    if len(ticker) > 5:
        return False, "Invalid ticker format"
    
    if not company_name.strip():
        return False, "Invalid company name"
    
    return True, None

@st.cache_data(ttl=3600)
def calculate_trend_metrics(
    historical_data: Dict[str, float]
) -> Dict[str, Union[float, str]]:
    """Calculate trend metrics from historical data."""
    try:
        values = list(historical_data.values())
        if len(values) < 2:
            return {'trend': 'neutral', 'change': 0.0}
        
        change = ((values[-1] - values[0]) / values[0]) * 100
        
        if change > 5:
            trend = 'positive'
        elif change < -5:
            trend = 'negative'
        else:
            trend = 'neutral'
            
        return {
            'trend': trend,
            'change': round(change, 2)
        }
    except Exception as e:
        logger.error(f"Error calculating trend metrics: {str(e)}")
        return {'trend': 'neutral', 'change': 0.0}

@handle_errors
def aggregate_sentiment_scores(
    news_score: float,
    social_score: float,
    analyst_score: float,
    stakeholder_score: float
) -> Dict[str, Any]:
    """Aggregate different sentiment scores into a final sentiment score."""
    weights = {
        'news': 0.3,
        'social': 0.2,
        'analyst': 0.3,
        'stakeholder': 0.2
    }
    
    scores = {
        'news': news_score,
        'social': social_score,
        'analyst': analyst_score,
        'stakeholder': stakeholder_score
    }
    
    final_score = calculate_weighted_score(scores, weights)
    
    confidence = min(
        1.0,
        sum(1 for score in scores.values() if score is not None) / len(scores)
    )
    
    return {
        'score': final_score,
        'confidence': confidence,
        'components': scores
    } 