# Complete Workflow Guide - Impact Chee Assignment

## Project Requirements Summary

### ✅ Must Have
1. **50+ unique companies** from annualreports.com
2. **50+ labeled excerpts** in dataset.csv
3. **Class balance** - both label 0 and label 1
4. **Correct columns**: company_name, exchange, year, text_excerpt, label
5. **Training script** accepts `--validation` argument
6. **JSON output** with files_used_for_training and exchanges_in_dataset

## Step-by-Step Execution

### Step 1: Run the Scraper (scraper_script.py)

```bash
cd /Users/kayan/Developer/impactchee
source venv/bin/activate
python scraper_script.py
```

**What it does:**
- Loads 50+ companies from built-in database
- Downloads PDF annual reports (2020-2025)
- Extracts text from PDFs (first 50 pages)
- Saves to `data/pdfs/` and `data/texts/`
- Creates `data/pdf_metadata.csv`

**Expected output:**
- 50+ PDF files in `data/pdfs/`
- 50+ text files in `data/texts/`
- Metadata CSV with company, exchange, year, paths

**Time estimate:** 15-30 minutes (depends on network and PDF availability)

### Step 2: Create Labeled Dataset (create_dataset.py)

```bash
python create_dataset.py
```

**What it does:**
- Reads text files from `data/texts/`
- Searches for Scope 1, 2, 3 mentions
- Labels excerpts based on reporting level
- Creates balanced dataset

**Labeling logic:**
- **Label 1**: Explicitly reports Scope 3 with actual data
- **Label 0**: Only reports Scope 1&2, or mentions Scope 3 as future plan

**Expected output:**
- `dataset.csv` with 50+ rows
- Mix of label 0 and label 1 (class balance)
- Columns: company_name, exchange, year, text_excerpt, label

**Time estimate:** 1-2 minutes

### Step 3: Train Model (training_script.py)

```bash
python training_script.py --validation validation.csv
```

**What it does:**
- Loads dataset.csv for training
- Loads validation.csv (provided by evaluators)
- Trains BERT classifier
- Evaluates on validation set
- Prints JSON output

**Expected output:**
```json
{
  "files_used_for_training": 50,
  "exchanges_in_dataset": ["NASDAQ", "NYSE"]
}
```

**Time estimate:** 5-15 minutes (depends on dataset size and hardware)

## Troubleshooting

### Issue: Scraper downloads few PDFs

**Cause:** Some company URLs may not have accessible PDFs
**Solution:** 
- Script will continue with available downloads
- Minimum viable: 20+ companies with PDFs is sufficient if they yield 50+ excerpts

### Issue: All labels are 0

**Cause:** Companies may not report Scope 3
**Solution:**
- Manually review some excerpts
- If needed, adjust labeling patterns in create_dataset.py
- Can manually add label 1 examples if found

### Issue: Training fails

**Cause:** Not enough data or missing validation.csv
**Solution:**
- Ensure dataset.csv has at least 20+ rows
- Check validation.csv exists and has correct format
- Reduce batch_size if memory issues

## Verification Checklist

Before submission, verify:

- [ ] `scraper_script.py` runs without errors
- [ ] `data/pdfs/` contains PDF files
- [ ] `data/texts/` contains text files
- [ ] `dataset.csv` exists with 50+ rows
- [ ] `dataset.csv` has both label 0 and label 1
- [ ] `dataset.csv` has correct column names
- [ ] `training_script.py` accepts --validation argument
- [ ] Training outputs JSON to stdout
- [ ] JSON has files_used_for_training and exchanges_in_dataset
- [ ] `requirements.txt` lists all dependencies
- [ ] `README.md` explains approach

## Expected Dataset Structure

```csv
company_name,exchange,year,text_excerpt,label
"Apple Inc.","NASDAQ",2023,"...we report Scope 1, 2, and 3 emissions...",1
"Microsoft Corporation","NASDAQ",2022,"...Scope 1 and Scope 2 emissions only...",0
```

## Submission Package

Create zip file with:
- scraper_script.py
- create_dataset.py
- training_script.py
- dataset.csv
- requirements.txt
- README.md
- (Optional) WORKFLOW.md

## Key Success Metrics

1. **Coverage**: 50+ unique companies ✓
2. **Data Quality**: 50+ labeled excerpts ✓
3. **Class Balance**: Both labels represented ✓
4. **Format**: Correct CSV structure ✓
5. **Automation**: CLI arguments work ✓
6. **Output**: JSON format correct ✓
