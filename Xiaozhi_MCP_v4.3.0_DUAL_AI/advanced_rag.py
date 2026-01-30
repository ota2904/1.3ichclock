"""
Advanced RAG System - Enhanced Knowledge Base with Multi-modal Support
======================================================================
Nâng cấp toàn diện để hỗ trợ:
1. Cross-reference tracking (page numbers, long-context)
2. Complex table preservation
3. Conflicting information detection
4. Multimodal OCR (images, diagrams)
5. Advanced aggregation & summarization

Copyright © 2025 miniZ Team
"""

import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import asyncio

# ============================================================
# ENHANCED DATA STRUCTURES
# ============================================================

@dataclass
class PageInfo:
    """Thông tin về trang trong document"""
    page_number: int
    content: str
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    references: List[str] = field(default_factory=list)  # Cross-references
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TableInfo:
    """Thông tin về bảng"""
    page_number: int
    table_index: int
    headers: List[str]
    rows: List[List[str]]
    merged_cells: List[Tuple[int, int, int, int]] = field(default_factory=list)  # (row1, col1, row2, col2)
    markdown: str = ""
    summary: str = ""

@dataclass
class ImageInfo:
    """Thông tin về hình ảnh"""
    page_number: int
    image_index: int
    image_type: str  # diagram, chart, photo, etc
    ocr_text: str = ""
    description: str = ""
    extracted_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentChunk:
    """Enhanced chunk với metadata đầy đủ"""
    doc_id: str
    chunk_id: str
    content: str
    page_numbers: List[int]  # Có thể span nhiều pages
    chunk_index: int
    total_chunks: int
    
    # Enhanced metadata
    has_tables: bool = False
    has_images: bool = False
    table_ids: List[str] = field(default_factory=list)
    image_ids: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)
    
    # Timestamps for conflict detection
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    version: str = "1.0"
    
    # Embeddings for semantic search (optional)
    embedding: Optional[List[float]] = None
    
    # Context links
    prev_chunk_id: Optional[str] = None
    next_chunk_id: Optional[str] = None

@dataclass
class ConflictInfo:
    """Thông tin về xung đột dữ liệu"""
    field_name: str
    values: List[Tuple[Any, str, int]]  # (value, source_chunk_id, page_number)
    confidence_scores: List[float]
    resolution: Optional[str] = None
    reason: str = ""

# ============================================================
# ADVANCED PDF EXTRACTOR
# ============================================================

