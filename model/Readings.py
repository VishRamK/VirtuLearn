from pathlib import Path
import fitz  # PyMuPDF


def pdf_to_txt(pdf_path: str | Path, out_path: str | Path | None = None) -> Path:
    """
    Extract text from a PDF and save to a .txt file.

    - pdf_path: path to the input PDF
    - out_path: optional output .txt path. If None, uses pdf_path with .txt suffix.

    Returns the Path to the written .txt file.
    """
    pdf_path = Path(pdf_path)
    if out_path is None:
        out_path = pdf_path.with_suffix(".txt")
    out_path = Path(out_path)

    with fitz.open(pdf_path) as doc:
        text = "\n\n".join(page.get_text("text") for page in doc)

    out_path.write_text(text, encoding="utf-8")
    print(f"Wrote {out_path}")
    return out_path


if __name__ == "__main__":
    # Keeps previous simple behavior when run directly
    pdf_to_txt("14_backprop.pdf", "14_backprop.txt")