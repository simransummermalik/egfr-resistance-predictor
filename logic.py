import pandas as pd
import numpy as np
from typing import Dict, List, Any
import json

class MutationClassifier:
    """Classifies EGFR mutations based on structural and functional impact"""
    
    def __init__(self):
        self.mutation_database = self._load_mutation_knowledge()
    
    def _load_mutation_knowledge(self):
        """Load curated mutation knowledge base"""
        return {
            # Point mutations
            'L858R': {
                'type': 'activating',
                'mechanism': 'Structural gain-of-function',
                'pathway_impact': 'Constitutive kinase activation',
                'resistance_profile': 'Sensitive to 1st/2nd gen TKIs, resistant to 3rd gen',
                'clinical_significance': 'Most common EGFR mutation in NSCLC (40-45%)',
                'affected_pathways': ['MAPK/ERK', 'PI3K/AKT'],
                'resistance_score': 0.3
            },
            'T790M': {
                'type': 'resistance',
                'mechanism': 'Gatekeeper mutation',
                'pathway_impact': 'Increased ATP affinity, reduced TKI binding',
                'resistance_profile': 'Resistant to 1st/2nd gen TKIs, sensitive to 3rd gen (osimertinib)',
                'clinical_significance': 'Primary resistance mechanism (50-60% of acquired resistance)',
                'affected_pathways': ['MAPK/ERK', 'PI3K/AKT'],
                'resistance_score': 0.8
            },
            'G719X': {
                'type': 'activating',
                'mechanism': 'Structural alteration in ATP-binding domain',
                'pathway_impact': 'Moderate kinase activation',
                'resistance_profile': 'Variable response to TKIs',
                'clinical_significance': 'Uncommon mutation (2-3% of EGFR mutations)',
                'affected_pathways': ['MAPK/ERK'],
                'resistance_score': 0.4
            },
            'Del19': {
                'type': 'activating',
                'mechanism': 'In-frame deletion causing conformational change',
                'pathway_impact': 'Constitutive kinase activation',
                'resistance_profile': 'Highly sensitive to 1st/2nd gen TKIs',
                'clinical_significance': 'Most common EGFR mutation (45-50%)',
                'affected_pathways': ['MAPK/ERK', 'PI3K/AKT'],
                'resistance_score': 0.2
            }
        }
    
    def classify_mutation(self, mutation_type: str, mutation_detail: str) -> Dict[str, Any]:
        """Classify a single mutation"""
        if mutation_type == "Point Mutation" and mutation_detail in self.mutation_database:
            return self.mutation_database[mutation_detail]
        elif mutation_type == "Amplification":
            return self._classify_amplification(mutation_detail)
        elif mutation_type == "Insertion":
            return self._classify_insertion(mutation_detail)
        elif mutation_type == "Deletion":
            return self._classify_deletion(mutation_detail)
        else:
            return self._classify_unknown(mutation_type, mutation_detail)
    
    def _classify_amplification(self, copy_number):
        """Classify gene amplification"""
        copy_num = int(copy_number) if isinstance(copy_number, (int, float, str)) else 6
        
        if copy_num >= 6:
            resistance_score = min(0.7, 0.3 + (copy_num - 2) * 0.1)
        else:
            resistance_score = 0.3 + (copy_num - 2) * 0.05
        
        return {
            'type': 'amplification',
            'mechanism': 'Copy number amplification leading to overexpression',
            'pathway_impact': 'Ligand-hypersensitive overexpression',
            'resistance_profile': f'High protein levels may require increased drug dosing',
            'clinical_significance': f'{copy_num}x amplification - significant overexpression',
            'affected_pathways': ['MAPK/ERK', 'PI3K/AKT', 'JAK/STAT'],
            'resistance_score': resistance_score
        }
    
    def _classify_insertion(self, insertion_detail):
        """Classify insertion mutations"""
        if "Exon 20" in insertion_detail:
            return {
                'type': 'resistance',
                'mechanism': 'Exon 20 insertion disrupting drug binding',
                'pathway_impact': 'Altered kinase domain structure',
                'resistance_profile': 'Resistant to 1st/2nd gen TKIs, variable response to newer agents',
                'clinical_significance': 'Exon 20 insertions represent 4-10% of EGFR mutations',
                'affected_pathways': ['MAPK/ERK', 'PI3K/AKT'],
                'resistance_score': 0.75
            }
        else:
            return self._classify_unknown("Insertion", insertion_detail)
    
    def _classify_deletion(self, deletion_detail):
        """Classify deletion mutations"""
        if "Del19" in deletion_detail or "Exon 19" in deletion_detail:
            return self.mutation_database['Del19']
        else:
            return {
                'type': 'structural',
                'mechanism': 'In-frame deletion causing structural alteration',
                'pathway_impact': 'Variable kinase activation',
                'resistance_profile': 'Variable TKI response depending on specific deletion',
                'clinical_significance': 'Uncommon deletion variant',
                'affected_pathways': ['MAPK/ERK'],
                'resistance_score': 0.4
            }
    
    def _classify_unknown(self, mutation_type, mutation_detail):
        """Handle unknown mutations with general classification"""
        return {
            'type': 'unknown',
            'mechanism': f'Unknown mechanism for {mutation_type}: {mutation_detail}',
            'pathway_impact': 'Requires further characterization',
            'resistance_profile': 'Unknown resistance profile',
            'clinical_significance': 'Novel or rare mutation requiring functional studies',
            'affected_pathways': ['Unknown'],
            'resistance_score': 0.5
        }