class AdvancedPDFExtractor:
    """
    Extract PDF với support:
    - Page tracking
    - Table structure preservation
    - Image OCR
    - Cross-reference detection
    """
    
    def __init__(self):
        self.ocr_available = False
        self.table_extract_available = False
        
        # Check available libraries
        try:
            import pytesseract
            self.ocr_available = True
        except ImportError:
            pass
        
        try:
            import camelot  # or tabula-py
            self.table_extract_available = True
        except ImportError:
            pass
    
    def extract_with_structure(self, pdf_path: str) -> Dict[str, Any]:
        """Extract PDF với đầy đủ structure"""
        try:
            import PyPDF2
            from PIL import Image
            import io
            
            result = {
                "success": True,
                "pages": [],
                "tables": [],
                "images": [],
                "metadata": {},
                "total_pages": 0
            }
            
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                result["total_pages"] = len(reader.pages)
                result["metadata"] = {
                    "title": reader.metadata.get('/Title', '') if reader.metadata else '',
                    "author": reader.metadata.get('/Author', '') if reader.metadata else '',
                    "creation_date": reader.metadata.get('/CreationDate', '') if reader.metadata else ''
                }
                
                for page_num, page in enumerate(reader.pages, 1):
                    print(f"📄 [PDF] Processing page {page_num}/{result['total_pages']}...")
                    
                    # Extract text
                    text = page.extract_text()
                    
                    # Detect cross-references (e.g., "see page 50", "trang 5")
                    refs = self._detect_references(text)
                    
                    # Create page info
                    page_info = PageInfo(
                        page_number=page_num,
                        content=text,
                        references=refs,
                        metadata={"word_count": len(text.split())}
                    )
                    
                    result["pages"].append(page_info)
                    
                    # Extract images if available
                    if hasattr(page, 'images'):
                        for img_idx, img in enumerate(page.images):
                            try:
                                image_info = self._process_image(img, page_num, img_idx)
                                if image_info:
                                    result["images"].append(image_info)
                                    page_info.images.append(image_info.__dict__)
                            except Exception as e:
                                print(f"⚠️ [PDF] Image extraction error: {e}")
            
            # Extract tables using specialized library
            if self.table_extract_available:
                result["tables"] = self._extract_tables_camelot(pdf_path)
            else:
                # Fallback: detect tables from text patterns
                result["tables"] = self._detect_tables_from_text(result["pages"])
            
            return result
            
        except Exception as e:
            print(f"❌ [PDF] Extraction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "pages": [],
                "tables": [],
                "images": []
            }
    
    def _detect_references(self, text: str) -> List[str]:
        """Detect cross-references in text"""
        patterns = [
            r'(see|xem|tham khảo)\s+(page|trang|p\.?)\s+(\d+)',
            r'(figure|hình|biểu đồ)\s+(\d+\.?\d*)',
            r'(table|bảng)\s+(\d+\.?\d*)',
            r'(section|mục|phần)\s+(\d+\.?\d*)',
        ]
        
        refs = []
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                refs.append(match.group(0))
        
        return refs
    
    def _process_image(self, img_data: Any, page_num: int, img_idx: int) -> Optional[ImageInfo]:
        """Process image với OCR"""
        try:
            if not self.ocr_available:
                return ImageInfo(
                    page_number=page_num,
                    image_index=img_idx,
                    image_type="unknown",
                    ocr_text="[OCR not available - install pytesseract]"
                )
            
            import pytesseract
            from PIL import Image
            import io
            
            # Convert image data to PIL Image
            if hasattr(img_data, 'data'):
                image = Image.open(io.BytesIO(img_data.data))
            else:
                return None
            
            # Perform OCR
            ocr_text = pytesseract.image_to_string(image, lang='vie+eng')
            
            # Detect image type (simple heuristics)
            img_type = "photo"
            if any(word in ocr_text.lower() for word in ['chart', 'graph', 'diagram', 'biểu đồ', 'sơ đồ']):
                img_type = "diagram"
            
            return ImageInfo(
                page_number=page_num,
                image_index=img_idx,
                image_type=img_type,
                ocr_text=ocr_text.strip()
            )
            
        except Exception as e:
            print(f"⚠️ [Image OCR] Error: {e}")
            return None
    
    def _extract_tables_camelot(self, pdf_path: str) -> List[TableInfo]:
        """Extract tables using Camelot"""
        try:
            import camelot
            
            tables = []
            camelot_tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            
            for idx, table in enumerate(camelot_tables):
                df = table.df
                
                # Get headers and rows
                headers = df.iloc[0].tolist() if len(df) > 0 else []
                rows = df.iloc[1:].values.tolist() if len(df) > 1 else []
                
                # Convert to markdown
                markdown = self._table_to_markdown(headers, rows)
                
                table_info = TableInfo(
                    page_number=table.page,
                    table_index=idx,
                    headers=headers,
                    rows=rows,
                    markdown=markdown
                )
                
                tables.append(table_info)
                print(f"📊 [Table] Extracted table {idx + 1} from page {table.page}")
            
            return tables
            
        except Exception as e:
            print(f"⚠️ [Table] Camelot extraction error: {e}")
            return []
    
    def _detect_tables_from_text(self, pages: List[PageInfo]) -> List[TableInfo]:
        """Fallback: detect tables from text patterns"""
        tables = []
        
        for page in pages:
            text = page.content
            lines = text.split('\n')
            
            # Simple heuristic: lines with multiple separator characters
            table_lines = []
            for line in lines:
                if line.count('|') >= 2 or line.count('\t') >= 2:
                    table_lines.append(line)
            
            if len(table_lines) >= 3:  # At least header + 2 rows
                # Try to parse as table
                rows = []
                for line in table_lines:
                    if '|' in line:
                        cells = [c.strip() for c in line.split('|')]
                        rows.append(cells)
                    elif '\t' in line:
                        cells = [c.strip() for c in line.split('\t')]
                        rows.append(cells)
                
                if rows:
                    headers = rows[0] if rows else []
                    data_rows = rows[1:] if len(rows) > 1 else []
                    
                    markdown = self._table_to_markdown(headers, data_rows)
                    
                    table_info = TableInfo(
                        page_number=page.page_number,
                        table_index=len(tables),
                        headers=headers,
                        rows=data_rows,
                        markdown=markdown
                    )
                    
                    tables.append(table_info)
        
        return tables
    
    def _table_to_markdown(self, headers: List[str], rows: List[List[str]]) -> str:
        """Convert table to Markdown format"""
        if not headers:
            return ""
        
        # Header row
        md = "| " + " | ".join(str(h) for h in headers) + " |\n"
        
        # Separator row
        md += "| " + " | ".join("---" for _ in headers) + " |\n"
        
        # Data rows
        for row in rows:
            # Pad row to match header length
            padded_row = row + [""] * (len(headers) - len(row))
            md += "| " + " | ".join(str(cell) for cell in padded_row[:len(headers)]) + " |\n"
        
        return md

# ============================================================
# CONFLICT DETECTOR
# ============================================================

