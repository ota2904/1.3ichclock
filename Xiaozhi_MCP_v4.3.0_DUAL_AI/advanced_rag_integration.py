"""
Integration Module - Tích hợp Advanced RAG vào xiaozhi_final.py
==================================================================
"""

import sys
from pathlib import Path

# Import advanced RAG components
try:
    from advanced_rag import (
        AdvancedPDFExtractor,
        ConflictDetector,
        SmartChunker,
        PageInfo,
        TableInfo,
        ImageInfo,
        DocumentChunk,
        ConflictInfo
    )
    ADVANCED_RAG_AVAILABLE = True
    print("✅ [Advanced RAG] Loaded successfully")
except ImportError as e:
    ADVANCED_RAG_AVAILABLE = False
    print(f"⚠️ [Advanced RAG] Not available: {e}")

# ============================================================
# ENHANCED EXTRACTION FUNCTION
# ============================================================

def extract_text_from_file_enhanced(file_path: str) -> dict:
    """
    Enhanced extraction với full structure support
    
    Returns:
        {
            "success": bool,
            "text": str,  # Plain text for backward compatibility
            "structure": {
                "pages": List[PageInfo],
                "tables": List[TableInfo],
                "images": List[ImageInfo],
                "cross_references": List[str]
            },
            "metadata": dict
        }
    """
    ext = Path(file_path).suffix.lower()
    
    # PDF: Use advanced extractor
    if ext == '.pdf' and ADVANCED_RAG_AVAILABLE:
        extractor = AdvancedPDFExtractor()
        result = extractor.extract_with_structure(file_path)
        
        if result["success"]:
            # Build plain text for backward compatibility
            plain_text = ""
            for page in result["pages"]:
                plain_text += f"\n[PAGE {page.page_number}]\n{page.content}\n"
            
            # Add table content
            for table in result["tables"]:
                plain_text += f"\n[TABLE on page {table.page_number}]\n{table.markdown}\n"
            
            # Add image OCR text
            for image in result["images"]:
                if image.ocr_text:
                    plain_text += f"\n[IMAGE OCR on page {image.page_number}]\n{image.ocr_text}\n"
            
            return {
                "success": True,
                "text": plain_text,
                "structure": {
                    "pages": result["pages"],
                    "tables": result["tables"],
                    "images": result["images"],
                    "cross_references": sum([p.references for p in result["pages"]], [])
                },
                "metadata": result["metadata"]
            }
    
    # Fallback to basic extraction
    try:
        from xiaozhi_final import extract_text_from_file
        text = extract_text_from_file(file_path)
        
        return {
            "success": True,
            "text": text,
            "structure": None,
            "metadata": {}
        }
    except Exception as e:
        return {
            "success": False,
            "text": f"[Error: {str(e)}]",
            "structure": None,
            "metadata": {}
        }

# ============================================================
# ENHANCED INDEXING WITH CONFLICT DETECTION
# ============================================================

