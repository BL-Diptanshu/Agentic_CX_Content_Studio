import io
import requests
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.colors import HexColor
from PIL import Image as PILImage


def generate_campaign_pdf(campaign_name, brand, text_content, image_url=None):
    """
    Generate a PDF export of campaign content.
    
    Args:
        campaign_name: Name of the campaign
        brand: Brand name
        text_content: Generated marketing copy
        image_url: URL of the generated image (optional)
    
    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2E86AB'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Custom subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#A23B72'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    # Custom heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor('#2E86AB'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Body text style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        spaceAfter=12,
        alignment=TA_LEFT
    )
    
    # Add title
    title = Paragraph(f"Campaign: {campaign_name}", title_style)
    elements.append(title)
    
    # Add brand
    subtitle = Paragraph(f"Brand: {brand}", subtitle_style)
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add text content
    # Replace newlines with <br/> tags for proper formatting
    formatted_text = text_content.replace('\n', '<br/>')
    text_para = Paragraph(formatted_text, body_style)
    elements.append(text_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add image if available
    if image_url:
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                img_buffer = io.BytesIO(response.content)
                pil_img = PILImage.open(img_buffer)
                
                # Calculate size to fit within page
                max_width = 5 * inch
                max_height = 5 * inch
                
                img_width, img_height = pil_img.size
                aspect_ratio = img_width / img_height
                
                if img_width > max_width or img_height > max_height:
                    if aspect_ratio > 1:  # Landscape
                        new_width = max_width
                        new_height = max_width / aspect_ratio
                    else:  # Portrait
                        new_height = max_height
                        new_width = max_height * aspect_ratio
                else:
                    new_width = img_width
                    new_height = img_height
                
                # Create reportlab Image
                img = Image(img_buffer, width=new_width, height=new_height)
                elements.append(img)
        except Exception as e:
            error_text = Paragraph(f"<i>Could not load image: {str(e)}</i>", body_style)
            elements.append(error_text)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