class ConflictDetector:
    """Detect và resolve conflicts trong dữ liệu"""
    
    def __init__(self):
        self.conflicts: List[ConflictInfo] = []
    
    def detect_conflicts(self, chunks: List[DocumentChunk], field_patterns: Dict[str, str]) -> List[ConflictInfo]:
        """
        Detect conflicts dựa trên patterns
        
        Args:
            chunks: List of document chunks
            field_patterns: Dict of {field_name: regex_pattern}
                Example: {"revenue": r"doanh thu[:\s]+(\d+[\d,\.]*)\s*(tỷ|triệu|billion|million)"}
        """
        conflicts = []
        field_values = {field: [] for field in field_patterns}
        
        # Extract values from all chunks
        for chunk in chunks:
            for field_name, pattern in field_patterns.items():
                matches = re.finditer(pattern, chunk.content, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    unit = match.group(2) if len(match.groups()) >= 2 else ""
                    
                    # Normalize value
                    normalized = self._normalize_value(value, unit)
                    
                    field_values[field_name].append((
                        normalized,
                        chunk.chunk_id,
                        chunk.page_numbers[0] if chunk.page_numbers else 0
                    ))
        
        # Detect conflicts
        for field_name, values in field_values.items():
            if len(set(v[0] for v in values)) > 1:  # More than one unique value
                conflict = ConflictInfo(
                    field_name=field_name,
                    values=values,
                    confidence_scores=[1.0] * len(values),  # Can be improved with ML
                    reason="Multiple different values found"
                )
                
                # Resolve: prefer later pages (assuming newer info)
                sorted_values = sorted(values, key=lambda x: x[2], reverse=True)
                conflict.resolution = sorted_values[0][0]
                conflict.reason += f" - Using value from page {sorted_values[0][2]} (most recent)"
                
                conflicts.append(conflict)
                print(f"⚠️ [Conflict] Detected in '{field_name}': {len(values)} different values")
        
        self.conflicts = conflicts
        return conflicts
    
    def _normalize_value(self, value: str, unit: str = "") -> float:
        """Normalize value to comparable format"""
        try:
            # Remove commas, spaces
            clean = value.replace(',', '').replace('.', '').replace(' ', '')
            num = float(clean)
            
            # Apply unit multiplier
            unit_lower = unit.lower()
            if 'tỷ' in unit_lower or 'billion' in unit_lower:
                num *= 1_000_000_000
            elif 'triệu' in unit_lower or 'million' in unit_lower:
                num *= 1_000_000
            elif 'nghìn' in unit_lower or 'thousand' in unit_lower:
                num *= 1_000
            
            return num
        except:
            return 0.0

# ============================================================
# ENHANCED CHUNKING STRATEGY
# ============================================================

class SmartChunker:
    """Intelligent chunking với context preservation"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_document(self, pages: List[PageInfo], doc_id: str) -> List[DocumentChunk]:
        """Chunk document với context links"""
        chunks = []
        
        # Build full text với page markers
        full_text = ""
        page_markers = []  # (position, page_number)
        
        for page in pages:
            page_markers.append((len(full_text), page.page_number))
            full_text += f"\n[PAGE {page.page_number}]\n{page.content}\n"
        
        # Sliding window chunking
        chunk_idx = 0
        position = 0
        
        while position < len(full_text):
            chunk_end = min(position + self.chunk_size, len(full_text))
            chunk_text = full_text[position:chunk_end]
            
            # Find which pages this chunk spans
            chunk_pages = []
            for marker_pos, page_num in page_markers:
                if marker_pos >= position and marker_pos < chunk_end:
                    chunk_pages.append(page_num)
            
            if not chunk_pages and page_markers:
                # Fallback: find closest page
                closest = min(page_markers, key=lambda x: abs(x[0] - position))
                chunk_pages = [closest[1]]
            
            chunk_id = f"{doc_id}_chunk_{chunk_idx}"
            prev_id = f"{doc_id}_chunk_{chunk_idx-1}" if chunk_idx > 0 else None
            
            chunk = DocumentChunk(
                doc_id=doc_id,
                chunk_id=chunk_id,
                content=chunk_text,
                page_numbers=chunk_pages,
                chunk_index=chunk_idx,
                total_chunks=0,  # Will update later
                prev_chunk_id=prev_id,
                created_date=datetime.now().isoformat()
            )
            
            chunks.append(chunk)
            
            # Move window
            position += self.chunk_size - self.overlap
            chunk_idx += 1
        
        # Update total_chunks and next_chunk_id
        for i, chunk in enumerate(chunks):
            chunk.total_chunks = len(chunks)
            if i < len(chunks) - 1:
                chunk.next_chunk_id = chunks[i + 1].chunk_id
        
        print(f"✂️ [Chunk] Created {len(chunks)} chunks for document {doc_id}")
        return chunks

# ============================================================
# EXPORT
# ============================================================

__all__ = [
    'AdvancedPDFExtractor',
    'ConflictDetector',
    'SmartChunker',
    'PageInfo',
    'TableInfo',
    'ImageInfo',
    'DocumentChunk',
    'ConflictInfo'
]
