import pdfplumber
import os
import sys

def pdf_to_text(pdf_path, output_path):
    """Convert a PDF file to text while preserving layout as much as possible."""
    print(f"Converting: {os.path.basename(pdf_path)}")
    
    with pdfplumber.open(pdf_path) as pdf:
        all_text = []
        for i, page in enumerate(pdf.pages, 1):
            # Extract text preserving layout
            text = page.extract_text(layout=True)
            if text:
                all_text.append(f"{'='*60}")
                all_text.append(f"  Page {i}")
                all_text.append(f"{'='*60}")
                all_text.append("")
                all_text.append(text)
                all_text.append("")
            
            # Also extract tables if any
            tables = page.extract_tables()
            if tables:
                for t_idx, table in enumerate(tables, 1):
                    all_text.append(f"\n--- Table {t_idx} on Page {i} ---")
                    for row in table:
                        # Clean None values
                        cleaned = [str(cell) if cell is not None else "" for cell in row]
                        all_text.append("\t".join(cleaned))
                    all_text.append("")
    
    full_text = "\n".join(all_text)
    
    # Write with UTF-8 encoding
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"  -> Saved: {os.path.basename(output_path)} ({len(pdf.pages)} pages)")
    return full_text


def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    pdf_files = sorted([f for f in os.listdir(folder) if f.lower().endswith('.pdf')])
    
    if not pdf_files:
        print("No PDF files found.")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s):\n")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder, pdf_file)
        # Replace .pdf with .txt
        txt_file = os.path.splitext(pdf_file)[0] + ".txt"
        txt_path = os.path.join(folder, txt_file)
        
        try:
            pdf_to_text(pdf_path, txt_path)
        except Exception as e:
            print(f"  ERROR converting {pdf_file}: {e}")
    
    print("\nDone!")


if __name__ == "__main__":
    main()
