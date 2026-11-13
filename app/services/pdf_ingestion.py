from unstructured.partition.pdf import partition_pdf
import os
from pathlib import Path


DATA_PATH = Path(__file__).parent.parent.parent / "data"

# Categories often safe to skip in academic papers
IGNORED_CATEGORIES = {"Header", "Footer", "PageBreak"}

# PDF-to-text extractor
def pdf_extractor(data_dir: Path) -> list[dict]:

    all_documents = []

    if not data_dir.exists():
        raise FileNotFoundError(f"Directory not found: {data_dir}")
    
    pdf_files = sorted(
        file for file in data_dir.iterdir()
        if file.is_file() and file.suffix.lower() == ".pdf"
    )

    for pdf_file in pdf_files:
        elements = partition_pdf(filename=str(pdf_file),
                                strategy="hi_res",
                                hi_res_model_name="yolox",
                                infer_table_structure=True,  # Extracts HTML for tables
                                languages=["eng"])

        for el in elements:
            if not el.text or el.category in IGNORED_CATEGORIES:
                continue

            all_documents.append({
                "source":pdf_file.name,
                "text": el.text,
                "type": el.category,
                "page_number": getattr(el.metadata, "page_number", None),
                "table_html": getattr(el.metadata, "text_as_html", None),
            })

    return all_documents