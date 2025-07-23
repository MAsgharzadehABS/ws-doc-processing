import os
import json
from dotenv import load_dotenv
from tools.pdf_text_parser import parse_multiple_pdfs
from tools.pdf_field_extractor import OpenAIDataExtractor, test_azure_openai_connection

# Load environment variables
load_dotenv()

def main():
    """
    Main processing pipeline for PDF parsing and field data extraction.
    Optimized for scanned documents with poor quality using OCR.
    """
    print("🔍 Field Data Extraction Pipeline")
    print("📄 Optimized for scanned documents with poor quality")
    print("=" * 60)
    
    # Configuration
    PDF_DIRECTORY = "test"  # Directory containing PDFs
    PARSED_DIRECTORY = "test-parsed"  # Directory to save parsed text files
    EXTRACT_DIRECTORY = "test-extract"  # Directory to save extracted JSON files
    
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
    
    # Step 1: Parse PDFs to text files using OCR
    print(f"\n📄 Step 1: Extracting text from scanned PDFs using OCR...")
    print("⏱️  Note: OCR processing may take several minutes for poor quality scans")
    print("-" * 50)
    
    try:
        parsing_results = parse_multiple_pdfs(PDF_DIRECTORY, PARSED_DIRECTORY)
        
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
        
        if successful_parses == 0:
            print("❌ No PDFs were successfully parsed. Cannot proceed with data extraction.")
            print("💡 Tip: Ensure Tesseract OCR is installed and PDFs contain readable text")
            return
            
    except Exception as e:
        print(f"❌ Error during PDF parsing: {e}")
        return
    
    # Step 2: Extract contact information data using Azure OpenAI
    print(f"\n🤖 Step 2: Extracting contact information data using Azure OpenAI...")
    print("-" * 50)
    
    try:
        extractor = OpenAIDataExtractor()
        extraction_results = extractor.process_all_parsed_texts(PARSED_DIRECTORY, EXTRACT_DIRECTORY)
        
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
        
        # Save consolidated results
        consolidated_file = os.path.join(EXTRACT_DIRECTORY, "contact_information_extraction_results.json")
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(extraction_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📁 Files and Results:")
        print(f"   📄 Parsed text files: {os.path.abspath(PARSED_DIRECTORY)}")
        print(f"   📊 Extracted JSON files: {os.path.abspath(EXTRACT_DIRECTORY)}")
        print(f"   🗃️ Consolidated results: {consolidated_file}")
        
        # Show extracted data files
        data_files = [f for f in os.listdir(EXTRACT_DIRECTORY) if f.endswith('_contact_information_data.json')]
        print(f"   📋 Individual data files (preserving original PDF names):")
        for data_file in data_files:
            # Show original PDF name reference
            original_name = data_file.replace('_contact_information_data.json', '.pdf')
            print(f"     - {data_file} (from {original_name})")
        
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
            
            # Display extracted data
            extracted_data = extraction_result.get("extracted_data", {})
            print(f"\n📋 Extracted Contact Information Data from {original_filename}:")
            print("-" * 50)
            for field, value in extracted_data.items():
                print(f"   {field}: {value}")
                
            output_file = extraction_result.get("output_file", "")
            if output_file:
                output_filename = os.path.basename(output_file)
                print(f"\n💾 Data saved as: {output_filename}")
                print(f"📁 Location: test-extract/")
        else:
            print(f"❌ Extraction failed: {extraction_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during extraction: {e}")


if __name__ == "__main__":
    # Run the main processing pipeline
    main()