class EGFRAnalyzer:
    """Main analysis engine for EGFR mutations"""
    
    def __init__(self):
        self.classifier = MutationClassifier()
        self.drug_database = self._load_drug_database()
    
    def _load_drug_database(self):
        """Load drug response database"""
        return {
            '1st_gen_TKI': {
                'drugs': ['Gefitinib', 'Erlotinib'],
                'mechanism': 'Reversible EGFR kinase inhibition',
                'effective_against': ['L858R', 'Del19', 'G719X'],
                'resistant_mutations': ['T790M', 'Exon 20 ins']
            },
            '2nd_gen_TKI': {
                'drugs': ['Afatinib', 'Dacomitinib'],
                'mechanism': 'Irreversible pan-HER inhibition',
                'effective_against': ['L858R', 'Del19', 'G719X', 'Exon 20 ins (limited)'],
                'resistant_mutations': ['T790M']
            },
            '3rd_gen_TKI': {
                'drugs': ['Osimertinib'],
                'mechanism': 'Selective T790M-mutant EGFR inhibition',
                'effective_against': ['T790M', 'L858R+T790M', 'Del19+T790M'],
                'resistant_mutations': ['C797S', 'Amplification (high level)']
            },
            'Monoclonal_Antibody': {
                'drugs': ['Cetuximab', 'Panitumumab'],
                'mechanism': 'EGFR extracellular domain blocking',
                'effective_against': ['Amplification', 'Overexpression'],
                'resistant_mutations': ['KRAS mutations', 'Downstream pathway activation']
            }
        }
    
    def analyze_mutations(self, mutations: List[Dict]) -> List[Dict]:
        """Analyze a list of mutations"""
        results = []
        
        for mutation in mutations:
            # Classify mutation
            classification = self.classifier.classify_mutation(
                mutation['type'], 
                mutation['detail']
            )
            
            # Generate drug recommendations
            drug_recommendations = self._generate_drug_recommendations(
                mutation, classification
            )
            
            # Create detailed analysis
            detailed_analysis = self._create_detailed_analysis(
                mutation, classification
            )
            
            results.append({
                'mutation': mutation,
                'analysis': {
                    **classification,
                    'drug_recommendations': drug_recommendations,
                    'detailed_mechanism': detailed_analysis['mechanism'],
                    'clinical_significance': detailed_analysis['clinical']
                }
            })
        
        return results
    
    def _generate_drug_recommendations(self, mutation, classification):
        """Generate personalized drug recommendations"""
        recommendations = []
        mutation_detail = str(mutation['detail'])
        
        for drug_class, info in self.drug_database.items():
            for drug in info['drugs']:
                efficacy = self._calculate_drug_efficacy(
                    mutation_detail, drug_class, classification
                )
                
                if efficacy != "None":
                    recommendations.append({
                        'name': drug,
                        'class': drug_class.replace('_', ' ').title(),
                        'efficacy': efficacy,
                        'rationale': self._get_drug_rationale(
                            mutation_detail, drug, classification
                        )
                    })
        
        return recommendations
    
    def _calculate_drug_efficacy(self, mutation_detail, drug_class, classification):
        """Calculate drug efficacy based on mutation profile"""
        drug_info = self.drug_database[drug_class]
        
        # Check if mutation is in effective list
        if any(mutation_detail in effective for effective in drug_info['effective_against']):
            if classification['resistance_score'] < 0.3:
                return "High"
            elif classification['resistance_score'] < 0.6:
                return "Medium"
            else:
                return "Low"
        
        # Check if mutation is in resistant list
        if any(mutation_detail in resistant for resistant in drug_info['resistant_mutations']):
            return "Low"
        
        # Handle amplification specially
        if mutation_detail.isdigit() and drug_class == 'Monoclonal_Antibody':
            return "High" if int(mutation_detail) >= 4 else "Medium"
        
        return "Medium"  # Default for unknown interactions
    
    def _get_drug_rationale(self, mutation_detail, drug, classification):
        """Provide rationale for drug recommendation"""
        if classification['type'] == 'activating':
            return f"Activating mutation responsive to kinase inhibition"
        elif classification['type'] == 'resistance':
            return f"Resistance mutation requiring specialized targeting"
        elif classification['type'] == 'amplification':
            return f"Overexpression may benefit from receptor blocking"
        else:
            return f"General EGFR targeting approach"
    
    def _create_detailed_analysis(self, mutation, classification):
        """Create detailed mechanistic analysis"""
        mechanism_detail = f"""
        {classification['mechanism']}
        
        This mutation affects EGFR function through {classification['pathway_impact'].lower()}.
        The structural changes lead to altered protein conformation and signaling capacity.
        """
        
        clinical_detail = f"""
        {classification['clinical_significance']}
        
        Resistance Score: {classification['resistance_score']:.2f}/1.0
        This score reflects the likelihood of treatment resistance based on known mechanisms.
        """
        
        return {
            'mechanism': mechanism_detail.strip(),
            'clinical': clinical_detail.strip()
        }
