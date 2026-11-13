
import argparse
from collections import Counter
from pathlib import Path

from app.services.pdf_ingestion import DATA_PATH, pdf_extractor


def inspect_pdf(
    data_dir: Path,
    pages: list[int],
    preview_count: int,
    element_chars: int,
    page_chars: int,
    table_chars: int,
) -> None:
    """Extract PDFs and print a report about extraction quality."""

    docs = pdf_extractor(data_dir)

    print("\n" + "=" * 60)
    print("PDF INGESTION REPORT")
    print("=" * 60)

    if not docs:
        print(f"\nNo PDF elements extracted from: {data_dir}")
        return

    # 1. Total extracted elements
    print(f"\nTotal extracted elements: {len(docs)}")

    # 2. Element categories
    categories = Counter(doc["type"] for doc in docs)

    print("\nElement categories:")
    for category, count in categories.most_common():
        print(f"  {category}: {count}")

    # 3. Elements per page
    page_counts = Counter(doc["page_number"] for doc in docs)

    print("\nElements per page:")
    for page, count in sorted(
        page_counts.items(),
        key=lambda item: (
            item[0] is None,
            item[0] if item[0] is not None else 0,
        ),
    ):
        print(f"  Page {page if page is not None else 'Unknown'}: {count}")

    # 4. Preview first N elements
    print(f"\nFIRST {preview_count} EXTRACTED ELEMENTS")

    for index, doc in enumerate(docs[:preview_count], start=1):
        text = " ".join(doc["text"].split())

        print(
            f"\n{index}. "
            f"[Page {doc['page_number']}] "
            f"[{doc['type']}]"
        )
        print(text[:element_chars])

        if doc["table_html"]:
            print("  Table HTML detected.")

    # 5. Inspect selected pages
    for page_number in pages:
        print("\n" + "=" * 60)
        print(f"PAGE {page_number}")
        print("=" * 60)

        page_docs = [
            doc for doc in docs
            if doc["page_number"] == page_number
        ]

        if not page_docs:
            print("No extracted elements found for this page.")
            continue

        for index, doc in enumerate(page_docs, start=1):
            text = " ".join(doc["text"].split())

            print(
                f"\n{index}. [{doc['type']}] "
                f"({len(text)} characters)"
            )
            print(text[:page_chars])

    # 6. Inspect detected tables
    tables = [
        doc for doc in docs
        if doc["type"] == "Table"
    ]

    print("\n" + "=" * 60)
    print("TABLE EXTRACTION RESULTS")
    print("=" * 60)

    if not tables:
        print("No tables detected.")
        return

    for index, doc in enumerate(tables, start=1):
        print(f"\nTable {index} | Page: {doc['page_number']}")
        print("\nExtracted text:")
        print(doc["text"][:table_chars])

        if doc["table_html"]:
            print("\nExtracted HTML:")
            print(doc["table_html"][:table_chars])
        else:
            print("\nNo HTML representation detected.")

    print("\n" + "=" * 60)
    print("END OF REPORT")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspect PDF extraction quality."
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_PATH,
        help="Directory containing PDF files (default: data/).",
    )

    parser.add_argument(
        "--pages",
        type=int,
        nargs="+",
        default=[1, 2, 3],
        help="Page numbers to inspect (default: 1 2 3).",
    )

    parser.add_argument(
        "--preview-count",
        type=int,
        default=15,
        help="Number of extracted elements to preview.",
    )

    parser.add_argument(
        "--element-chars",
        type=int,
        default=250,
        help="Maximum characters shown per element preview.",
    )

    parser.add_argument(
        "--page-chars",
        type=int,
        default=400,
        help="Maximum characters shown per page element.",
    )

    parser.add_argument(
        "--table-chars",
        type=int,
        default=1000,
        help="Maximum characters shown per table representation.",
    )

    args = parser.parse_args()

    inspect_pdf(
        data_dir=args.data_dir,
        pages=args.pages,
        preview_count=args.preview_count,
        element_chars=args.element_chars,
        page_chars=args.page_chars,
        table_chars=args.table_chars,
    )


if __name__ == "__main__":
    main()
