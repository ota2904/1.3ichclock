"""
Enhanced PDF Extractor - Inspired by DeepSeek-OCR
Preserves structure, tables, images, and layout information
"""
import fitz  # PyMuPDF
from PIL import Image
import io
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PDFBlock:
    """Represents a block in PDF (text, image, or table)"""
    type: str  # "text", "image", "table"
    bbox: tuple  # (x1, y1, x2, y2)
    content: str  # Text content or description
    page_num: int
    metadata: dict = None


class EnhancedPDFExtractor:
    """
    Enhanced PDF extraction với structure preservation
    
    Features:
    - Layout-aware extraction (bounding boxes)
    - Text block detection với vị trí
    - Image extraction
    - Table detection (heuristic-based)
    - Page-level metadata
    """
    
    def __init__(self, dpi: int = 144):
        """
        Args:
            dpi: Resolution for image extraction (default 144 like DeepSeek-OCR)
        """
        self.dpi = dpi
        
    def extract_with_structure(self, pdf_path: str) -> Dict:
        """
        Extract PDF with full structure preservation
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            {
                "pages": [
                    {
                        "page_num": 1,
                        "text": "full page text",
                        "blocks": [PDFBlock, ...],
                        "width": 595, "height": 842
                    }
                ],
                "metadata": {...},
                "total_pages": 10
            }
        """
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"❌ [PDF] Error opening {pdf_path}: {e}")
            return {"error": str(e), "pages": []}
        
        result = {
            "pages": [],
            "metadata": doc.metadata,
            "total_pages": doc.page_count
        }
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            page_data = {
                "page_num": page_num + 1,
                "text": "",
                "blocks": [],
                "width": page.rect.width,
                "height": page.rect.height
            }
            
            # Extract blocks với bounding boxes
            blocks = page.get_text("dict")["blocks"]
            page_text_parts = []
            
            for block in blocks:
                if block["type"] == 0:  # Text block
                    text_content = self._extract_text_from_block(block)
                    if text_content.strip():
                        page_text_parts.append(text_content)
                        
                        page_data["blocks"].append(PDFBlock(
                            type="text",
                            bbox=block["bbox"],
                            content=text_content,
                            page_num=page_num + 1,
                            metadata={
                                "lines": len(block.get("lines", [])),
                                "font_sizes": self._get_font_sizes(block)
                            }
                        ))
                
                elif block["type"] == 1:  # Image block
                    try:
                        # Extract image
                        img_info = self._extract_image(doc, block, page_num)
                        if img_info:
                            page_data["blocks"].append(PDFBlock(
                                type="image",
                                bbox=block["bbox"],
                                content=f"[Image: {img_info['width']}x{img_info['height']}]",
                                page_num=page_num + 1,
                                metadata=img_info
                            ))
                            page_text_parts.append(f"[Image: {img_info['width']}x{img_info['height']}]")
                    except Exception as e:
                        print(f"⚠️ [PDF] Error extracting image on page {page_num+1}: {e}")
            
            # Detect tables (simple heuristic)
            tables = self._detect_tables(page, page_num)
            page_data["blocks"].extend(tables)
            for table in tables:
                page_text_parts.append(table.content)
            
            # Join all text
            page_data["text"] = "\n".join(page_text_parts)
            result["pages"].append(page_data)
        
        total_pages = doc.page_count
        doc.close()
        
        print(f"✅ [PDF] Extracted {total_pages} pages with structure")
        return result
    
    def _extract_text_from_block(self, block: dict) -> str:
        """Extract text from a text block"""
        text_parts = []
        for line in block.get("lines", []):
            line_text = ""
            for span in line.get("spans", []):
                line_text += span.get("text", "")
            if line_text.strip():
                text_parts.append(line_text)
        return "\n".join(text_parts)
    
    def _get_font_sizes(self, block: dict) -> List[float]:
        """Get font sizes in block for header detection"""
        sizes = []
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                sizes.append(span.get("size", 12))
        return sizes
    
    def _extract_image(self, doc, block: dict, page_num: int) -> Optional[dict]:
        """Extract image from block"""
        try:
            xref = block.get("image")
            if not xref:
                return None
            
            pix = fitz.Pixmap(doc, xref)
            
            # Convert to PIL Image
            if pix.n < 5:  # GRAY or RGB
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            else:  # CMYK or other
                img = Image.frombytes("RGBA", [pix.width, pix.height], pix.samples)
            
            return {
                "width": pix.width,
                "height": pix.height,
                "colorspace": pix.colorspace.name if pix.colorspace else "unknown",
                "xref": xref
            }
        except Exception as e:
            print(f"⚠️ [PDF] Image extraction failed: {e}")
            return None
    
    def _detect_tables(self, page, page_num: int) -> List[PDFBlock]:
        """
        Detect tables using heuristic (lines and grid patterns)
        Simple implementation - can be improved with ML
        """
        tables = []
        
        # Get horizontal and vertical lines
        drawings = page.get_drawings()
        h_lines = []
        v_lines = []
        
        for drawing in drawings:
            for item in drawing["items"]:
                if item[0] == "l":  # Line
                    p1, p2 = item[1], item[2]
                    if abs(p1.y - p2.y) < 2:  # Horizontal line
                        h_lines.append((min(p1.x, p2.x), p1.y, max(p1.x, p2.x), p1.y))
                    elif abs(p1.x - p2.x) < 2:  # Vertical line
                        v_lines.append((p1.x, min(p1.y, p2.y), p1.x, max(p1.y, p2.y)))
        
        # If we have both h and v lines, likely a table
        if len(h_lines) >= 2 and len(v_lines) >= 2:
            # Find bounding box of table
            all_x = [x for line in h_lines for x in [line[0], line[2]]] + \
                   [x for line in v_lines for x in [line[0], line[2]]]
            all_y = [y for line in h_lines for y in [line[1], line[3]]] + \
                   [y for line in v_lines for y in [line[1], line[3]]]
            
            if all_x and all_y:
                bbox = (min(all_x), min(all_y), max(all_x), max(all_y))
                
                tables.append(PDFBlock(
                    type="table",
                    bbox=bbox,
                    content=f"[Table: {len(h_lines)-1} rows x {len(v_lines)-1} cols]",
                    page_num=page_num + 1,
                    metadata={
                        "h_lines": len(h_lines),
                        "v_lines": len(v_lines),
                        "estimated_rows": len(h_lines) - 1,
                        "estimated_cols": len(v_lines) - 1
                    }
                ))
        
        return tables
    
    def convert_to_markdown(self, pdf_data: Dict) -> str:
        """
        Convert structured PDF to markdown
        
        Features:
        - Preserve page numbers
        - Detect headers (large font)
        - Keep table placeholders
        - Reference images
        """
        markdown = ""
        
        for page in pdf_data["pages"]:
            markdown += f"\n## 📄 Page {page['page_num']}\n\n"
            
            for block in page["blocks"]:
                if block.type == "text":
                    # Detect if this is a header (font size > 14)
                    font_sizes = block.metadata.get("font_sizes", [12])
                    avg_font = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                    
                    if avg_font > 14:
                        # Header
                        markdown += f"### {block.content}\n\n"
                    else:
                        # Normal text
                        markdown += f"{block.content}\n\n"
                
                elif block.type == "table":
                    markdown += f"**{block.content}**\n\n"
                    markdown += "*(Table structure detected - content may vary)*\n\n"
                
                elif block.type == "image":
                    markdown += f"![{block.content}]\n\n"
        
        return markdown
    
    def to_plain_text(self, pdf_data: Dict) -> str:
        """
        Convert to plain text (backward compatible with existing system)
        """
        text_parts = []
        
        for page in pdf_data["pages"]:
            text_parts.append(f"=== Page {page['page_num']} ===")
            text_parts.append(page["text"])
            text_parts.append("")  # Blank line
        
        return "\n".join(text_parts)
    
    def get_statistics(self, pdf_data: Dict) -> dict:
        """Get PDF statistics"""
        stats = {
            "total_pages": pdf_data["total_pages"],
            "total_blocks": 0,
            "text_blocks": 0,
            "image_blocks": 0,
            "table_blocks": 0,
            "total_chars": 0
        }
        
        for page in pdf_data["pages"]:
            stats["total_blocks"] += len(page["blocks"])
            stats["total_chars"] += len(page["text"])
            
            for block in page["blocks"]:
                if block.type == "text":
                    stats["text_blocks"] += 1
                elif block.type == "image":
                    stats["image_blocks"] += 1
                elif block.type == "table":
                    stats["table_blocks"] += 1
        
        return stats


# Test function
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python deepseek_pdf_extractor.py <pdf_file>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    print(f"🔍 Testing Enhanced PDF Extractor with: {pdf_path}")
    print("="*60)
    
    extractor = EnhancedPDFExtractor()
    
    # Extract
    data = extractor.extract_with_structure(pdf_path)
    
    # Statistics
    stats = extractor.get_statistics(data)
    print("\n📊 Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Show first page blocks
    if data["pages"]:
        print(f"\n📄 Page 1 blocks:")
        for i, block in enumerate(data["pages"][0]["blocks"][:5]):  # First 5 blocks
            print(f"  {i+1}. {block.type}: {block.content[:50]}...")
    
    # Markdown output
    print("\n📝 Markdown preview (first 500 chars):")
    markdown = extractor.convert_to_markdown(data)
    print(markdown[:500] + "...")
