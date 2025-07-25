import os
import json
import datetime
from multiprocessing import Pool, cpu_count
from functools import partial
from dotenv import load_dotenv
from tools.pdf_text_parser import parse_multiple_pdfs, PDFTextParser
from tools.pdf_field_extractor import OpenAIDataExtractor, test_azure_openai_connection
from tqdm import tqdm

# Configuration
ROOT_DIRECTORY = "files"
PDF_DIRECTORY = f"{ROOT_DIRECTORY}/raw_inputs"  # Directory containing PDFs
PARSED_DIRECTORY = f"{ROOT_DIRECTORY}/parsed"  # Directory to save parsed text files
EXTRACT_DIRECTORY = f"{ROOT_DIRECTORY}/extracted"  # Directory to save extracted JSON files
MAX_PROCESSES = 36 #cpu_count()  # Maximum number of processes to use (defaults to CPU count)

# Load environment variables
load_dotenv()

def parse_single_pdf_wrapper(args):
    """
    Wrapper function for parsing a single PDF file - compatible with multiprocessing.
    
    Args:
        args (tuple): (pdf_file, pdf_directory, output_dir)
        
    Returns:
        dict: Result dictionary with parsing information
    """
    pdf_file, pdf_directory, output_dir = args
    pdf_path = os.path.join(pdf_directory, pdf_file)
    
    try:
        parser = PDFTextParser()
        result = parser.parse_and_save(pdf_path, output_dir)
        return result
    except Exception as e:
        return {
            "pdf_path": pdf_path,
            "filename": pdf_file,
            "error": str(e),
            "success": False
        }

def extract_single_text_wrapper(args):
    """
    Wrapper function for extracting data from a single text file - compatible with multiprocessing.
    
    Args:
        args (tuple): (text_file, parsed_dir, output_dir)
        
    Returns:
        dict: Result dictionary with extraction information
    """
    text_file, parsed_dir, output_dir = args
    text_file_path = os.path.join(parsed_dir, text_file)
    
    try:
        extractor = OpenAIDataExtractor()
        result = extractor.process_parsed_text_file(text_file_path, output_dir)
        return result
    except Exception as e:
        return {
            "text_file": text_file_path,
            "filename_base": text_file.replace('.txt', ''),
            "error": str(e),
            "success": False
        }

