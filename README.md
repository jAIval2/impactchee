# Impact Chee - AI/ML Intern Screening Assignment

An automated machine learning solution for classifying corporate annual reports based on their GHG emissions disclosure level (Scope 1, 2, and 3).

## Project Overview

This project implements a complete pipeline for:
1. **Data Collection**: Scraping annual reports from annualreports.com
2. **Dataset Creation**: Extracting and labeling text excerpts based on Scope reporting
3. **Model Training**: Training a BERT-based classifier to predict disclosure levels

## Project Structure

```
impactchee/
├── scraper_script.py          # Web scraper for annual reports
├── create_dataset.py          # Dataset creation and labeling
├── training_script.py         # ML model training
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── dataset.csv               # Training dataset (50+ labeled excerpts)
├── data/
│   ├── pdfs/                 # Downloaded PDF reports
│   ├── texts/                # Extracted text files
│   └── pdf_metadata.csv      # Metadata for downloaded reports
└── model/                    # Trained model (created after training)
```

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd impactchee
```

2. Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Workflow

### Step 1: Scrape Annual Reports

```bash
python scraper_script.py
```

This script:
- Fetches companies from annualreports.com
- Downloads PDF annual reports (2020-2025)
- Extracts text from PDFs
- Saves metadata to `data/pdf_metadata.csv`

**Output**: PDF files in `data/pdfs/` and text files in `data/texts/`

### Step 2: Create Labeled Dataset

```bash
python create_dataset.py
```

This script:
- Processes extracted text files
- Identifies Scope 1, 2, and 3 mentions
- Labels excerpts based on reporting level
- Creates balanced dataset

**Labeling Logic**:
- **Label 1**: Explicitly reports Scope 1, 2, AND 3 emissions
- **Label 0**: Only reports Scope 1 and/or 2, or mentions Scope 3 as future plan

**Output**: `dataset.csv` with 50+ labeled excerpts

### Step 3: Train ML Model

```bash
python training_script.py --validation validation.csv
```

This script:
- Loads training and validation datasets
- Initializes BERT-based classifier
- Trains model with AdamW optimizer
- Evaluates on validation set
- Saves best model

**Required Arguments**:
- `--validation`: Path to validation CSV file

**Optional Arguments**:
- `--dataset`: Path to training dataset (default: `dataset.csv`)
- `--model_dir`: Directory to save model (default: `./model`)
- `--batch_size`: Batch size for training (default: 16)
- `--epochs`: Number of training epochs (default: 3)
- `--learning_rate`: Learning rate (default: 2e-5)
- `--max_length`: Maximum token length (default: 512)

**Output**: 
- Trained model in `model/` directory
- JSON output with:
  - `files_used_for_training`: Number of unique companies
  - `exchanges_in_dataset`: List of stock exchanges

## Dataset Format

The dataset CSV must have the following columns:

| Column | Type | Description |
|--------|------|-------------|
| company_name | string | Name of the company |
| exchange | string | Stock exchange (NYSE, NASDAQ, LSE, etc.) |
| year | integer | Year of the report (2020-2025) |
| text_excerpt | string | Text excerpt (max 500 chars) |
| label | integer | 0 (Scope 1&2 only) or 1 (Scope 1,2,3) |

## Model Architecture

- **Base Model**: BERT (bert-base-uncased)
- **Task**: Binary classification (2 classes)
- **Optimizer**: AdamW with learning rate warmup
- **Loss Function**: Cross-entropy loss
- **Metrics**: Accuracy, Precision, Recall, F1-score

## Key Features

✅ Automated web scraping with error handling
✅ Intelligent text extraction from PDFs
✅ Sophisticated scope detection with regex patterns
✅ Balanced dataset creation
✅ BERT-based deep learning model
✅ Comprehensive evaluation metrics
✅ Model persistence and checkpointing
✅ Command-line interface with argparse

## Dependencies

See `requirements.txt` for complete list. Key packages:
- `transformers`: BERT model and tokenizer
- `torch`: Deep learning framework
- `pandas`: Data manipulation
- `scikit-learn`: Metrics and evaluation
- `pdfplumber`: PDF text extraction
- `beautifulsoup4`: HTML parsing

## Troubleshooting

**No companies found during scraping**:
- Website structure may have changed
- Check internet connection
- Fallback companies are used automatically

**No Scope 3 mentions in dataset**:
- Companies may not report Scope 3
- Try scraping different companies
- Manually verify labels in dataset.csv

**CUDA out of memory**:
- Reduce `--batch_size` (e.g., 8 instead of 16)
- Reduce `--max_length` (e.g., 256 instead of 512)

## Evaluation

The model is evaluated on the validation set using:
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1-score**: Harmonic mean of precision and recall

## Notes

- The scraper respects rate limiting with 1-2 second delays between requests
- Text extraction is limited to first 50 pages of each PDF
- Excerpts are capped at 500 characters as per requirements
- Model uses linear learning rate warmup for stable training
