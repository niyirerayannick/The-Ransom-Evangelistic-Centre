"""Render book PDF pages as JPEG images using PyMuPDF."""


def get_pdf_page_count(file_field):
    import fitz

    with file_field.open("rb") as handle:
        document = fitz.open(stream=handle.read(), filetype="pdf")
        return document.page_count


def render_pdf_page_jpeg(file_field, page_num, max_width=1200):
    import fitz

    with file_field.open("rb") as handle:
        document = fitz.open(stream=handle.read(), filetype="pdf")
        if page_num < 1 or page_num > document.page_count:
            raise ValueError("Page out of range")

        page = document.load_page(page_num - 1)
        scale = min(max(max_width / page.rect.width, 0.5), 2.5)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        return pixmap.tobytes("jpeg")
