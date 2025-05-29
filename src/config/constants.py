"""Constants for the application."""

# Scoring weights
WEIGHTS = {
    'ESG': {
        'ENVIRONMENTAL': 0.15,
        'SOCIAL': 0.15,
        'GOVERNANCE': 0.15,
        'SDG': 0.15,
        'CONTROVERSIES': 0.20,
        'RISK': 0.20
    },
    'FINANCIAL': {
        'PROFITABILITY': 0.25,
        'GROWTH': 0.25,
        'MARKET_PERFORMANCE': 0.25,
        'RISK_METRICS': 0.25
    },
    'SENTIMENT': {
        'NEWS': 0.30,
        'SOCIAL_MEDIA': 0.20,
        'ANALYST_RATINGS': 0.30,
        'STAKEHOLDER_FEEDBACK': 0.20
    }
}

# Score ranges
SCORE_RANGES = {
    'EXCEPTIONAL': (8.5, 10.0, 'Strong Buy'),
    'STRONG': (7.0, 8.4, 'Buy'),
    'MODERATE': (5.5, 6.9, 'Hold'),
    'CONCERNING': (4.0, 5.4, 'Sell'),
    'POOR': (0.0, 3.9, 'Strong Sell')
}

# Chart configurations
CHART_CONFIG = {
    'HEIGHT': {
        'SMALL': 200,
        'MEDIUM': 300,
        'LARGE': 400
    },
    'MARGINS': {
        'SMALL': {'l': 10, 'r': 10, 't': 30, 'b': 10},
        'MEDIUM': {'l': 40, 'r': 40, 't': 40, 'b': 40}
    }
}

# Colors
COLORS = {
    'PRIMARY': '#1a237e',
    'SECONDARY': '#0d47a1',
    'SUCCESS': '#4caf50',
    'WARNING': '#ff9800',
    'DANGER': '#ff1744',
    'INFO': '#2196f3',
    'LIGHT': '#f8f9fa',
    'DARK': '#333333'
} 