async def index_documents_enhanced(files: list, use_conflict_detection: bool = True) -> dict:
    """
    Enhanced indexing với:
    - Smart chunking
    - Conflict detection
    - Full structure preservation
    """
    if not ADVANCED_RAG_AVAILABLE:
        # Fallback to basic indexing
        print("⚠️ [Index] Using basic indexing (Advanced RAG not available)")
        return {"success": False, "error": "Advanced RAG not available"}
    
    chunker = SmartChunker(chunk_size=1000, overlap=200)
    conflict_detector = ConflictDetector()
    
    all_chunks = []
    all_tables = []
    all_images = []
    
    for file_info in files:
        file_path = file_info["path"]
        print(f"📄 [Index] Processing: {file_info['name']}")
        
        # Extract with structure
        extraction = extract_text_from_file_enhanced(file_path)
        
        if not extraction["success"]:
            print(f"❌ [Index] Failed: {file_info['name']}")
            continue
        
        doc_id = hashlib.md5(file_path.encode()).hexdigest()[:16]
        
        # If structure available, use smart chunking
        if extraction["structure"] and extraction["structure"]["pages"]:
            pages = extraction["structure"]["pages"]
            chunks = chunker.chunk_document(pages, doc_id)
            
            # Store tables and images
            all_tables.extend(extraction["structure"]["tables"])
            all_images.extend(extraction["structure"]["images"])
            
            # Mark chunks that contain tables/images
            for chunk in chunks:
                for table in extraction["structure"]["tables"]:
                    if table.page_number in chunk.page_numbers:
                        chunk.has_tables = True
                        chunk.table_ids.append(f"table_{table.page_number}_{table.table_index}")
                
                for image in extraction["structure"]["images"]:
                    if image.page_number in chunk.page_numbers:
                        chunk.has_images = True
                        chunk.image_ids.append(f"image_{image.page_number}_{image.image_index}")
            
            all_chunks.extend(chunks)
            print(f"✅ [Index] Created {len(chunks)} chunks from {len(pages)} pages")
        else:
            # Fallback: basic chunking
            text = extraction["text"]
            # Simple chunking
            chunk_size = 1000
            for i in range(0, len(text), chunk_size - 200):
                chunk_text = text[i:i + chunk_size]
                chunk = DocumentChunk(
                    doc_id=doc_id,
                    chunk_id=f"{doc_id}_chunk_{i//chunk_size}",
                    content=chunk_text,
                    page_numbers=[0],
                    chunk_index=i//chunk_size,
                    total_chunks=(len(text) + chunk_size - 1) // chunk_size
                )
                all_chunks.append(chunk)
    
    # Detect conflicts if enabled
    conflicts = []
    if use_conflict_detection and all_chunks:
        # Define field patterns to check
        field_patterns = {
            "doanh_thu": r"doanh\s*thu[:\s]+(\d+[\d,\.]*)\s*(tỷ|triệu|billion|million)?",
            "lợi_nhuận": r"lợi\s*nhuận[:\s]+(\d+[\d,\.]*)\s*(tỷ|triệu|billion|million)?",
            "năm": r"năm\s+(\d{4})",
            "ngày": r"ngày\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        }
        
        conflicts = conflict_detector.detect_conflicts(all_chunks, field_patterns)
        print(f"🔍 [Conflict] Detected {len(conflicts)} potential conflicts")
    
    return {
        "success": True,
        "chunks": all_chunks,
        "tables": all_tables,
        "images": all_images,
        "conflicts": conflicts,
        "stats": {
            "total_chunks": len(all_chunks),
            "total_tables": len(all_tables),
            "total_images": len(all_images),
            "total_conflicts": len(conflicts)
        }
    }

# ============================================================
# AGGREGATION QUERIES
# ============================================================

class AggregationEngine:
    """Engine for aggregation queries across all chunks"""
    
    @staticmethod
    def count_mentions(chunks: list, keyword: str) -> dict:
        """Count how many times a keyword is mentioned"""
        total_mentions = 0
        pages_mentioned = set()
        chunks_mentioned = []
        
        keyword_lower = keyword.lower()
        
        for chunk in chunks:
            if isinstance(chunk, DocumentChunk):
                count = chunk.content.lower().count(keyword_lower)
                if count > 0:
                    total_mentions += count
                    pages_mentioned.update(chunk.page_numbers)
                    chunks_mentioned.append({
                        "chunk_id": chunk.chunk_id,
                        "page_numbers": chunk.page_numbers,
                        "count": count
                    })
        
        return {
            "keyword": keyword,
            "total_mentions": total_mentions,
            "pages_with_mentions": sorted(list(pages_mentioned)),
            "total_pages": len(pages_mentioned),
            "chunks": chunks_mentioned[:10]  # Top 10
        }
    
    @staticmethod
    def extract_all_dates(chunks: list) -> dict:
        """Extract and sort all dates mentioned"""
        import re
        from datetime import datetime
        
        dates = []
        date_patterns = [
            r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}',  # DD/MM/YYYY
            r'\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}',  # YYYY/MM/DD
            r'ngày\s+\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}',  # Vietnamese
        ]
        
        for chunk in chunks:
            if isinstance(chunk, DocumentChunk):
                for pattern in date_patterns:
                    matches = re.finditer(pattern, chunk.content, re.IGNORECASE)
                    for match in matches:
                        date_str = match.group(0)
                        dates.append({
                            "date_string": date_str,
                            "chunk_id": chunk.chunk_id,
                            "page_numbers": chunk.page_numbers
                        })
        
        # Remove duplicates and sort
        unique_dates = list({d["date_string"]: d for d in dates}.values())
        
        return {
            "total_dates": len(unique_dates),
            "dates": sorted(unique_dates, key=lambda x: x["date_string"]),
            "summary": f"Found {len(unique_dates)} unique dates across documents"
        }
    
    @staticmethod
    def list_all_projects(chunks: list) -> dict:
        """List all projects mentioned"""
        import re
        
        projects = set()
        project_patterns = [
            r'dự\s*án\s+([A-Z][A-Za-z0-9\s]{3,30})',
            r'project\s+([A-Z][A-Za-z0-9\s]{3,30})',
        ]
        
        for chunk in chunks:
            if isinstance(chunk, DocumentChunk):
                for pattern in project_patterns:
                    matches = re.finditer(pattern, chunk.content, re.IGNORECASE)
                    for match in matches:
                        project_name = match.group(1).strip()
                        if len(project_name) > 3:
                            projects.add(project_name)
        
        return {
            "total_projects": len(projects),
            "projects": sorted(list(projects)),
            "summary": f"Found {len(projects)} unique projects"
        }

# ============================================================
# EXPORT
# ============================================================

__all__ = [
    'extract_text_from_file_enhanced',
    'index_documents_enhanced',
    'AggregationEngine',
    'ADVANCED_RAG_AVAILABLE'
]
