# Financial RAG System

A sophisticated Retrieval-Augmented Generation (RAG) system for financial analysis that predicts corporate investment projects and calculates Tobin's q ratios using multi-source financial data.

## Overview

This system combines financial documents, conference calls, patents, and market data to analyze companies and predict their next strategic investment projects. It uses **Pinecone** as a vector database and **OpenAI** language models to provide AI-powered financial insights with particular focus on Tobin's q ratio calculations.

### Key Features

- 🏦 **Multi-Source Financial RAG**: Integrates 10-K filings, conference calls, patent data, WSJ articles, and academic research
- 📊 **Tobin's Q Prediction**: Calculates market value to implementation cost ratios for predicted projects
- 🔍 **Semantic Search + Reranking**: Uses Pinecone embeddings with BGE reranker for relevant document retrieval
- 📈 **Financial Anchoring**: Grounds predictions in actual company financial metrics from Compustat
- 🎯 **Structured Output**: Uses Pydantic models for consistent project predictions with confidence scores
- 📋 **Comprehensive Evaluation**: Generates correlation analysis and statistical summaries

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │────│  Pinecone Vector │────│   OpenAI LLM    │
│                 │    │     Database     │    │   (GPT-4o-mini) │
│ • 10-K Filings  │    │                  │    │                 │
│ • Conf. Calls   │    │ • Embeddings     │    │ • Analysis      │
│ • Patents       │    │ • Retrieval      │    │ • Predictions   │
│ • WSJ Articles  │    │ • Reranking      │    │ • Structured    │
│ • Academic      │    │                  │    │   Output        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                       ┌──────────▼──────────┐
                       │   Analysis Pipeline  │
                       │                     │
                       │ 1. Company Query    │
                       │ 2. Multi-namespace  │
                       │    Retrieval        │
                       │ 3. Context Building │
                       │ 4. LLM Analysis     │
                       │ 5. Project Prediction│
                       │ 6. Q-ratio Extract. │
                       └─────────────────────┘
```

## Data Sources

The system retrieves information from multiple financial data namespaces:

- **10K-item1**: Business descriptions and strategic overviews
- **10K-item7**: Management Discussion & Analysis (MD&A) 
- **conference_call**: Quarterly earnings call transcripts
- **patents**: Patent filing data and innovation indicators
- **wsj_frontpage**: Wall Street Journal market analysis
- **academic-papers**: Research on Tobin's q and investment theory

## Installation

### Prerequisites

- Python 3.8+
- Pinecone API key and index named "finance-rag"
- OpenAI API key  
- Dropbox API credentials (for accessing financial datasets)

### Dependencies

Install required packages:

```bash
cd Retrieval_Code/
pip install -r requirements.txt
```

Key dependencies:
- `pinecone>=7.3.0` - Vector database client
- `langchain-pinecone` - Pinecone integration with embeddings
- `openai>=1.107.1` - OpenAI API client
- `dropbox` - Data storage access
- `pandas` - Data manipulation
- `pydantic` - Data validation and structured models
- `matplotlib` - Visualization
- `scikit-learn` - Statistical analysis

### Environment Setup

Create a `.env` file in the `Retrieval_Code/` directory:

```env
PINECONE_API_KEY=your_pinecone_api_key
OPENAI_API_KEY=your_openai_api_key
DBX_APP_KEY=your_dropbox_app_key
DBX_APP_SECRET=your_dropbox_app_secret
DBX_REFRESH_TOKEN=your_dropbox_refresh_token
```

**Note**: The system expects a Pinecone index named "finance-rag" with the following namespaces:
- `10K-item1`, `10K-item7` - SEC filing data
- `conference_call` - Earnings call transcripts  
- `patents` - Patent filings
- `wsj_frontpage` - News articles
- `academic-papers` - Research literature

## Usage

### Basic Analysis

Run analysis on a sample of companies:

```bash
cd Retrieval_Code/
python main.py
```

This will:
1. Load company data from the configured sample size (default: 10 companies)
2. Process each company through the RAG pipeline
3. Generate project predictions with Tobin's q ratios
4. Save results, plots, and summary statistics

### Configuration

Modify analysis parameters in `main.py`:

```python
# Sample size (10, 50, or 100 companies)
sample_size = 10

# Enable verbose output with prompts and responses
main(verbose=True)
```

### Testing Basic Functionality

Test that all dependencies are correctly installed:

```bash
cd Retrieval_Code/
python -c "import pinecone; import openai; import pandas; from models import ProjectsPayload; print('All imports successful')"
```

### Custom Company Analysis

For analyzing specific companies, use the retrieval functions directly:

```python
from retriever import generate_predictions
from data_loader import load_comp_total

# Load financial data
comp_data = load_comp_total()
company_data = comp_data[(comp_data['gvkey'] == 12345) & (comp_data['fyear'] == 2023)]

