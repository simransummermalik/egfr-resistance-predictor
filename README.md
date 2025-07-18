# EGFR Resistance Predictor

**EGFR Resistance Predictor** is a lightweight, clinically-informed bioinformatics tool that models the impact of mutations and amplifications in the EGFR gene on therapeutic resistance in non-small cell lung cancer (NSCLC). This project aims to bridge biological insight and computational prediction to support precision oncology decisions.

## Overview

This tool allows users to input specific EGFR mutations (e.g., small duplications, insertions, point mutations, and amplifications), and predicts:

- The likely mechanistic consequence (e.g., gain-of-function vs overexpression)
- Downstream signaling pathway activation (e.g., PI3K/AKT, RAS/MAPK)
- Resistance potential to EGFR-targeted therapies (e.g., TKIs)
- Suggested treatment approach (e.g., TKI generation or combination therapy)

The logic is built on curated literature, publicly available cancer mutation knowledge bases (e.g., COSMIC, OncoKB, CIViC), and the Hallmarks of Cancer framework.

## Features

- Accepts EGFR mutation input manually or from file
- Classifies mutation impact (structural vs copy number)
- Predicts signaling pathway behavior and drug resistance
- Recommends a therapeutic strategy based on mutation context
- Built with modular backend logic for extensibility

## Project Structure

```
egfr-resistance-predictor/
├── app.py                     # Streamlit application
├── logic.py                   # Core prediction engine
├── egfr_mutation_impact.csv   # Curated reference mutation dataset
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
```

## Setup Instructions

1. Clone the repository or download the project files:

```bash
git clone https://github.com/your-username/egfr-resistance-predictor.git
cd egfr-resistance-predictor
```

2. (Optional) Create and activate a virtual environment:

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```

4. Run the Streamlit application:

```bash
streamlit run app.py
```

This will open a browser window at `http://localhost:8501/`.

## Example Usage

**Input:**

- Mutation: Exon 20 insertion
- Type: Small duplication
- Copy Number: 1

**Predicted Output:**

- Mechanism: Gain-of-function
- Pathway Activated: PI3K/AKT
- Resistance Level: High
- Therapy Recommendation: Consider 3rd-generation TKIs (e.g., mobocertinib) or antibody-TKI combinations

## Scientific Context

EGFR (epidermal growth factor receptor) mutations are a key driver of tumorigenesis in NSCLC. Structural mutations such as small in-frame duplications may lead to constitutive activation of the receptor, while gene amplifications increase the expression of wild-type EGFR, resulting in hypersensitive ligand-mediated signaling. Both mechanisms can result in resistance to first- or second-generation tyrosine kinase inhibitors (TKIs). This tool models those distinctions and predicts treatment outcomes accordingly.

## References

- Hanahan D, Weinberg RA. (2011). *Hallmarks of Cancer: The Next Generation*. Cell, 144(5), 646–674.
- OncoKB Knowledge Base: https://www.oncokb.org/
- COSMIC: https://cancer.sanger.ac.uk/cosmic
- CIViC: https://civicdb.org/

## IMPORTANT

This tool is intended for research and educational use only. It is not a substitute for clinical decision-making or diagnostic tools.

## Acknowledgments

Developed during the Jackson Laboratory Summer Cancer Genomics Program as a personal project. Inspired by translational research in EGFR-targeted therapy resistance and bioinformatics-driven precision oncology.
