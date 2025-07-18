import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import base64
from io import BytesIO
import json

# Set page config
st.set_page_config(
    page_title="EGFR Mutation Resistance Predictor",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .mutation-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .resistance-high {
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left-color: #f44336;
    }
    .resistance-medium {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        border-left-color: #ff9800;
    }
    .resistance-low {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border-left-color: #4caf50;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .drug-recommendation {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4169e1;
        margin: 0.5rem 0;
    }
    .pathway-affected {
        background: #fff5f5;
        color: #c53030;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: bold;
        margin: 0.25rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'mutations' not in st.session_state:
    st.session_state.mutations = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []

class EGFRAnalyzer:
    """Main analysis engine for EGFR mutations"""
    
    def __init__(self):
        self.mutation_database = {
            'L858R': {
                'type': 'activating',
                'mechanism': 'Structural gain-of-function in kinase domain',
                'pathway_impact': 'Constitutive kinase activation',
                'resistance_profile': 'Sensitive to 1st/2nd gen TKIs, resistant to 3rd gen initially',
                'clinical_significance': 'Most common EGFR mutation in NSCLC (40-45% of EGFR+ cases)',
                'affected_pathways': ['MAPK/ERK', 'PI3K/AKT'],
                'resistance_score': 0.3,
                'frequency': 0.45
            },
            'T790M': {
                'type': 'resistance',
                'mechanism': 'Gatekeeper mutation increasing ATP affinity',
                'pathway_impact': 'Reduced TKI binding affinity, maintained kinase activity',
                'resistance_profile': 'Resistant to 1st/2nd gen TKIs, sensitive to 3rd gen (osimertinib)',
                'clinical_significance': 'Primary acquired resistance mechanism (50-60% of resistance cases)',
                'affected_pathways': ['MAPK/ERK', 'PI3K/AKT'],
                'resistance_score': 0.8,
                'frequency': 0.50
            },
            'Del19': {
                'type': 'activating',
                'mechanism': 'In-frame deletion causing conformational change',
                'pathway_impact': 'Constitutive kinase activation with high sensitivity',
                'resistance_profile': 'Highly sensitive to 1st/2nd gen TKIs',
                'clinical_significance': 'Most common EGFR mutation (45-50% of EGFR+ cases)',
                'affected_pathways': ['MAPK/ERK', 'PI3K/AKT'],
                'resistance_score': 0.2,
                'frequency': 0.45
            },
            'G719X': {
                'type': 'activating',
                'mechanism': 'Point mutation in ATP-binding domain',
                'pathway_impact': 'Moderate kinase activation',
                'resistance_profile': 'Variable response to TKIs, often requires combination therapy',
                'clinical_significance': 'Uncommon mutation (2-3% of EGFR mutations)',
                'affected_pathways': ['MAPK/ERK'],
                'resistance_score': 0.4,
                'frequency': 0.03
            },
            'Exon 20 ins': {
                'type': 'resistance',
                'mechanism': 'Insertion disrupting drug binding pocket',
                'pathway_impact': 'Altered kinase domain structure',
                'resistance_profile': 'Resistant to 1st/2nd gen TKIs, limited response to newer agents',
                'clinical_significance': 'Exon 20 insertions represent 4-10% of EGFR mutations',
                'affected_pathways': ['MAPK/ERK', 'PI3K/AKT'],
                'resistance_score': 0.75,
                'frequency': 0.08
            }
        }
        
        self.drug_database = {
            '1st Generation TKI': {
                'drugs': ['Gefitinib', 'Erlotinib'],
                'mechanism': 'Reversible EGFR kinase inhibition',
                'effective_against': ['L858R', 'Del19', 'G719X'],
                'resistant_mutations': ['T790M', 'Exon 20 ins'],
                'approval_year': 2003
            },
            '2nd Generation TKI': {
                'drugs': ['Afatinib', 'Dacomitinib'],
                'mechanism': 'Irreversible pan-HER inhibition',
                'effective_against': ['L858R', 'Del19', 'G719X'],
                'resistant_mutations': ['T790M'],
                'approval_year': 2013
            },
            '3rd Generation TKI': {
                'drugs': ['Osimertinib'],
                'mechanism': 'Selective T790M-mutant EGFR inhibition',
                'effective_against': ['T790M', 'L858R+T790M', 'Del19+T790M'],
                'resistant_mutations': ['C797S', 'Amplification'],
                'approval_year': 2015
            },
            'Monoclonal Antibody': {
                'drugs': ['Cetuximab', 'Panitumumab'],
                'mechanism': 'EGFR extracellular domain blocking',
                'effective_against': ['Amplification', 'Overexpression'],
                'resistant_mutations': ['KRAS mutations'],
                'approval_year': 2004
            }
        }
    
    def analyze_mutation(self, mutation_type, mutation_detail, exon):
        """Analyze a single mutation"""
        if mutation_detail in self.mutation_database:
            base_analysis = self.mutation_database[mutation_detail].copy()
        elif mutation_type == "Amplification":
            base_analysis = self._analyze_amplification(mutation_detail)
        else:
            base_analysis = self._analyze_unknown(mutation_type, mutation_detail)
        
        # Generate drug recommendations
        drug_recommendations = self._generate_drug_recommendations(mutation_detail, base_analysis)
        
        return {
            'mutation': {
                'type': mutation_type,
                'detail': mutation_detail,
                'exon': exon
            },
            'analysis': {
                **base_analysis,
                'drug_recommendations': drug_recommendations
            }
        }
    
    def _analyze_amplification(self, copy_number):
        """Analyze gene amplification"""
        try:
            copy_num = int(copy_number)
        except:
            copy_num = 6
        
        resistance_score = min(0.7, 0.3 + (copy_num - 2) * 0.05)
        
        return {
            'type': 'amplification',
            'mechanism': f'Gene amplification leading to {copy_num}x overexpression',
            'pathway_impact': 'Ligand-hypersensitive receptor overexpression',
            'resistance_profile': f'High protein levels may require increased drug dosing or combination therapy',
            'clinical_significance': f'{copy_num}x amplification - significant therapeutic challenge',
            'affected_pathways': ['MAPK/ERK', 'PI3K/AKT', 'JAK/STAT'],
            'resistance_score': resistance_score,
            'frequency': 0.15
        }
    
    def _analyze_unknown(self, mutation_type, mutation_detail):
        """Handle unknown mutations"""
        return {
            'type': 'unknown',
            'mechanism': f'Unknown mechanism for {mutation_type}: {mutation_detail}',
            'pathway_impact': 'Requires functional characterization',
            'resistance_profile': 'Unknown - requires experimental validation',
            'clinical_significance': 'Novel or rare mutation requiring further study',
            'affected_pathways': ['Unknown'],
            'resistance_score': 0.5,
            'frequency': 0.01
        }
    
    def _generate_drug_recommendations(self, mutation_detail, analysis):
        """Generate drug recommendations"""
        recommendations = []
        
        for drug_class, info in self.drug_database.items():
            for drug in info['drugs']:
                efficacy = self._calculate_efficacy(mutation_detail, drug_class, analysis)
                if efficacy != "None":
                    recommendations.append({
                        'name': drug,
                        'class': drug_class,
                        'efficacy': efficacy,
                        'mechanism': info['mechanism'],
                        'rationale': self._get_rationale(mutation_detail, drug, analysis)
                    })
        
        return recommendations
    
    def _calculate_efficacy(self, mutation_detail, drug_class, analysis):
        """Calculate drug efficacy"""
        drug_info = self.drug_database[drug_class]
        
        if any(mutation_detail in effective for effective in drug_info['effective_against']):
            if analysis['resistance_score'] < 0.3:
                return "High"
            elif analysis['resistance_score'] < 0.6:
                return "Medium"
            else:
                return "Low"
        
        if any(mutation_detail in resistant for resistant in drug_info['resistant_mutations']):
            return "Low"
        
        if mutation_detail.isdigit() and drug_class == 'Monoclonal Antibody':
            return "High" if int(mutation_detail) >= 4 else "Medium"
        
        return "Medium"
    
    def _get_rationale(self, mutation_detail, drug, analysis):
        """Get rationale for drug recommendation"""
        if analysis['type'] == 'activating':
            return f"Activating mutation typically responsive to kinase inhibition"
        elif analysis['type'] == 'resistance':
            return f"Resistance mutation requiring specialized targeting approach"
        elif analysis['type'] == 'amplification':
            return f"Overexpression benefits from receptor blocking or high-dose TKI"
        else:
            return f"General EGFR targeting approach recommended"

def create_pathway_visualization(results):
    """Create pathway visualization"""
    # Define pathway nodes
    nodes = {
        'EGFR': {'x': 0, 'y': 0, 'size': 40},
        'RAS': {'x': -3, 'y': -2, 'size': 30},
        'RAF': {'x': -3, 'y': -3, 'size': 25},
        'MEK': {'x': -3, 'y': -4, 'size': 25},
        'ERK': {'x': -3, 'y': -5, 'size': 25},
        'PI3K': {'x': 3, 'y': -2, 'size': 30},
        'AKT': {'x': 3, 'y': -3, 'size': 25},
        'mTOR': {'x': 3, 'y': -4, 'size': 25},
        'JAK': {'x': 0, 'y': -2, 'size': 25},
        'STAT': {'x': 0, 'y': -3, 'size': 25},
        'Proliferation': {'x': -1.5, 'y': -6, 'size': 35},
        'Survival': {'x': 1.5, 'y': -6, 'size': 35}
    }
    
    # Determine affected pathways
    affected_pathways = set()
    for result in results:
        affected_pathways.update(result['analysis']['affected_pathways'])
    
    fig = go.Figure()
    
    # Add edges first (so they appear behind nodes)
    edges = [
        ('EGFR', 'RAS'), ('RAS', 'RAF'), ('RAF', 'MEK'), ('MEK', 'ERK'),
        ('EGFR', 'PI3K'), ('PI3K', 'AKT'), ('AKT', 'mTOR'),
        ('EGFR', 'JAK'), ('JAK', 'STAT'),
        ('ERK', 'Proliferation'), ('STAT', 'Proliferation'),
        ('AKT', 'Survival'), ('mTOR', 'Survival')
    ]
    
    for start, end in edges:
        start_node = nodes[start]
        end_node = nodes[end]
        
        fig.add_trace(go.Scatter(
            x=[start_node['x'], end_node['x']],
            y=[start_node['y'], end_node['y']],
            mode='lines',
            line=dict(color='lightgray', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add nodes
    for node_name, node_info in nodes.items():
        is_affected = any(pathway in node_name or node_name in pathway 
                         for pathway in affected_pathways)
        
        color = '#ff4444' if is_affected else '#4169e1'
        size = node_info['size'] + 15 if is_affected else node_info['size']
        
        fig.add_trace(go.Scatter(
            x=[node_info['x']],
            y=[node_info['y']],
            mode='markers+text',
            marker=dict(
                size=size, 
                color=color,
                line=dict(width=2, color='white')
            ),
            text=node_name,
            textposition="middle center",
            textfont=dict(size=10, color='white', family='Arial Black'),
            name=node_name,
            showlegend=False,
            hovertemplate=f"<b>{node_name}</b><br>{'AFFECTED' if is_affected else 'Normal'}<extra></extra>"
        ))
    
    fig.update_layout(
        title={
            'text': "EGFR Signaling Pathway Impact",
            'x': 0.5,
            'font': {'size': 18, 'color': '#2c3e50'}
        },
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4, 4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-7, 1]),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=500,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def create_resistance_chart(results):
    """Create resistance scoring chart"""
    if not results:
        return go.Figure()
    
    mutations = [f"{r['mutation']['detail']}" for r in results]
    scores = [r['analysis']['resistance_score'] for r in results]
    colors = ['#d32f2f' if s > 0.7 else '#f57c00' if s > 0.4 else '#388e3c' for s in scores]
    
    fig = go.Figure(data=go.Bar(
        x=mutations,
        y=scores,
        marker_color=colors,
        text=[f"{s:.2f}" for s in scores],
        textposition='auto',
        hovertemplate="<b>%{x}</b><br>Resistance Score: %{y:.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        title={
            'text': "Resistance Score by Mutation",
            'x': 0.5,
            'font': {'size': 16, 'color': '#2c3e50'}
        },
        xaxis_title="Mutations",
        yaxis_title="Resistance Score (0-1)",
        yaxis=dict(range=[0, 1]),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400
    )
    
    # Add threshold lines
    fig.add_hline(y=0.7, line_dash="dash", line_color="red", 
                  annotation_text="High Resistance", annotation_position="top right")
    fig.add_hline(y=0.4, line_dash="dash", line_color="orange", 
                  annotation_text="Medium Resistance", annotation_position="top right")
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">🧬 EGFR Mutation Resistance Predictor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">A clinically-inspired bioinformatics tool for modeling EGFR-driven resistance in NSCLC</p>', unsafe_allow_html=True)
    
    # Initialize analyzer
    analyzer = EGFRAnalyzer()
    
    # Sidebar
    with st.sidebar:
        st.header("🔬 Analysis Configuration")
        
        analysis_mode = st.selectbox(
            "Analysis Mode",
            ["Clinical Prediction", "Research Mode", "Educational Demo"],
            help="Choose the analysis focus"
        )
        
        st.header("📊 Input Options")
        input_method = st.radio(
            "Input Method:",
            ["Manual Entry", "Example Cases", "File Upload"]
        )
        
        if st.button("🔄 Clear All Data", type="secondary"):
            st.session_state.mutations = []
            st.session_state.analysis_results = []
            st.rerun()
        
        # Display current mutations
        if st.session_state.mutations:
            st.header("📝 Current Mutations")
            for i, mut in enumerate(st.session_state.mutations):
                st.write(f"{i+1}. **{mut['detail']}** ({mut['type']})")
    
    # Main content
    if input_method == "Manual Entry":
        manual_entry_interface(analyzer)
    elif input_method == "Example Cases":
        example_cases_interface(analyzer)
    else:
        file_upload_interface(analyzer)
    
    # Analysis Results
    if st.session_state.analysis_results:
        display_analysis_results()

def manual_entry_interface(analyzer):
    """Manual mutation entry interface"""
    st.markdown('<h2 class="section-header">📝 Manual Mutation Entry</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("mutation_form", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                mutation_type = st.selectbox(
                    "Mutation Type",
                    ["Point Mutation", "Deletion", "Insertion", "Amplification", "Duplication"],
                    help="Select the type of genetic alteration"
                )
            
            with col_b:
                if mutation_type == "Point Mutation":
                    mutation_detail = st.selectbox(
                        "Specific Mutation",
                        ["L858R", "T790M", "G719X", "Other"],
                        help="Common EGFR point mutations"
                    )
                    if mutation_detail == "Other":
                        mutation_detail = st.text_input("Enter mutation:")
                elif mutation_type == "Deletion":
                    mutation_detail = st.selectbox(
                        "Deletion Type",
                        ["Del19", "Other deletion"],
                        help="Common EGFR deletions"
                    )
                elif mutation_type == "Insertion":
                    mutation_detail = st.selectbox(
                        "Insertion Type",
                        ["Exon 20 ins", "Other insertion"],
                        help="Common EGFR insertions"
                    )
                elif mutation_type == "Amplification":
                    mutation_detail = st.number_input(
                        "Copy Number", 
                        min_value=2, 
                        max_value=20, 
                        value=6,
                        help="Number of gene copies"
                    )
                else:
                    mutation_detail = st.text_input("Mutation Detail:")
            
            with col_c:
                exon = st.selectbox(
                    "Exon/Location",
                    ["Exon 18", "Exon 19", "Exon 20", "Exon 21", "Whole Gene", "Other"],
                    help="Genomic location of the mutation"
                )
            
            submitted = st.form_submit_button("➕ Add Mutation", type="primary")
            
            if submitted and mutation_detail:
                new_mutation = {
                    'type': mutation_type,
                    'detail': str(mutation_detail),
                    'exon': exon,
                    'timestamp': datetime.now()
                }
                st.session_state.mutations.append(new_mutation)
                
                # Analyze the mutation
                result = analyzer.analyze_mutation(mutation_type, str(mutation_detail), exon)
                st.session_state.analysis_results.append(result)
                
                st.success(f"✅ Added {mutation_type}: {mutation_detail}")
                st.rerun()
    
    with col2:
        st.info("""
        **💡 Quick Guide:**
        
        **Common Mutations:**
        - **L858R**: Most common activating mutation
        - **Del19**: Highly TKI-sensitive
        - **T790M**: Resistance mutation
        - **Exon 20 ins**: TKI-resistant
        
        **Amplification:**
        - Copy number ≥4 is significant
        - Higher copies = more resistance
        """)

def example_cases_interface(analyzer):
    """Example cases interface"""
    st.markdown('<h2 class="section-header">📚 Example Clinical Cases</h2>', unsafe_allow_html=True)
    
    examples = {
        "🟢 Classic EGFR+ NSCLC (Treatment-Naive)": [
            {'type': 'Point Mutation', 'detail': 'L858R', 'exon': 'Exon 21'},
        ],
        "🟡 Acquired Resistance Case": [
            {'type': 'Point Mutation', 'detail': 'L858R', 'exon': 'Exon 21'},
            {'type': 'Point Mutation', 'detail': 'T790M', 'exon': 'Exon 20'}
        ],
        "🔴 High Amplification Case": [
            {'type': 'Amplification', 'detail': '8', 'exon': 'Whole Gene'}
        ],
        "🟠 Exon 19 Deletion (Highly Sensitive)": [
            {'type': 'Deletion', 'detail': 'Del19', 'exon': 'Exon 19'}
        ],
        "🔴 Resistant Insertion Case": [
            {'type': 'Insertion', 'detail': 'Exon 20 ins', 'exon': 'Exon 20'}
        ],
        "⚫ Complex Multi-Mutation Case": [
            {'type': 'Point Mutation', 'detail': 'G719X', 'exon': 'Exon 18'},
            {'type': 'Amplification', 'detail': '4', 'exon': 'Whole Gene'}
        ]
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_example = st.selectbox(
            "Select Example Case:",
            list(examples.keys()),
            help="Choose a pre-configured clinical scenario"
        )
        
        # Show case details
        case_mutations = examples[selected_example]
        st.write("**Case Details:**")
        for mut in case_mutations:
            st.write(f"• {mut['type']}: {mut['detail']} ({mut['exon']})")
        
        if st.button("🚀 Load Example Case", type="primary"):
            # Clear existing data
            st.session_state.mutations = []
            st.session_state.analysis_results = []
            
            # Add new mutations
            for mut in case_mutations:
                mut['timestamp'] = datetime.now()
                st.session_state.mutations.append(mut)
                
                # Analyze mutation
                result = analyzer.analyze_mutation(mut['type'], mut['detail'], mut['exon'])
                st.session_state.analysis_results.append(result)
            
            st.success(f"✅ Loaded: {selected_example}")
            st.rerun()
    
    with col2:
        st.info("""
        **🎯 Case Descriptions:**
        
        **🟢 Classic EGFR+**: Standard activating mutation, excellent TKI response expected
        
        **🟡 Acquired Resistance**: T790M develops after initial TKI treatment
        
        **🔴 High Amplification**: Overexpression requiring combination therapy
        
        **🟠 Del19**: Most TKI-sensitive mutation type
        
        **🔴 Exon 20 Insertion**: Intrinsically TKI-resistant
        
        **⚫ Complex Case**: Multiple alterations requiring personalized approach
        """)

def file_upload_interface(analyzer):
    """File upload interface"""
    st.markdown('<h2 class="section-header">📁 File Upload</h2>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload mutation data file",
        type=['csv', 'txt', 'vcf'],
        help="Supported formats: CSV, TXT, VCF"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                st.write("**File Preview:**")
                st.dataframe(df.head())
                
                if st.button("Process CSV File"):
                    st.session_state.mutations = []
                    st.session_state.analysis_results = []
                    
                    for _, row in df.iterrows():
                        mutation = {
                            'type': row.get('type', 'Point Mutation'),
                            'detail': str(row.get('mutation', row.get('detail', ''))),
                            'exon': row.get('exon', 'Unknown'),
                            'timestamp': datetime.now()
                        }
                        st.session_state.mutations.append(mutation)
                        
                        result = analyzer.analyze_mutation(
                            mutation['type'], 
                            mutation['detail'], 
                            mutation['exon']
                        )
                        st.session_state.analysis_results.append(result)
                    
                    st.success(f"✅ Processed {len(df)} mutations from CSV")
                    st.rerun()
            
            else:
                content = str(uploaded_file.read(), "utf-8")
                st.text_area("File Content:", content, height=200)
                st.info("Manual parsing required for this file format")
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")

def display_analysis_results():
    """Display comprehensive analysis results"""
    st.markdown('<h2 class="section-header">🔬 Analysis Results</h2>', unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_mutations = len(st.session_state.analysis_results)
    avg_resistance = np.mean([r['analysis']['resistance_score'] for r in st.session_state.analysis_results])
    high_resistance_count = sum(1 for r in st.session_state.analysis_results if r['analysis']['resistance_score'] > 0.7)
    
    with col1:
        st.metric("Total Mutations", total_mutations)
    with col2:
        st.metric("Avg Resistance Score", f"{avg_resistance:.2f}")
    with col3:
        st.metric("High Resistance Cases", high_resistance_count)
    with col4:
        risk_level = "🔴 High" if avg_resistance > 0.6 else "🟡 Medium" if avg_resistance > 0.3 else "🟢 Low"
        st.metric("Overall Risk", risk_level)
    
    # Detailed mutation analysis
    st.markdown("### 🧬 Detailed Mutation Analysis")
    
    for i, result in enumerate(st.session_state.analysis_results):
        mutation = result['mutation']
        analysis = result['analysis']
        
        # Determine card styling based on resistance
        resistance_score = analysis['resistance_score']
        if resistance_score > 0.7:
            card_class = "mutation-card resistance-high"
            risk_emoji = "🔴"
        elif resistance_score > 0.4:
            card_class = "mutation-card resistance-medium"
            risk_emoji = "🟡"
        else:
            card_class = "mutation-card resistance-low"
            risk_emoji = "🟢"
        
        st.markdown(f"""
        <div class="{card_class}">
            <h4>{risk_emoji} {mutation['type']}: {mutation['detail']} ({mutation['exon']})</h4>
            <p><strong>🔬 Mechanism:</strong> {analysis['mechanism']}</p>
            <p><strong>📊 Resistance Score:</strong> {resistance_score:.2f}/1.0</p>
            <p><strong>🎯 Clinical Significance:</strong> {analysis['clinical_significance']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable detailed analysis
        with st.expander(f"🔍 Detailed Analysis - {mutation['detail']}", expanded=False):
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("**🧪 Molecular Details:**")
                st.write(f"• **Type:** {analysis['type'].title()}")
                st.write(f"• **Pathway Impact:** {analysis['pathway_impact']}")
                st.write(f"• **Resistance Profile:** {analysis['resistance_profile']}")
                
                st.write("**🛤️ Affected Pathways:**")
                for pathway in analysis['affected_pathways']:
                    st.markdown(f'<span class="pathway-affected">{pathway}</span>', unsafe_allow_html=True)
            
            with col_b:
                st.write("**💊 Drug Recommendations:**")
                for drug in analysis['drug_recommendations']:
                    efficacy_color = "🟢" if drug['efficacy'] == "High" else "🟡" if drug['efficacy'] == "Medium" else "🔴"
                    st.markdown(f"""
                    <div class="drug-recommendation">
                        <strong>{efficacy_color} {drug['name']}</strong> ({drug['class']})<br>
                        <em>Efficacy: {drug['efficacy']}</em><br>
                        <small>{drug['rationale']}</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Visualizations
    st.markdown("### 📈 Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pathway visualization
        pathway_fig = create_pathway_visualization(st.session_state.analysis_results)
        st.plotly_chart(pathway_fig, use_container_width=True)
    
    with col2:
        # Resistance chart
        resistance_fig = create_resistance_chart(st.session_state.analysis_results)
        st.plotly_chart(resistance_fig, use_container_width=True)
    
    # Treatment recommendations summary
    st.markdown("### 💊 Treatment Recommendations Summary")
    
    # Aggregate all drug recommendations
    all_drugs = []
    for result in st.session_state.analysis_results:
        all_drugs.extend(result['analysis']['drug_recommendations'])
    
    if all_drugs:
        # Create drug efficacy summary
        drug_summary = {}
        for drug in all_drugs:
            key = f"{drug['name']} ({drug['class']})"
            if key not in drug_summary:
                drug_summary[key] = {'high': 0, 'medium': 0, 'low': 0, 'total': 0}
            drug_summary[key][drug['efficacy'].lower()] += 1
            drug_summary[key]['total'] += 1
        
        # Display as table
        summary_data = []
        for drug, counts in drug_summary.items():
            summary_data.append({
                'Drug': drug,
                'High Efficacy': counts['high'],
                'Medium Efficacy': counts['medium'],
                'Low Efficacy': counts['low'],
                'Total Recommendations': counts['total']
            })
        
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, use_container_width=True)
    
    # Export options
    st.markdown("### 📄 Export Options")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Results CSV"):
            # Create CSV data
            csv_data = []
            for result in st.session_state.analysis_results:
                csv_data.append({
                    'Mutation_Type': result['mutation']['type'],
                    'Mutation_Detail': result['mutation']['detail'],
                    'Exon': result['mutation']['exon'],
                    'Resistance_Score': result['analysis']['resistance_score'],
                    'Mechanism': result['analysis']['mechanism'],
                    'Clinical_Significance': result['analysis']['clinical_significance']
                })
            
            df_export = pd.DataFrame(csv_data)
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"egfr_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Copy Summary"):
            summary_text = f"EGFR Analysis Summary ({datetime.now().strftime('%Y-%m-%d')})\n"
            summary_text += f"Total Mutations: {total_mutations}\n"
            summary_text += f"Average Resistance Score: {avg_resistance:.2f}\n"
            summary_text += f"High Resistance Cases: {high_resistance_count}\n\n"
            
            for result in st.session_state.analysis_results:
                mutation = result['mutation']
                analysis = result['analysis']
                summary_text += f"{mutation['detail']}: {analysis['resistance_score']:.2f} resistance score\n"
            
            st.code(summary_text)
    
    with col3:
        st.info("📄 PDF Report generation available in full version")

if __name__ == "__main__":
    main()
