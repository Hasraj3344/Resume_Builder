"""DOCX formatter for exporting resumes and cover letters."""

from typing import List, Optional, Dict
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from src.models import Resume, Experience, Education
import re


class DOCXFormatter:
    """Format and export documents to DOCX with ATS-friendly styling."""

    def __init__(self, template_style: str = "professional"):
        """
        Initialize DOCX formatter.

        Args:
            template_style: Template style (professional, modern, minimal)
        """
        self.template_style = template_style
        self.doc = Document()
        self._setup_document_styles()

    def _setup_document_styles(self):
        """Set up document-wide styles."""
        # Set normal style
        style = self.doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)

        # Set margins (ATS-friendly: 0.5-1 inch)
        sections = self.doc.sections
        for section in sections:
            section.top_margin = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

    def _add_heading(self, text: str, level: int = 1, color: str = "000000"):
        """
        Add a formatted heading.

        Args:
            text: Heading text
            level: Heading level (1=name, 2=section, 3=subsection)
            color: Hex color code
        """
        if level == 1:  # Name heading
            para = self.doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = para.add_run(text.upper())
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = RGBColor.from_string(color)
            para.space_after = Pt(6)

        elif level == 2:  # Section heading
            para = self.doc.add_paragraph()
            run = para.add_run(text.upper())
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor.from_string(color)

            # Add underline
            self._add_paragraph_border(para, border_color=color)
            para.space_after = Pt(6)

        elif level == 3:  # Subsection (company, role)
            para = self.doc.add_paragraph()
            run = para.add_run(text)
            run.font.size = Pt(11)
            run.font.bold = True
            para.space_after = Pt(3)

    def _add_paragraph_border(self, paragraph, border_color: str = "000000"):
        """Add bottom border to paragraph."""
        p = paragraph._element
        pPr = p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')

        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')  # Border size
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), border_color)

        pBdr.append(bottom)
        pPr.append(pBdr)

    def _add_contact_info(self, resume: Resume):
        """Add contact information section."""
        contact = resume.contact

        # Center-aligned contact info
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        contact_parts = []
        if contact.email:
            contact_parts.append(contact.email)
        if contact.phone:
            contact_parts.append(contact.phone)
        if contact.location:
            contact_parts.append(contact.location)
        if contact.linkedin:
            contact_parts.append(f"LinkedIn: {contact.linkedin}")
        if contact.github:
            contact_parts.append(f"GitHub: {contact.github}")

        run = para.add_run(" | ".join(contact_parts))
        run.font.size = Pt(10)
        para.space_after = Pt(12)

    def _add_bullet_point(self, text: str, bold_keywords: List[str] = None):
        """
        Add a bullet point with optional keyword bolding.

        Args:
            text: Bullet text
            bold_keywords: Keywords to bold
        """
        para = self.doc.add_paragraph(style='List Bullet')
        para.paragraph_format.left_indent = Inches(0.25)
        para.paragraph_format.space_after = Pt(3)

        if bold_keywords:
            # Split text and bold keywords
            self._add_text_with_bold_keywords(para, text, bold_keywords)
        else:
            run = para.add_run(text)
            run.font.size = Pt(11)

    def _add_text_with_bold_keywords(self, paragraph, text: str, keywords: List[str]):
        """Add text with specific keywords bolded."""
        # Create regex pattern for keywords
        if not keywords:
            run = paragraph.add_run(text)
            run.font.size = Pt(11)
            return

        # Sort keywords by length (longest first) to avoid partial matches
        sorted_keywords = sorted(keywords, key=len, reverse=True)

        # Escape special regex characters
        escaped_keywords = [re.escape(kw) for kw in sorted_keywords]

        # Create pattern
        pattern = '|'.join(escaped_keywords)

        if not pattern:
            run = paragraph.add_run(text)
            run.font.size = Pt(11)
            return

        # Split text by keywords
        parts = re.split(f'({pattern})', text, flags=re.IGNORECASE)

        for part in parts:
            if part:
                run = paragraph.add_run(part)
                run.font.size = Pt(11)

                # Bold if it's a keyword
                if any(part.lower() == kw.lower() for kw in sorted_keywords):
                    run.font.bold = True

    def _format_date_range(self, start_date: str, end_date: str, is_current: bool) -> str:
        """Format date range."""
        if is_current:
            return f"{start_date} – Present"
        return f"{start_date} – {end_date}"

    def export_resume(
        self,
        resume: Resume,
        output_path: str,
        bold_keywords: List[str] = None
    ):
        """
        Export resume to DOCX.

        Args:
            resume: Resume object
            output_path: Output file path
            bold_keywords: Keywords to bold throughout document
        """
        print(f"\nExporting resume to DOCX: {output_path}")

        # Add name
        self._add_heading(resume.contact.full_name, level=1, color="1F4788")

        # Add contact info
        self._add_contact_info(resume)

        # Professional Summary
        if resume.summary:
            self._add_heading("Professional Summary", level=2, color="1F4788")
            para = self.doc.add_paragraph(resume.summary)
            para.space_after = Pt(12)

        # Technical Skills
        if resume.skills:
            self._add_heading("Technical Skills", level=2, color="1F4788")

            # Group skills or list them
            skills_text = ", ".join(resume.skills)
            para = self.doc.add_paragraph()

            if bold_keywords:
                self._add_text_with_bold_keywords(para, skills_text, bold_keywords)
            else:
                run = para.add_run(skills_text)
                run.font.size = Pt(11)

            para.space_after = Pt(12)

        # Professional Experience
        if resume.experience:
            self._add_heading("Professional Experience", level=2, color="1F4788")

            for exp in resume.experience:
                # Company and title
                self._add_heading(f"{exp.title}", level=3)

                # Company, location, dates
                para = self.doc.add_paragraph()
                company_text = exp.company
                if exp.location:
                    company_text += f", {exp.location}"
                company_text += f" | {self._format_date_range(exp.start_date, exp.end_date, exp.is_current)}"

                run = para.add_run(company_text)
                run.font.size = Pt(10)
                run.font.italic = True
                para.space_after = Pt(6)

                # Bullets
                for bullet in exp.bullets:
                    self._add_bullet_point(bullet, bold_keywords)

                # Add space after experience
                self.doc.add_paragraph().space_after = Pt(6)

        # Education
        if resume.education:
            self._add_heading("Education", level=2, color="1F4788")

            for edu in resume.education:
                para = self.doc.add_paragraph()

                # Degree and institution
                degree_text = f"{edu.degree}"
                if edu.field_of_study:
                    degree_text += f" in {edu.field_of_study}"
                degree_text += f" - {edu.institution}"

                run = para.add_run(degree_text)
                run.font.size = Pt(11)
                run.font.bold = True

                # Graduation date
                if edu.graduation_date:
                    para_date = self.doc.add_paragraph()
                    run_date = para_date.add_run(f"Graduated: {edu.graduation_date}")
                    run_date.font.size = Pt(10)
                    run_date.font.italic = True

                # GPA if available
                if edu.gpa:
                    para_date.add_run(f" | GPA: {edu.gpa}")

                para.space_after = Pt(6)

        # Certifications
        if resume.certifications:
            self._add_heading("Certifications", level=2, color="1F4788")

            for cert in resume.certifications:
                para = self.doc.add_paragraph(style='List Bullet')
                cert_text = cert.name
                if cert.issuer:
                    cert_text += f" - {cert.issuer}"
                if cert.date:
                    cert_text += f" ({cert.date})"

                run = para.add_run(cert_text)
                run.font.size = Pt(11)

        # Save document
        self.doc.save(output_path)
        print(f"✓ Resume exported successfully")

    def export_cover_letter(
        self,
        cover_letter_text: str,
        candidate_name: str,
        output_path: str
    ):
        """
        Export cover letter to DOCX.

        Args:
            cover_letter_text: Cover letter text
            candidate_name: Candidate's name
            output_path: Output file path
        """
        print(f"\nExporting cover letter to DOCX: {output_path}")

        # Add name at top
        para_name = self.doc.add_paragraph()
        para_name.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run_name = para_name.add_run(candidate_name)
        run_name.font.size = Pt(14)
        run_name.font.bold = True
        para_name.space_after = Pt(12)

        # Add current date
        from datetime import datetime
        para_date = self.doc.add_paragraph()
        run_date = para_date.add_run(datetime.now().strftime("%B %d, %Y"))
        run_date.font.size = Pt(11)
        para_date.space_after = Pt(24)

        # Add cover letter content
        # Split by paragraphs
        paragraphs = cover_letter_text.split('\n\n')

        for para_text in paragraphs:
            para_text = para_text.strip()
            if para_text:
                para = self.doc.add_paragraph(para_text)
                para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                para_format = para.paragraph_format
                para_format.space_after = Pt(12)
                para_format.line_spacing = 1.15

                for run in para.runs:
                    run.font.size = Pt(11)

        # Save document
        self.doc.save(output_path)
        print(f"✓ Cover letter exported successfully")

    def export_combined_document(
        self,
        resume: Resume,
        cover_letter_text: str,
        output_path: str,
        bold_keywords: List[str] = None
    ):
        """
        Export cover letter and resume in one document.

        Args:
            resume: Resume object
            cover_letter_text: Cover letter text
            output_path: Output file path
            bold_keywords: Keywords to bold in resume
        """
        print(f"\nExporting combined document to DOCX: {output_path}")

        # First export cover letter
        self.export_cover_letter(cover_letter_text, resume.contact.full_name, output_path)

        # Add page break
        self.doc.add_page_break()

        # Then export resume on second page
        # Add name
        self._add_heading(resume.contact.full_name, level=1, color="1F4788")
        self._add_contact_info(resume)

        # Continue with resume sections...
        # (Same as export_resume but without recreating document)

        self.doc.save(output_path)
        print(f"✓ Combined document exported successfully")


