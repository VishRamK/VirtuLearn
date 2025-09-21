import os
import io
from typing import List, Tuple
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_pdf_text(path: str) -> str:
    parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            parts.append(t)
    return "\n".join(parts).strip()

def extract_pdf_images_as_pil(path: str, dpi: int = 300) -> List[Image.Image]:
    # pdf2image renders each page; we can OCR full-page raster and/or crop figures if needed.
    # For simplicity, we OCR full pages and also keep rendered pages as images.
    pages = convert_from_path(path, dpi=dpi)
    return pages  # list of PIL Images

def ocr_images(images: List[Image.Image], lang: str = "eng") -> str:
    ocr_parts = []
    for idx, img in enumerate(images, start=1):
        text = pytesseract.image_to_string(img, lang=lang) or ""
        if text.strip():
            ocr_parts.append(f"[OCR Page {idx}]\n{text.strip()}")
    return "\n\n".join(ocr_parts).strip()

def read_pdf_with_images(path: str) -> Tuple[str, str]:
    """
    Returns:
      (plain_text, ocr_text_from_images)
    """
    text = extract_pdf_text(path)
    images = extract_pdf_images_as_pil(path)
    ocr_text = ocr_images(images)
    return text, ocr_text

'''

import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()  # uses OPENAI_API_KEY from env

def pil_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")

async def caption_images_with_openai(images: List[Image.Image]) -> str:
    import asyncio
    b64s = [pil_to_base64(img) for img in images[:5]]  # limit for speed
    prompts = []
    for i, b64 in enumerate(b64s, start=1):
        prompts.append({
            "role": "user",
            "content": [
                {"type": "text", "text": f"Describe this page’s key visual information succinctly. Focus on facts, labels, axes, and relationships. Page {i}."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        })
    # Run sequentially for simplicity (can parallelize if you want)
    captions = []
    for msg in prompts:
        resp = await client.chat.completions.with_streaming_response.create(
            model="gpt-4o",
            messages=[msg],
            temperature=0.2,
        )
        full = await resp.get_final_response()
        captions.append(full.choices[0].message.content.strip())
    return "\n\n".join([f"[VISION Page {i}]\n{cap}" for i, cap in enumerate(captions, start=1)])
'''