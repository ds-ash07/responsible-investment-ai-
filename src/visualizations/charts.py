"""Chart creation utilities for the application."""
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from ..config.constants import COLORS, CHART_CONFIG
import logging

logger = logging.getLogger(__name__)

@st.cache_data(ttl=3600)
def create_gauge_chart(
    value: float,
    title: str,
    min_val: float = 0,
    max_val: float = 10,
    height: int = CHART_CONFIG['HEIGHT']['SMALL']
) -> go.Figure:
    """Create a gauge chart with specified parameters."""
    try:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            title={'text': title},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': COLORS['PRIMARY']},
                'steps': [
                    {'range': [0, 3.5], 'color': COLORS['DANGER']},
                    {'range': [3.5, 5], 'color': COLORS['WARNING']},
                    {'range': [5, 6.5], 'color': "yellow"},
                    {'range': [6.5, 8], 'color': "lightgreen"},
                    {'range': [8, 10], 'color': COLORS['SUCCESS']}
                ]
            }
        ))
        fig.update_layout(
            height=height,
            margin=CHART_CONFIG['MARGINS']['SMALL']
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating gauge chart: {str(e)}")
        return go.Figure()

@st.cache_data(ttl=3600)
def create_radar_chart(
    categories: List[str],
    values: List[float],
    title: str,
    height: int = CHART_CONFIG['HEIGHT']['MEDIUM']
) -> go.Figure:
    """Create a radar chart for ESG metrics."""
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=title,
            line_color=COLORS['PRIMARY']
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=False,
            title=title,
            height=height,
            margin=CHART_CONFIG['MARGINS']['MEDIUM']
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating radar chart: {str(e)}")
        return go.Figure()

@st.cache_data(ttl=3600)
def create_trend_chart(
    data: Dict[str, float],
    title: str,
    height: int = CHART_CONFIG['HEIGHT']['MEDIUM']
) -> go.Figure:
    """Create a line chart for trends."""
    try:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(data.keys()),
            y=list(data.values()),
            mode='lines+markers',
            name=title,
            line=dict(color=COLORS['PRIMARY'], width=2)
        ))
        fig.update_layout(
            title=title,
            xaxis_title="Time Period",
            yaxis_title="Value",
            height=height,
            margin=CHART_CONFIG['MARGINS']['MEDIUM'],
            template='plotly_white',
            hovermode='x unified'
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating trend chart: {str(e)}")
        return go.Figure()

@st.cache_data(ttl=3600)
def create_comparison_chart(
    companies: List[str],
    metrics: Dict[str, List[float]],
    title: str,
    height: int = CHART_CONFIG['HEIGHT']['LARGE']
) -> go.Figure:
    """Create a bar chart for company comparisons."""
    try:
        fig = go.Figure()
        
        for i, company in enumerate(companies):
            fig.add_trace(go.Bar(
                name=company,
                x=list(metrics.keys()),
                y=[metrics[metric][i] for metric in metrics.keys()],
                marker_color=COLORS['PRIMARY'] if i == 0 else COLORS['SECONDARY']
            ))
            
        fig.update_layout(
            title=title,
            barmode='group',
            height=height,
            margin=CHART_CONFIG['MARGINS']['MEDIUM'],
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        return fig
    except Exception as e:
        logger.error(f"Error creating comparison chart: {str(e)}")
        return go.Figure()

@st.cache_data(ttl=3600)
def create_sentiment_timeline(
    sentiment_data: Dict[str, Any],
    height: int = CHART_CONFIG['HEIGHT']['MEDIUM']
) -> Optional[go.Figure]:
    """Create a timeline visualization of sentiment data."""
    try:
        dates = sentiment_data.get('dates', [])
        scores = sentiment_data.get('scores', [])
        sources = sentiment_data.get('sources', [])
        
        if not dates or not scores:
            return None
            
        fig = go.Figure()
        
        # Add main sentiment line
        fig.add_trace(go.Scatter(
            x=dates,
            y=scores,
            mode='lines+markers',
            name='Sentiment Score',
            line=dict(color=COLORS['PRIMARY'], width=2),
            hovertemplate="Date: %{x}<br>Score: %{y:.2f}<br>Source: %{text}<extra></extra>",
            text=sources
        ))
        
        # Add confidence band if available
        if 'confidence' in sentiment_data:
            confidence = sentiment_data['confidence']
            fig.add_trace(go.Scatter(
                x=dates + dates[::-1],
                y=[s + c for s, c in zip(scores, confidence)] + 
                   [s - c for s, c in zip(scores[::-1], confidence[::-1])],
                fill='toself',
                fillcolor='rgba(26,35,126,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval',
                showlegend=True
            ))
        
        fig.update_layout(
            title="Sentiment Timeline",
            xaxis_title="Date",
            yaxis_title="Sentiment Score",
            height=height,
            margin=CHART_CONFIG['MARGINS']['MEDIUM'],
            template='plotly_white',
            hovermode='x unified',
            yaxis=dict(range=[0, 10])
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating sentiment timeline: {str(e)}")
        return None 