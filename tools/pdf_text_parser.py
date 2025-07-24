import os
import logging
from typing import Dict, List, Optional
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
from pathlib import Path
import datetime
import cv2
import random
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the Poppler path
POPPLER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "poppler", "poppler-23.08.0", "Library", "bin")

class PDFTextParser:
    """
    A focused PDF text parser that extracts text using OCR for scanned documents
    and saves results to the test-parsed/ directory with original filenames.
    Enhanced with advanced image preprocessing for poor quality handwritten documents.
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
    
    def preprocess_image_for_ocr(self, image):
        """
        Apply advanced image preprocessing to improve OCR accuracy on poor quality handwritten documents.
        
        Args:
            image: PIL Image object
            
        Returns:
            PIL Image: Preprocessed image optimized for OCR
        """
        try:
            # Convert PIL Image to OpenCV format
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding for better binarization
            # This works better than simple thresholding for uneven lighting
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            # Remove small noise
            kernel = np.ones((1, 1), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Close small gaps in characters
            kernel = np.ones((2, 2), np.uint8)
            closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # Dilation to make text slightly thicker (helpful for thin handwriting)
            kernel = np.ones((1, 1), np.uint8)
            dilated = cv2.dilate(closing, kernel, iterations=1)
            
            # Apply median filter to reduce remaining noise
            filtered = cv2.medianBlur(dilated, 3)
            
            # Optional: Sharpen the image
            kernel_sharpen = np.array([[-1,-1,-1],
                                      [-1, 9,-1],
                                      [-1,-1,-1]])
            sharpened = cv2.filter2D(filtered, -1, kernel_sharpen)
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(sharpened)
            
            # Enhance contrast and brightness using PIL
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(1.5)  # Increase contrast
            
            enhancer = ImageEnhance.Brightness(processed_image)
            processed_image = enhancer.enhance(1.1)  # Slightly increase brightness
            
            # Resize image for better OCR (tesseract works better on larger images)
            width, height = processed_image.size
            if width < 300 or height < 300:
                scale_factor = max(300/width, 300/height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                processed_image = processed_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original image: {e}")
            return image
    
    def extract_text_with_multiple_configs(self, processed_image):
        """
        Try multiple OCR configurations and return the best result based on confidence.
        
        Args:
            processed_image: PIL Image object (preprocessed)
            
        Returns:
            str: Best OCR result
        """
        # Multiple OCR configurations to try
        configs = [
            r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-_/()[]@%+&',
            r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-_/()[]@%+&',
            r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-_/()[]@%+&',
            r'--oem 3 --psm 13 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-_/()[]@%+&',
        ]
        
        best_text = ""
        best_confidence = 0
        
        for i, config in enumerate(configs):
            try:
                # Get OCR result with confidence scores
                data = pytesseract.image_to_data(
                    processed_image, 
                    config=config,
                    lang='eng',
                    output_type=pytesseract.Output.DICT
                )
                
                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_text = pytesseract.image_to_string(
                            processed_image, 
                            config=config,
                            lang='eng'
                        )
                        logger.debug(f"Config {i+1} achieved confidence: {avg_confidence:.2f}")
            except Exception as e:
                logger.debug(f"Config {i+1} failed: {e}")
                continue
        
        # Fallback to original configuration if none worked well
        if not best_text.strip():
            logger.warning("All advanced configs failed, falling back to default")
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-_/()[]@%+&'
            best_text = pytesseract.image_to_string(
                processed_image, 
                config=custom_config,
                lang='eng'
            )
        else:
            logger.debug(f"Best OCR result with confidence: {best_confidence:.2f}")
        
        return best_text
    
    def extract_text_ocr(self, pdf_path: str, output_dir: Optional[str] = None, filename_base: Optional[str] = None) -> str:
        """
        Extract text using OCR with advanced preprocessing (optimized for scanned PDFs with poor quality).
        
        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str): Directory to save processed images (optional)
            filename_base (str): Base filename for saving processed images (optional)
            
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
            
            logger.info(f"Processing {total_pages} pages with enhanced OCR preprocessing...")
            
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{total_pages}")
                
                # Apply advanced image preprocessing
                processed_image = self.preprocess_image_for_ocr(image)

                # Save the processed image if output directory and filename are provided
                if output_dir and filename_base:
                    try:
                        os.makedirs(output_dir, exist_ok=True)
                        if total_pages == 1:
                            # Single page PDF - save without page number
                            processed_image_path = os.path.join(output_dir, f"{filename_base}_processed.png")
                        else:
                            # Multi-page PDF - include page number
                            processed_image_path = os.path.join(output_dir, f"{filename_base}_processed_page_{i+1}.png")
                        
                        processed_image.save(processed_image_path, "PNG")
                        logger.info(f"Saved processed image to: {processed_image_path}")
                    except Exception as e:
                        logger.warning(f"Failed to save processed image for page {i+1}: {e}")

                # Extract text using multiple configurations
                page_text = self.extract_text_with_multiple_configs(processed_image)
                
                # Post-processing to clean up common OCR errors
                if page_text.strip():
                    # Remove excessive whitespace
                    page_text = ' '.join(page_text.split())
                    
                    # Optional: Apply common OCR error corrections here if needed
                    # page_text = self.apply_ocr_corrections(page_text)
                    
                    text += f"--- Page {i+1} ---\n{page_text.strip()}\n\n"
            
            logger.info(f"Enhanced OCR extraction completed. Extracted {len(text)} characters from {total_pages} pages")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract text with enhanced OCR from {pdf_path}: {e}")
            return ""
    
    def parse_and_save(self, pdf_path: str, output_dir: str = "test-parsed") -> Dict:
        """
        Parse PDF using enhanced OCR and save extracted text to the specified directory.
        Preserves the original PDF filename and includes comprehensive metadata.
        
        Args:
            pdf_path (str): Path to the PDF file
            output_dir (str): Directory to save parsed text files
            
        Returns:
            Dict: Parsing results with metadata
        """
        logger.info(f"Starting enhanced OCR text extraction for: {pdf_path}")
        
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
        
        # Extract text using enhanced OCR
        extracted_text = self.extract_text_ocr(pdf_path, output_dir, filename_base)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            logger.warning(f"No meaningful text could be extracted from {pdf_path}")
            return {
                "pdf_path": pdf_path,
                "filename": original_filename,
                "filename_base": filename_base,
                "error": "No meaningful text extracted via enhanced OCR",
                "success": False
            }
        
        # Get file metadata
        file_stats = os.stat(pdf_path)
        processing_timestamp = datetime.datetime.now().isoformat()
        
        # Create comprehensive metadata header
        metadata_header = f"""=== DOCUMENT METADATA ===
Original Filename: {original_filename}
Original File Path: {pdf_path}
File Size: {file_stats.st_size} bytes
File Modified: {datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()}
Processing Timestamp: {processing_timestamp}
Extraction Method: Enhanced OCR (Tesseract with Advanced Preprocessing)
OCR Configuration: Multiple PSM modes with confidence-based selection
Image Preprocessing: Gaussian blur, adaptive thresholding, morphological operations, sharpening, contrast/brightness enhancement
Text Length: {len(extracted_text)} characters
Parser Version: PDFTextParser v2.0 (Enhanced)
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
                f.write(f"Extraction method: Enhanced OCR (Tesseract)\n")
                f.write(f"Image preprocessing: Advanced multi-step preprocessing pipeline\n")
                f.write(f"OCR configurations: Multiple PSM modes with confidence scoring\n")
                f.write(f"Text length: {len(extracted_text)} characters\n")
                f.write(f"Processing: Optimized for poor quality handwritten scanned documents\n")
                f.write(f"Features: Gaussian blur, adaptive thresholding, morphological operations, sharpening, contrast enhancement\n")
                f.write(f"Parser version: PDFTextParser v2.0 (Enhanced)\n")
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
            "extraction_method": "Enhanced OCR",
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
    Parse multiple PDF files using enhanced OCR and save their text content.
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
    
    logger.info(f"Found {len(pdf_files)} PDF files to process with enhanced OCR")
    logger.info("Note: Processing scanned documents with advanced preprocessing - this may take additional time but should provide better results")
    
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
    
    logger.info(f"\n=== Enhanced OCR Processing Summary ===")
    logger.info(f"Total files: {len(pdf_files)}")
    logger.info(f"Successfully processed: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Enhancement features: Advanced image preprocessing, multiple OCR configurations, confidence-based selection")
    
    return results