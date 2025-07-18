import pandas as pd
import json
from typing import Dict, List

def load_mutation_database():
    """Load curated mutation database"""
    # This would typically load from a CSV or database
    # For now, return structured data
    return {
        'point_mutations': [
            {
                'mutation': 'L858R',
                'exon': 21,
                'frequency': 0.45,
                'clinical_significance': 'Pathogenic',
                'drug_response': 'Sensitive to 1st/2nd gen TKIs'
            },
            {
                'mutation': 'T790M',
                'exon': 20,
                'frequency': 0.50,  # of resistance cases
                'clinical_significance': 'Resistance',
                'drug_response': 'Requires 3rd gen TKIs'
            }
        ],
        'structural_variants': [
            {
                'type': 'Exon 19 deletion',
                'frequency': 0.45,
                'clinical_significance': 'Pathogenic',
                'drug_response': 'Highly sensitive to TKIs'
            },
            {
                'type': 'Exon 20 insertion',
                'frequency': 0.10,
                'clinical_significance': 'Resistance',
                'drug_response': 'Poor response to standard TKIs'
            }
        ]
    }

def load_drug_database():
    """Load drug response database"""
    return {
        'TKI_1st_gen': {
            'drugs': ['Gefitinib', 'Erlotinib'],
            'mechanism': 'Reversible EGFR inhibition',
            'approval_year': 2003,
            'common_resistance': ['T790M', 'MET amplification']
        },
        'TKI_2nd_gen': {
            'drugs': ['Afatinib', 'Dacomitinib'],
            'mechanism': 'Irreversible pan-HER inhibition',
            'approval_year': 2013,
            'common_resistance': ['T790M', 'C797S']
        },
        'TKI_3rd_gen': {
            'drugs': ['Osimertinib'],
            'mechanism': 'Selective T790M inhibition',
            'approval_year': 2015,
            'common_resistance': ['C797S', 'Amplification']
        }
    }

def load_clinical_trials_data():
    """Load relevant clinical trials data"""
    return [
        {
            'trial': 'FLAURA',
            'drug': 'Osimertinib',
            'population': 'EGFR+ NSCLC',
            'primary_endpoint': 'PFS',
            'result': '18.9 months vs 10.2 months'
        },
        {
            'trial': 'LUX-Lung 3',
            'drug': 'Afatinib',
            'population': 'EGFR+ NSCLC',
            'primary_endpoint': 'PFS',
            'result': '11.1 months vs 6.9 months'
        }
    ]