def main():
    """
    Main processing pipeline for PDF parsing and field data extraction.
    Optimized for scanned documents with poor quality using OCR.
    
    Features:
    - Multiprocessing support for parallel PDF parsing and data extraction
    - Automatic process count optimization based on CPU cores and file count
    - Enhanced performance for batch processing multiple documents
    """
    print("🔍 Field Data Extraction Pipeline")
    print("📄 Optimized for scanned documents with poor quality")
    print("=" * 60)
    
    
    # Check if test directory exists
    if not os.path.exists(PDF_DIRECTORY):
        print(f"❌ Error: PDF directory '{PDF_DIRECTORY}' not found!")
        return
    
    # List PDF files
    pdf_files = [f for f in os.listdir(PDF_DIRECTORY) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in '{PDF_DIRECTORY}' directory!")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF files:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"   {i}. {pdf_file}")
    
    print(f"\n🔧 Configuration:")
    print(f"   📁 Input Directory: {PDF_DIRECTORY}")
    print(f"   📁 Parsed Text Directory: {PARSED_DIRECTORY}")
    print(f"   📁 Extracted Data Directory: {EXTRACT_DIRECTORY}")
    print(f"   🔍 Extraction Method: OCR (Tesseract) - optimized for scanned documents")
    print(f"   📝 Filename Preservation: Original PDF names maintained")
    print(f"   🚀 Multiprocessing: Enabled with up to {MAX_PROCESSES} parallel processes")
    
    # Test Azure OpenAI connection
    print(f"\n🔌 Testing Azure OpenAI Connection...")
    if test_azure_openai_connection():
        print("   ✅ Azure OpenAI connection successful")
    else:
        print("   ❌ Azure OpenAI connection failed")
        print("   Please check your OPENAI_ENDPOINT and OPENAI_KEY in .env file")
        return
    
    print(f"\n🚀 Starting PDF processing pipeline...")
    print("=" * 60)
    
    # Step 1: Parse PDFs to text files using OCR (with multiprocessing)
    print(f"\n📄 Step 1: Extracting text from scanned PDFs using OCR...")
    print("⏱️  Note: OCR processing may take several minutes for poor quality scans")
    print(f"🚀 Using multiprocessing with {min(MAX_PROCESSES, len(pdf_files))} processes for parallel processing")
    print("-" * 50)
    
    try:
        # Prepare arguments for multiprocessing
        parse_args = [(pdf_file, PDF_DIRECTORY, PARSED_DIRECTORY) for pdf_file in pdf_files]
        
        # Use multiprocessing Pool for parallel PDF parsing
        with Pool(processes=min(MAX_PROCESSES, len(pdf_files))) as pool:
            parsing_results = list(tqdm(pool.imap(parse_single_pdf_wrapper, parse_args), total=len(parse_args), desc="PDF Parsing"))
        
        successful_parses = 0
        failed_parses = 0
        
        for result in parsing_results:
            if result.get("success"):
                print(f"✅ {result['filename']}: {result['text_length']:,} chars extracted via OCR")
                successful_parses += 1
            else:
                print(f"❌ {result['filename']}: {result.get('error', 'Unknown error')}")
                failed_parses += 1
        
        print(f"\n📊 OCR Parsing Summary:")
        print(f"   ✅ Successfully parsed: {successful_parses}")
        print(f"   ❌ Failed to parse: {failed_parses}")
        print(f"   🚀 Processed with {min(MAX_PROCESSES, len(pdf_files))} parallel processes")
        
        if successful_parses == 0:
            print("❌ No PDFs were successfully parsed. Cannot proceed with data extraction.")
            print("💡 Tip: Ensure Tesseract OCR is installed and PDFs contain readable text")
            return
            
    except Exception as e:
        print(f"❌ Error during PDF parsing: {e}")
        return
    
    # Step 2: Extract contact information data using Azure OpenAI (with multiprocessing)
    print(f"\n🤖 Step 2: Extracting contact information data using Azure OpenAI...")
    print("-" * 50)
    
    try:
        # Find all text files (excluding info files)
        text_files = [
            f for f in os.listdir(PARSED_DIRECTORY) 
            if f.endswith('.txt') and not f.endswith('_info.txt')
        ]
        
        if not text_files:
            print(f"❌ No text files found in {PARSED_DIRECTORY}")
            return
        
        print(f"🚀 Using multiprocessing with {min(MAX_PROCESSES, len(text_files))} processes for parallel data extraction")
        
        # Create output directory if it doesn't exist
        os.makedirs(EXTRACT_DIRECTORY, exist_ok=True)
        
        # Prepare arguments for multiprocessing
        extract_args = [(text_file, PARSED_DIRECTORY, EXTRACT_DIRECTORY) for text_file in text_files]
        
        # Use multiprocessing Pool for parallel data extraction
        with Pool(processes=min(MAX_PROCESSES, len(text_files))) as pool:
            extraction_results = pool.map(extract_single_text_wrapper, extract_args)
        
        successful_extractions = 0
        failed_extractions = 0
        
        for result in extraction_results:
            if result.get("success"):
                print(f"✅ {result['filename_base']}: Contact information data extracted successfully")
                successful_extractions += 1
                
            else:
                print(f"❌ {result.get('filename_base', 'Unknown')}: {result.get('error', 'Unknown error')}")
                failed_extractions += 1
        
        print(f"📊 Extraction Summary:")
        print(f"   ✅ Successfully extracted: {successful_extractions}")
        print(f"   ❌ Failed to extract: {failed_extractions}")
        print(f"   🚀 Processed with {min(MAX_PROCESSES, len(text_files))} parallel processes")
        
        # Save consolidated results with enhanced metadata
        consolidated_file = os.path.join(ROOT_DIRECTORY, "contact_information_extraction_results.json")
        
        # Enhance consolidated results with metadata summary
        enhanced_consolidated_results = {
            "processing_summary": {
                "total_files_processed": len(pdf_files),
                "successful_extractions": successful_extractions,
                "failed_extractions": failed_extractions,
                "processing_timestamp": datetime.datetime.now().isoformat(),
                "input_directory": PDF_DIRECTORY,
                "parsed_directory": PARSED_DIRECTORY,
                "extract_directory": EXTRACT_DIRECTORY
            },
            "individual_results": extraction_results
        }
        
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_consolidated_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📁 Files and Results:")
        print(f"   📄 Parsed text files: {os.path.abspath(PARSED_DIRECTORY)}")
        print(f"   📊 Extracted JSON files: {os.path.abspath(EXTRACT_DIRECTORY)}")
        print(f"   🗃️ Enhanced consolidated results: {consolidated_file}")
        
        # Show extracted data files with metadata info
        data_files = [f for f in os.listdir(EXTRACT_DIRECTORY) if f.endswith('_contact_information_data.json')]
        print(f"   📋 Individual data files (with metadata & original filenames):")
        for data_file in data_files:
            # Show original PDF name reference
            original_name = data_file.replace('_contact_information_data.json', '.pdf')
            print(f"     - {data_file} (from {original_name})")
            # Try to show original filename from metadata if available
            try:
                data_file_path = os.path.join(EXTRACT_DIRECTORY, data_file)
                with open(data_file_path, 'r', encoding='utf-8') as f:
                    data_content = json.load(f)
                    if 'document_metadata' in data_content and 'original_filename' in data_content['document_metadata']:
                        original_from_metadata = data_content['document_metadata']['original_filename']
                        if original_from_metadata:
                            print(f"       ✓ Metadata preserved: {original_from_metadata}")
            except Exception:
                pass
        
    except Exception as e:
        print(f"❌ Error during contact information data extraction: {e}")
        return
    
    print(f"\n🎉 Contact information data extraction pipeline completed!")
    print(f"✅ Successfully processed {successful_extractions} out of {len(pdf_files)} PDF documents")
    print(f"📝 All output files preserve original PDF naming for easy reference")


def process_single_pdf(pdf_path: str):
    """
    Process a single PDF file through the complete pipeline.
    Uses OCR extraction for scanned documents.
    
    Args:
        pdf_path (str): Path to the PDF file
    """
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    original_filename = os.path.basename(pdf_path)
    print(f"🔍 Processing single PDF: {original_filename}")
    print(f"🔍 Using OCR extraction for scanned document")
    
    # Step 1: Parse PDF to text using OCR
    from tools.pdf_text_parser import PDFTextParser
    parser = PDFTextParser()
    
    print("📄 Step 1: Extracting text using OCR...")
    parse_result = parser.parse_and_save(pdf_path, "test-parsed")
    
    if not parse_result.get("success"):
        print(f"❌ Failed to extract text: {parse_result.get('error', 'Unknown error')}")
        return
    
    print(f"✅ Extracted {parse_result['text_length']:,} characters using OCR")
    print(f"📝 Saved as: {parse_result['filename_base']}.txt (preserving original name)")
    
    # Step 2: Extract contact information data
    print("🤖 Step 2: Extracting contact information data...")
    
    try:
        extractor = OpenAIDataExtractor()
        extraction_result = extractor.process_parsed_text_file(parse_result['text_file'], "test-extract")
        
        if extraction_result.get("success"):
            print("✅ Contact information data extraction completed!")
            
            # Display extracted data with metadata
            extracted_data = extraction_result.get("extracted_data", {})
            print(f"\n📋 Extracted Contact Information Data from {original_filename}:")
            print("-" * 50)
            
            # Show metadata if available
            if isinstance(extracted_data, dict) and "document_metadata" in extracted_data:
                metadata = extracted_data["document_metadata"]
                print(f"📄 Original Filename: {metadata.get('original_filename', 'N/A')}")
                print(f"📅 Processing Timestamp: {metadata.get('extraction_processing_timestamp', 'N/A')}")
                print(f"🔧 Extraction Method: {metadata.get('extraction_method', 'N/A')}")
                print(f"📏 Text Length: {metadata.get('text_length', 'N/A')}")
                print("-" * 50)
                
                # Show extracted fields
                if "extracted_fields" in extracted_data:
                    fields_data = extracted_data["extracted_fields"]
                    for field, value in fields_data.items():
                        print(f"   {field}: {value}")
                else:
                    for field, value in extracted_data.items():
                        if field != "document_metadata":
                            print(f"   {field}: {value}")
            else:
                # Fallback for old format
                for field, value in extracted_data.items():
                    print(f"   {field}: {value}")
                
            output_file = extraction_result.get("output_file", "")
            if output_file:
                output_filename = os.path.basename(output_file)
                print(f"\n💾 Enhanced data with metadata saved as: {output_filename}")
                print(f"📁 Location: test-extract/")
                print(f"✅ Original filename preserved in metadata")
        else:
            print(f"❌ Extraction failed: {extraction_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")


if __name__ == "__main__":
    # Run the main processing pipeline
    main()








