
from types import SimpleNamespace

import pytest

from app.services import pdf_ingestion


def make_element(
    text,
    category,
    page_number=1,
    table_html=None,
):
    """Create a mock Unstructured document element."""

    metadata = SimpleNamespace(
        page_number=page_number,
        text_as_html=table_html,
    )

    return SimpleNamespace(
        text=text,
        category=category,
        metadata=metadata,
    )


def test_extracts_text_and_preserves_metadata(tmp_path, monkeypatch):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"fake pdf content")

    elements = [
        make_element(
            text="Introduction to object detection",
            category="Title",
            page_number=1,
        ),
        make_element(
            text="YOLO is a real-time object detector.",
            category="NarrativeText",
            page_number=2,
        ),
    ]

    monkeypatch.setattr(
        pdf_ingestion,
        "partition_pdf",
        lambda **kwargs: elements,
    )

    docs = pdf_ingestion.pdf_extractor(tmp_path)

    assert len(docs) == 2

    assert docs[0]["source"] == "sample.pdf"
    assert docs[0]["text"] == "Introduction to object detection"
    assert docs[0]["type"] == "Title"
    assert docs[0]["page_number"] == 1

    assert docs[1]["page_number"] == 2


def test_ignores_empty_elements_and_unwanted_categories(
    tmp_path,
    monkeypatch,
):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"fake pdf content")

    elements = [
        make_element("", "NarrativeText"),
        make_element(None, "NarrativeText"),
        make_element("Page header", "Header"),
        make_element("Page footer", "Footer"),
        make_element("", "PageBreak"),
        make_element("Useful content", "NarrativeText"),
    ]

    monkeypatch.setattr(
        pdf_ingestion,
        "partition_pdf",
        lambda **kwargs: elements,
    )

    docs = pdf_ingestion.pdf_extractor(tmp_path)

    assert len(docs) == 1
    assert docs[0]["text"] == "Useful content"


def test_preserves_table_html(tmp_path, monkeypatch):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"fake pdf content")

    html = "<table><tr><td>YOLO</td></tr></table>"

    elements = [
        make_element(
            text="YOLO results",
            category="Table",
            page_number=5,
            table_html=html,
        )
    ]

    monkeypatch.setattr(
        pdf_ingestion,
        "partition_pdf",
        lambda **kwargs: elements,
    )

    docs = pdf_ingestion.pdf_extractor(tmp_path)

    assert docs[0]["table_html"] == html
    assert docs[0]["page_number"] == 5


def test_accepts_uppercase_pdf_extension(tmp_path, monkeypatch):
    pdf_path = tmp_path / "sample.PDF"
    pdf_path.write_bytes(b"fake pdf content")

    elements = [
        make_element("PDF content", "NarrativeText")
    ]

    monkeypatch.setattr(
        pdf_ingestion,
        "partition_pdf",
        lambda **kwargs: elements,
    )

    docs = pdf_ingestion.pdf_extractor(tmp_path)

    assert len(docs) == 1
    assert docs[0]["source"] == "sample.PDF"


def test_missing_directory_raises_error(tmp_path):
    missing_dir = tmp_path / "does_not_exist"

    with pytest.raises(FileNotFoundError):
        pdf_ingestion.pdf_extractor(missing_dir)


def test_empty_directory_returns_empty_list(tmp_path):
    docs = pdf_ingestion.pdf_extractor(tmp_path)

    assert docs == []
