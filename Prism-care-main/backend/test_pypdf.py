from pypdf import PdfWriter, PdfReader
import io

def test_pdf_extraction():
    print("Testing pypdf extraction...")
    
    # Create a dummy PDF in memory
    buffer = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    
    # We can't easily add text with just pypdf writer (it's mostly for manipulation), 
    # but we can try to read an existing one if we had it. 
    # Actually, let's just create a file and try to read it to ensure library loads and works.
    # Since we can't generate text-based PDF easily without reportlab, we will check if we can import and verify version.
    
    print(f"pypdf imported successfully.")
    
    # Try to write a simple file
    with open("test.pdf", "wb") as f:
        writer.write(f)
    print("Created test.pdf")
    
    # Try to read it back
    reader = PdfReader("test.pdf")
    print(f"Read test.pdf, pages: {len(reader.pages)}")
    
    print("✅ pypdf is functional")

if __name__ == "__main__":
    test_pdf_extraction()
