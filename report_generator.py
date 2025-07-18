from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import io
import base64

class PDFReportGenerator:
    """Generates comprehensive PDF reports for EGFR mutation analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#1f77b4')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50')
        ))
    
    def generate_report(self, results, patient_info=None):
        """Generate comprehensive PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("EGFR Mutation Resistance Analysis Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y")
        metadata = f"Generated on: {report_date}"
        story.append(Paragraph(metadata, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        summary = self._generate_executive_summary(results)
        story.append(Paragraph(summary, self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Mutation Analysis
        story.append(Paragraph("Detailed Mutation Analysis", self.styles['SectionHeader']))
        
        for i, result in enumerate(results, 1):
            mutation = result['mutation']
            analysis = result['analysis']
            
            # Mutation header
            mut_header = f"Mutation {i}: {mutation['type']} - {mutation['detail']}"
            story.append(Paragraph(mut_header, self.styles['Heading3']))
            
            # Analysis details
            details = [
                f"<b>Location:</b> {mutation['exon']}",
                f"<b>Mechanism:</b> {analysis['mechanism']}",
                f"<b>Pathway Impact:</b> {analysis['pathway_impact']}",
                f"<b>Resistance Score:</b> {analysis['resistance_score']:.2f}/1.0",
                f"<b>Clinical Significance:</b> {analysis['clinical_significance']}"
            ]
            
            for detail in details:
                story.append(Paragraph(detail, self.styles['Normal']))
            
            story.append(Spacer(1, 12))
        
        # Drug Recommendations
        story.append(Paragraph("Treatment Recommendations", self.styles['SectionHeader']))
        drug_table = self._create_drug_recommendation_table(results)
        story.append(drug_table)
        story.append(Spacer(1, 20))
        
        # Clinical Considerations
        story.append(Paragraph("Clinical Considerations", self.styles['SectionHeader']))
        considerations = self._generate_clinical_considerations(results)
        story.append(Paragraph(considerations, self.styles['Normal']))
        
        # References
        story.append(Spacer(1, 20))
        story.append(Paragraph("References", self.styles['SectionHeader']))
        references = self._get_references()
        for ref in references:
            story.append(Paragraph(ref, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _generate_executive_summary(self, results):
        """Generate executive summary of findings"""
        total_mutations = len(results)
        high_resistance = sum(1 for r in results if r['analysis']['resistance_score'] > 0.7)
        
        summary = f"""
        This report analyzes {total_mutations} EGFR mutation(s) identified in the sample. 
        {high_resistance} mutation(s) show high resistance potential (score > 0.7), indicating 
        potential challenges with standard targeted therapy approaches. The analysis incorporates 
        current clinical knowledge of EGFR mutation mechanisms and drug resistance patterns 
        to provide evidence-based treatment recommendations.
        """
        
        return summary.strip()
    
    def _create_drug_recommendation_table(self, results):
        """Create drug recommendation table"""
        # Collect all drug recommendations
        all_drugs = []
        for result in results:
            for drug in result['analysis']['drug_recommendations']:
                all_drugs.append([
                    drug['name'],
                    drug['class'],
                    drug['efficacy'],
                    drug['rationale'][:50] + "..." if len(drug['rationale']) > 50 else drug['rationale']
                ])
        
        # Create table
        data = [['Drug', 'Class', 'Efficacy', 'Rationale']] + all_drugs
        
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        return table
    
    def _generate_clinical_considerations(self, results):
        """Generate clinical considerations section"""
        considerations = """
        <b>Key Clinical Considerations:</b><br/>
        • Monitor for acquired resistance mechanisms during treatment<br/>
        • Consider combination therapies for high-resistance mutations<br/>
        • Regular imaging and biomarker monitoring recommended<br/>
        • Genetic counseling may be appropriate for hereditary cases<br/>
        • Consider clinical trial enrollment for novel therapeutic approaches<br/><br/>
        
        <b>Limitations:</b><br/>
        This analysis is based on current literature and may not account for all 
        possible resistance mechanisms or novel therapeutic approaches. Clinical 
        correlation and multidisciplinary team discussion are essential for 
        optimal patient management.
        """
        
        return considerations
    
    def _get_references(self):
        """Get relevant scientific references"""
        return [
            "1. Sharma SV, et al. Epidermal growth factor receptor mutations in lung cancer. Nat Rev Cancer. 2007;7(3):169-181.",
            "2. Mok TS, et al. Osimertinib or Platinum-Pemetrexed in EGFR T790M-Positive Lung Cancer. N Engl J Med. 2017;376(7):629-640.",
            "3. Soria JC, et al. Osimertinib in Untreated EGFR-Mutated Advanced Non-Small-Cell Lung Cancer. N Engl J Med. 2018;378(2):113-125.",
            "4. Yun CH, et al. The T790M mutation in EGFR kinase causes drug resistance by increasing the affinity for ATP. Proc Natl Acad Sci USA. 2008;105(6):2070-2075."
        ]