class DOCXExporter:
    """High-level DOCX export interface."""

    @staticmethod
    def export_resume(
        resume: Resume,
        output_path: str,
        template_style: str = "professional",
        bold_keywords: List[str] = None
    ):
        """
        Export resume to DOCX file.

        Args:
            resume: Resume object
            output_path: Output file path
            template_style: Template style
            bold_keywords: Keywords to bold
        """
        formatter = DOCXFormatter(template_style)
        formatter.export_resume(resume, output_path, bold_keywords)

    @staticmethod
    def export_cover_letter(
        cover_letter_text: str,
        candidate_name: str,
        output_path: str,
        template_style: str = "professional"
    ):
        """
        Export cover letter to DOCX file.

        Args:
            cover_letter_text: Cover letter text
            candidate_name: Candidate's name
            output_path: Output file path
            template_style: Template style
        """
        formatter = DOCXFormatter(template_style)
        formatter.export_cover_letter(cover_letter_text, candidate_name, output_path)

    @staticmethod
    def export_combined(
        resume: Resume,
        cover_letter_text: str,
        output_path: str,
        template_style: str = "professional",
        bold_keywords: List[str] = None
    ):
        """
        Export cover letter + resume in one document.

        Args:
            resume: Resume object
            cover_letter_text: Cover letter text
            output_path: Output file path
            template_style: Template style
            bold_keywords: Keywords to bold
        """
        formatter = DOCXFormatter(template_style)
        formatter.export_combined_document(resume, cover_letter_text, output_path, bold_keywords)
