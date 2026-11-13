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



# if __name__ == "__main__":

#     docs = pdf_extractor(DATA_PATH)

#     print(f"Total extracted elements: {len(docs)}")

#     # Show element categories
#     categories = Counter(doc["type"] for doc in docs)
#     print("\nElement categories:")
#     print(categories)

#     # Show elements per page
#     pages = Counter(doc["page_number"] for doc in docs)
#     print("\nElements per page:")
#     print(pages)

#     # Inspect first 15 extracted elements
#     print("\nFirst 15 elements:")

#     for i, doc in enumerate(docs[:15], start=1):

#         preview = doc["text"].replace("\n", " ")[:250]

#         print(
#             f"\n{i}. "
#             f"[Page {doc['page_number']}] "
#             f"[{doc['type']}]"
#         )

#         print(preview)

#         if doc["table_html"]:
#             print("Table HTML detected!")


if __name__ == "__main__":

    docs = pdf_extractor(DATA_PATH)

    # Inspect complete pages
    for page_number in [1, 2, 3]:

        print(f"\n{'=' * 60}")
        print(f"PAGE {page_number}")
        print(f"{'=' * 60}")

        page_docs = [
            doc for doc in docs
            if doc["page_number"] == page_number
        ]

        for i, doc in enumerate(page_docs, start=1):

            text = " ".join(doc["text"].split())

            print(
                f"\n{i}. [{doc['type']}] "
                f"({len(text)} characters)"
            )

            print(text[:400])

    # Inspect detected tables separately
    print("\n\nTABLE EXTRACTION RESULTS")

    for doc in docs:

        if doc["type"] == "Table":

            print(f"\nPage: {doc['page_number']}")
            print("Text:", doc["text"][:500])

            if doc["table_html"]:
                print("HTML:", doc["table_html"][:1000])
            else:
                print("No HTML representation detected.")

