# AI Responsible Investing Platform 🌱💹

A sophisticated AI-powered investment analysis platform that combines ESG (Environmental, Social, and Governance) metrics, SDG (Sustainable Development Goals) alignment, market sentiment, and financial analysis to provide comprehensive investment insights. Powered by NVIDIA's Nemotron LLM and modern data analytics.

## Core Features 🚀

### ESG & SDG Analysis Engine
- **Environmental Impact Assessment**
  - Carbon emissions tracking
  - Resource usage efficiency
  - Waste management practices
  - Environmental policy compliance
- **Social Responsibility Evaluation**
  - Workforce diversity metrics
  - Human rights compliance
  - Community impact assessment
  - Labor practices analysis
- **Governance Structure Analysis**
  - Board composition evaluation
  - Executive compensation analysis
  - Shareholder rights assessment
  - Transparency metrics

### Advanced Market Sentiment Analysis
- **Multi-Source Sentiment Processing**
  - Real-time news sentiment analysis
  - Social media sentiment tracking
  - Stakeholder feedback analysis
  - Market confidence metrics
- **Temporal Analysis**
  - Trend identification
  - Historical pattern recognition
  - Future outlook prediction
  - Volatility assessment

### Financial Analytics
- **Core Financial Metrics**
  - ROE (Return on Equity)
  - ROA (Return on Assets)
  - Profit margins
  - Growth indicators
- **Market Performance**
  - Stock momentum analysis
  - Volatility metrics
  - Trading volume analysis
  - Price trend evaluation

## Technical Architecture 🏗️

### AI/ML Components
- **Primary Model**: NVIDIA Nemotron (llama-3.1-nemotron-ultra-253b-v1)
- **NLP Processing**: NLTK for text analysis
- **Machine Learning**: scikit-learn for metric processing
- **Deep Learning**: PyTorch for advanced analytics

### Data Integration
- **Financial Data**: Yahoo Finance API
- **Market Data**: Real-time market feeds
- **News Sources**: Multiple news API integrations
- **Social Media**: Platform-specific API connections

### Visualization Engine
- **Framework**: Streamlit
- **Charts**: Plotly
- **UI Components**: Custom React components
- **Styling**: Modern CSS with responsive design

## Installation Guide 🔧

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-responsible-investing.git
cd ai-responsible-investing
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys:
# - NEMOTRON_API_KEY
# - NEWS_API_KEY
# - ESG_DATA_KEY
```

## Usage Guide 📚

1. Start the application:
```bash
streamlit run src/app.py
```

2. Input Analysis:
   - Enter company name or ticker symbol
   - Select analysis timeframe
   - Choose analysis components

3. View Results:
   - ESG Performance Dashboard
   - SDG Alignment Metrics
   - Market Sentiment Analysis
   - Financial Health Indicators
   - AI-Generated Insights

## Project Structure 📁

```
ai-responsible-investing/
├── src/
│   ├── config/           # Configuration files
│   │   ├── api_config.py # API configurations
│   │   ├── constants.py  # System constants
│   │   └── tasks.yaml    # Analysis task definitions
│   ├── tools/            # Analysis tools
│   │   ├── base_analyzer.py    # Base analysis class
│   │   ├── sdg_analyzer.py     # SDG analysis
│   │   ├── sentiment_analyzer.py # Sentiment analysis
│   │   └── financial_analyzer.py # Financial analysis
│   ├── utils/            # Utility functions
│   │   ├── data_processing.py  # Data processors
│   │   └── nemotron_client.py  # AI model client
│   └── visualizations/   # Visualization components
│       └── charts.py     # Chart generators
├── .devcontainer/        # Development container config
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt      # Project dependencies
└── setup.py             # Package configuration
```

## Configuration ⚙️

### API Configuration
- `src/config/api_config.py`: API endpoints and authentication
- `src/config/constants.py`: System constants and weights
- `src/config/tasks.yaml`: Analysis task definitions

### Analysis Weights
```yaml
ESG_WEIGHTS:
  ENVIRONMENTAL: 0.15
  SOCIAL: 0.15
  GOVERNANCE: 0.15
  SDG: 0.15
  CONTROVERSIES: 0.20
  RISK: 0.20

SENTIMENT_WEIGHTS:
  NEWS: 0.30
  SOCIAL_MEDIA: 0.20
  ANALYST_RATINGS: 0.30
  STAKEHOLDER_FEEDBACK: 0.20
```

## Development 👩‍💻

### Setting Up Development Environment
1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

### Running Tests
```bash
pytest tests/
```

### Code Style
- Black for Python formatting
- flake8 for linting
- isort for import sorting

## Contributing 🤝

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 👏

- NVIDIA for the Nemotron AI model
- Yahoo Finance for financial data
- Various ESG data providers
- Open-source community

## Disclaimer ⚠️

This tool is for informational purposes only and should not be considered as financial advice. Always conduct thorough research and consult with financial professionals before making investment decisions. 