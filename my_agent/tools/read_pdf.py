import fitz  # PyMuPDF


def read_pdf(file_path: str) -> str:
    """Read and extract all text content from a PDF file.

    Use this tool whenever a question references a PDF file or when file paths
    ending in .pdf are provided. Pass the exact file path given in the question.

    Args:
        file_path: The path to the PDF file to read.

    Returns:
        The full text content extracted from all pages of the PDF.
    """
    try:
        doc = fitz.open(file_path)
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_parts.append(page.get_text())
        doc.close()
        full_text = "\n".join(text_parts)
        if not full_text.strip():
            return "The PDF appears to contain no extractable text (it may be image-based)."
        return full_text
    except FileNotFoundError:
        return f"Error: File not found at '{file_path}'."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"
