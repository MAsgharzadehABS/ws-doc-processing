import os
import logging
from typing import Dict, List
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Poppler path
POPPLER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "poppler", "poppler-23.08.0", "Library", "bin")

class PDFTextParser:
    """
    A focused PDF text parser that extracts text using OCR for scanned documents
    and saves results to the test-parsed/ directory with original filenames.
    """
    
    def __init__(self):
        """Initialize the PDF Text Parser."""
        # Check if Poppler binaries are available
        poppler_exe = os.path.join(POPPLER_PATH, "pdftoppm.exe")
        if not os.path.exists(poppler_exe):
            logger.error(f"Poppler not found at {POPPLER_PATH}")
            logger.error("Please ensure Poppler is installed in the poppler/ directory")
            raise RuntimeError("Poppler binaries are required for PDF processing")
        else:
            logger.info(f"Found Poppler at: {POPPLER_PATH}")
        
        # Ensure tesseract is available
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except Exception as e:
            logger.error(f"Tesseract OCR not available: {e}")
            logger.error("Please install Tesseract OCR to process scanned PDF documents")
            raise RuntimeError("Tesseract OCR is required for processing scanned documents")
    
    def extract_text_ocr(self, pdf_path: str) -> str:
        """
        Extract text using OCR (optimized for scanned PDFs with poor quality).
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            str: Extracted text from OCR
        """
        try:
            logger.info(f"Converting PDF to images for OCR: {pdf_path}")
            
            # Convert PDF to images with higher DPI for better OCR accuracy
            images = convert_from_path(
                pdf_path, 
                dpi=300,  # Higher DPI for better quality
                fmt='PNG',  # PNG format for better quality
                poppler_path=POPPLER_PATH  # Specify Poppler binaries path
            )
            
            text = ""
            total_pages = len(images)
            
            logger.info(f"Processing {total_pages} pages with OCR...")
            
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{total_pages}")
                
                # Enhanced OCR configuration for poor quality scanned documents
                custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-_/()[]@%+&'
                
                # Perform OCR on each page
                page_text = pytesseract.image_to_string(
                    image, 
                    config=custom_config,
                    lang='eng'  # Specify English language
                )
                
                if page_text.strip():  # Only add non-empty pages
                    text += f"--- Page {i+1} ---\n{page_text.strip()}\n\n"
            
            logger.info(f"OCR extraction completed. Extracted {len(text)} characters from {total_pages} pages")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text with OCR from {pdf_path}: {e}")
            return ""
    
    def parse_and_save(self, pdf_path: str, output_dir: str = "test-parsed") -> Dict:
        """
        Parse PDF using OCR and save extracted text to the specified directory.
        Preserves the original PDF filename and includes comprehensive metadata.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str): Directory to save parsed text files
            
        Returns:
            Dict: Parsing results with metadata
        """
        logger.info(f"Starting OCR text extraction for: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return {"error": "File not found", "success": False}
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Get original filename without extension (preserving special characters)
        original_filename = os.path.basename(pdf_path)
        filename_base = os.path.splitext(original_filename)[0]
        
        logger.info(f"Processing file: {original_filename}")
        logger.info(f"Base name for output: {filename_base}")
        
        # Extract text using OCR
        extracted_text = self.extract_text_ocr(pdf_path)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            logger.warning(f"No meaningful text could be extracted from {pdf_path}")
            return {
                "pdf_path": pdf_path,
                "filename": original_filename,
                "filename_base": filename_base,
                "error": "No meaningful text extracted via OCR",
                "success": False
            }
        
        # Get file metadata
        import datetime
        file_stats = os.stat(pdf_path)
        processing_timestamp = datetime.datetime.now().isoformat()
        
        # Create comprehensive metadata header
        metadata_header = f"""=== DOCUMENT METADATA ===
Original Filename: {original_filename}
Original File Path: {pdf_path}
File Size: {file_stats.st_size} bytes
File Modified: {datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()}
Processing Timestamp: {processing_timestamp}
Extraction Method: OCR (Tesseract)
OCR Configuration: Enhanced for poor quality scanned documents
Text Length: {len(extracted_text)} characters
Parser Version: PDFTextParser v1.0
=== END METADATA ===

=== EXTRACTED TEXT CONTENT ===
"""
        
        # Combine metadata header with extracted text
        final_content = metadata_header + extracted_text + "\n\n=== END DOCUMENT ==="
        
        # Save the extracted text with original filename and metadata
        text_file_path = os.path.join(output_dir, f"{filename_base}.txt")
        try:
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            logger.info(f"Saved extracted text with metadata to: {text_file_path}")
        except Exception as e:
            logger.error(f"Failed to save text file: {e}")
            return {
                "pdf_path": pdf_path,
                "filename": original_filename,
                "error": f"Failed to save text file: {e}",
                "success": False
            }
        
        # Save extraction method info (enhanced)
        info_file_path = os.path.join(output_dir, f"{filename_base}_info.txt")
        try:
            with open(info_file_path, 'w', encoding='utf-8') as f:
                f.write(f"=== PROCESSING INFORMATION ===\n")
                f.write(f"Original PDF: {pdf_path}\n")
                f.write(f"Original filename: {original_filename}\n")
                f.write(f"File size: {file_stats.st_size} bytes\n")
                f.write(f"File modified: {datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()}\n")
                f.write(f"Processing timestamp: {processing_timestamp}\n")
                f.write(f"Extraction method: OCR (Tesseract)\n")
                f.write(f"Text length: {len(extracted_text)} characters\n")
                f.write(f"Processing: Optimized for poor quality scanned documents\n")
                f.write(f"OCR settings: Enhanced configuration with character whitelist\n")
                f.write(f"Parser version: PDFTextParser v1.0\n")
                f.write(f"Output file: {text_file_path}\n")
            logger.info(f"Saved processing info to: {info_file_path}")
        except Exception as e:
            logger.warning(f"Failed to save info file: {e}")
        
        result = {
            "pdf_path": pdf_path,
            "filename": original_filename,
            "filename_base": filename_base,
            "text_file": text_file_path,
            "info_file": info_file_path,
            "extraction_method": "OCR",
            "text_length": len(extracted_text),
            "file_size": file_stats.st_size,
            "processing_timestamp": processing_timestamp,
            "success": True
        }
        
        logger.info(f"Successfully processed {original_filename}")
        logger.info(f"Text file: {text_file_path}")
        logger.info(f"Text length: {len(extracted_text)} characters")
        
        return result


def parse_multiple_pdfs(pdf_directory: str, output_dir: str = "test-parsed") -> List[Dict]:
    """
    Parse multiple PDF files using OCR and save their text content.
    Preserves original PDF filenames.
    
    Args:
        pdf_directory (str): Directory containing PDF files
        output_dir (str): Directory to save parsed text files
        
    Returns:
        List[Dict]: Results for each processed PDF
    """
    parser = PDFTextParser()
    results = []
    
    if not os.path.exists(pdf_directory):
        logger.error(f"Directory not found: {pdf_directory}")
        return results
    
    # Find all PDF files
    pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_directory}")
        return results
    
    logger.info(f"Found {len(pdf_files)} PDF files to process with OCR")
    logger.info("Note: Processing scanned documents with poor quality - this may take some time")
    
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_path = os.path.join(pdf_directory, pdf_file)
        logger.info(f"\n=== Processing {i}/{len(pdf_files)}: {pdf_file} ===")
        
        try:
            result = parser.parse_and_save(pdf_path, output_dir)
            results.append(result)
            
            if result.get("success"):
                logger.info(f"✅ Successfully processed: {pdf_file}")
            else:
                logger.warning(f"⚠️ Failed to process: {pdf_file} - {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Error processing {pdf_file}: {e}")
            results.append({
                "pdf_path": pdf_path,
                "filename": pdf_file,
                "error": str(e),
                "success": False
            })
    
    # Summary
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    
    logger.info(f"\n=== OCR Processing Summary ===")
    logger.info(f"Total files: {len(pdf_files)}")
    logger.info(f"Successfully processed: {successful}")
    logger.info(f"Failed: {failed}")
    
    return results