# Analyze a specific company
results = generate_predictions(
    gvkey="12345",           # Company identifier  
    fyear=2023,              # Fiscal year
    cusip="123456789",       # CUSIP identifier
    comn="Apple Inc",        # Company name
    comp_row=company_data,   # Financial metrics DataFrame
    verbose=True
)
```

## Output

The system generates several outputs:

### Results CSV
Contains predicted projects with:
- `q1`, `q2`, `q3`: Tobin's q ratios for three predicted projects
- `mkv1-3`: Market values (in millions USD)
- `cost1-3`: Implementation costs (in millions USD)
- Company and year identifiers

### Visualizations
- **Q-ratio Distributions**: Histograms showing the distribution of predicted Tobin's q values
- **Correlation Analysis**: Statistical relationships between predictions and actual financial metrics

### Summary Statistics
- Mean, median, standard deviation of q-ratios
- Comparison with academic literature benchmarks
- Correlation coefficients with real financial data

## Project Structure

```
financial-RAG/
├── README.md                    # This file
├── Retrieval_Code/             # Main application code
│   ├── main.py                 # Main execution pipeline
│   ├── retriever.py            # Core RAG retrieval logic
│   ├── retriever_hpc.py        # HPC version of retriever
│   ├── pinecone_client.py      # Vector database interface
│   ├── llm_client.py           # OpenAI API integration
│   ├── llm_client_hpc.py       # HPC version of LLM client
│   ├── models.py               # Pydantic data models
│   ├── config.py               # Environment configuration
│   ├── data_loader.py          # Data loading utilities
│   ├── prompt_builder.py       # LLM prompt templates
│   ├── plotting.py             # Visualization functions
│   ├── test.py                 # Testing utilities
│   ├── SFT.py                  # Supervised fine-tuning
│   ├── RFT.py                  # Reinforcement fine-tuning
│   ├── requirements.txt        # Python dependencies
│   ├── SFT_files/              # Fine-tuning data
│   └── RFT_files/              # Reinforcement learning data
├── UpdatesNReports/            # Development progress reports
│   ├── May_05/                 # Progress reports by date
│   ├── Jun_16/                 # Latest improvements
│   └── ...
├── Pinecone_Retrieval.ipynb    # Jupyter notebook for exploration
└── .gitignore
```

## Academic Background

The system is grounded in academic finance literature on Tobin's q:
- **Mean**: ~1.11 (market values typically exceed replacement costs)
- **Median**: ~0.57 (right-skewed distribution)
- **Standard Deviation**: ~1.91 (high variability across firms)
- **Skewness**: ~3.76 (long right tail of high-q firms)

These benchmarks guide the LLM's project valuation and ensure realistic predictions.

## Fine-tuning and Evaluation

The repository includes fine-tuning capabilities:
- `SFT.py`: Supervised fine-tuning scripts for training custom models
- `RFT.py`: Reinforcement fine-tuning from academic feedback  
- `SFT_files/`, `RFT_files/`: Training data and model checkpoints
- Model evaluation against real financial outcomes with correlation analysis

## Development and Research

This project follows an iterative research approach documented in `UpdatesNReports/`:
- **Jun_16**: Latest improvements including reranker integration and q-ratio optimization
- **May-June 2024**: Progressive development from basic RAG to sophisticated financial analysis
- Each report contains performance metrics, correlation analysis, and next steps

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**: Ensure all API keys are set in your `.env` file
   ```bash
   python -c "import config; print('Config loaded successfully')"
   ```

2. **Pinecone Index Setup**: The system expects specific namespaces in your Pinecone index:
   - Verify your index is named "finance-rag" 
   - Check that all required namespaces exist with data

3. **Dropbox Access**: Financial data is stored in Dropbox, ensure credentials are valid:
   - App key, secret, and refresh token must be current
   - Test with: `python -c "from data_loader import load_sample; load_sample().head()"`

4. **OpenAI API**: Uses advanced models including reasoning capabilities:
   - Requires access to `gpt-4o-mini` and `o3-mini` models
   - Fine-tuned model: `ft:o4-mini-2025-04-16:ragresearchteam::BrdcYDoD:ckpt-step-10`

### Performance Characteristics

Based on recent evaluation runs:
- **Correlation with actual q-ratios**: ~0.5-0.6 (strong for financial predictions)
- **Processing time**: ~30-60 seconds per company analysis
- **q-ratio distribution**: Mean≈1.3, closely matches academic literature
- **Sample sizes**: Tested on 10, 50, and 100 company batches

## Contributing

This project uses iterative development with progress tracking in `UpdatesNReports/`. Key areas for improvement:
- Enhanced reranking strategies (BGE-reranker-v2-m3 currently implemented)
- Additional data source integration (earnings guidance, analyst reports)
- Improved financial metric anchoring and calibration
- Extended evaluation methodologies and backtesting

## License

[Add appropriate license information]

## Citation

If you use this system in academic research, please cite:
[Add citation information when available]