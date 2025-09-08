from pathlib import Path
import io, zipfile
import pdfplumber
import docx2txt

def read_text(path: Path) -> str:
    path = Path(path)
    text = ""
    if path.suffix.lower() == ".pdf":
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        text = "\n".join(text_parts)
        print(f"🔍 PDF Extraction: {path.name} -> {len(text)} characters")
    elif path.suffix.lower() in {".doc", ".docx"}:
        text = docx2txt.process(str(path)) or ""
        print(f"🔍 DOCX Extraction: {path.name} -> {len(text)} characters")
    else:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            print(f"🔍 Text Extraction: {path.name} -> {len(text)} characters")
        except Exception:
            text = path.read_text(errors="ignore")
            print(f"🔍 Text Extraction (fallback): {path.name} -> {len(text)} characters")
    
    return text

def load_files_from_uploader(files) -> list[tuple[str, str]]:
    """
    Accepts a list of streamlit UploadedFile objects (.pdf, .docx, .zip) and returns (name, text).
    """
    results = []
    print(f"\n📁 Processing {len(files)} uploaded file(s)...")
    
    for f in files:
        name = f.name
        data = f.read()
        print(f"📄 Processing: {name}")
        
        if name.lower().endswith(".zip"):
            print(f"   📦 ZIP file detected, extracting contents...")
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                zip_members = [member for member in z.namelist() if member.lower().endswith((".pdf",".doc",".docx",".txt"))]
                print(f"   📦 Found {len(zip_members)} extractable files in ZIP")
                
                for member in zip_members:
                    with z.open(member) as fh:
                        tmp = Path("/tmp")/Path(member).name
                        tmp.write_bytes(fh.read())
                        extracted_text = read_text(tmp)
                        results.append((Path(member).name, extracted_text))
                        print(f"   ✅ Extracted from ZIP: {Path(member).name} -> {len(extracted_text)} characters")
        else:
            tmp = Path("/tmp")/name
            tmp.write_bytes(data)
            extracted_text = read_text(tmp)
            results.append((name, extracted_text))
            print(f"   ✅ Direct extraction: {name} -> {len(extracted_text)} characters")
    
    print(f"🎯 Total processed: {len(results)} documents")
    return results
