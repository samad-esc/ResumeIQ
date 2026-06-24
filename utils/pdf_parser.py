import PyPDF2
import io

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + " "
        
        # Clean whitespace
        text = " ".join(text.split())
        
        if len(text) < 100:
            return None, "Resume appears to be empty or a scanned image. Upload a text-based PDF."
        
        return text, None
    
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"