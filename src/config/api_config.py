"""API configuration settings."""

NEMOTRON_CONFIG = {
    'API_KEY': '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',
    'MODEL_NAME': 'llama-3.1-nemotron-ultra-253b-v1',
    'MAX_TOKENS': 4096,
    'TEMPERATURE': 0.7,
    'TOP_P': 0.95,
    'PRESENCE_PENALTY': 0.0,
    'FREQUENCY_PENALTY': 0.0
}

# Base prompts for different analysis types
ANALYSIS_PROMPTS = {
    'SDG': """Analyze the company's alignment with Sustainable Development Goals and ESG criteria. 
    Focus on environmental impact, social responsibility, governance practices, and sustainability initiatives.
    Provide detailed scoring for each category on a scale of 0-10.""",
    
    'SENTIMENT': """Analyze market sentiment, news coverage, and public perception of the company.
    Consider recent developments, media coverage, social media sentiment, and stakeholder feedback.
    Provide detailed scoring for each category on a scale of 0-10.""",
    
    'FINANCIAL': """Analyze the company's financial health, market performance, and risk metrics.
    Consider profitability, growth, market position, and risk management practices.
    Provide detailed scoring for each category on a scale of 0-10."""
} 