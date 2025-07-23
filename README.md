# Document Processing System with Enhanced Metadata

A comprehensive system for processing PDF documents using OCR and Azure OpenAI for structured contact information extraction. **Features enhanced metadata preservation throughout the entire processing pipeline.**

## 🚀 Features

- **📄 OCR Text Extraction**: Uses Tesseract OCR optimized for poor quality scanned documents
- **🤖 Azure OpenAI Integration**: Leverages Azure OpenAI for intelligent contact information extraction
- **📋 Contact Information Specialization**: Specifically designed to extract contact information and delivery data fields
- **📦 Batch Processing**: Process multiple PDF documents at once with progress tracking
- **📊 Structured Output**: Generates clean JSON output with standardized fields and comprehensive metadata
- **🏷️ Enhanced Metadata Preservation**: **NEW!** Complete metadata tracking including original filenames, processing timestamps, file sizes, and extraction methods
- **🔍 Full Traceability**: Every output file can be traced back to its original source with complete audit trail
- **📝 Filename Preservation**: Maintains original PDF filenames throughout all processing stages

## 🏗️ System Architecture

The system works in two main steps with **enhanced metadata tracking**:

1. **📄 PDF OCR Extraction**: Extract text from scanned PDFs using Tesseract OCR and save to `test-parsed/` folder **with comprehensive metadata headers**
2. **🤖 Data Extraction**: Use Azure OpenAI to extract structured contact information data **with preserved source metadata**

## 🛠️ Installation

### Prerequisites

#### 1. **Poppler Utils** (Required for PDF to image conversion)

**Windows Installation:**

1. **Download Poppler for Windows:**
   - Go to: https://github.com/oschwartz10612/poppler-windows/releases/
   - Download the latest release (e.g., `Release-24.08.0-0.zip`)

2. **Extract Poppler:**
   - Create a `poppler/` directory in your project root
   - Extract the downloaded ZIP file into the `poppler/` directory
   - Your structure should look like: `poppler/poppler-24.08.0/Library/bin/`

3. **Verify Poppler Installation:**
   The system will automatically detect Poppler in the `poppler/` directory. You should see files like:
   ```
   poppler/
   └── poppler-24.08.0/
       └── Library/
           └── bin/
               ├── pdftoppm.exe
               ├── pdfinfo.exe
               └── other poppler tools...
   ```

#### 2. **Tesseract OCR** (Required for scanned document processing)

**Installing Tesseract OCR on Windows:**

1. **Download Tesseract installer:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-v5.3.3.20231005.exe`)

2. **Install Tesseract:**
   - Run the installer as Administrator
   - During installation, note the installation path (usually `C:\Program Files\Tesseract-OCR\`)
   - Make sure to check "Add to PATH" during installation

3. **Verify installation:**
   ```bash
   tesseract --version
   ```

### Python Environment Setup

1. Clone the repository and navigate to the project directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Create a `.env` file in the project root with your Azure configuration:

```env
# Azure Blob Storage Configuration (optional)
SAS_TOKEN=your_sas_token_here
CONTAINER_NAME=your_container_name_here

# Azure OpenAI Configuration (required)
OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
OPENAI_KEY=your_azure_openai_api_key_here
```

## 🚀 Usage

### Process Multiple PDFs

Place your PDF files in the `test/` directory and run:

```bash
python main.py
```

This will:
1. ✅ Extract text from all PDFs in the `test/` directory using OCR **with metadata headers**
2. 📁 Save extracted text to `test-parsed/` folder (preserving original filenames)
3. 🤖 Extract contact information data using Azure OpenAI **with preserved metadata**
4. 💾 Save results as enhanced JSON files with comprehensive metadata

### Process Single PDF

```python
from main import process_single_pdf
process_single_pdf("path/to/your/document.pdf")
```

### Manual Steps

You can also run the components separately:

```python
# Step 1: Extract text from PDFs using OCR with metadata
from tools.pdf_text_parser import parse_multiple_pdfs
results = parse_multiple_pdfs("test", "test-parsed")

# Step 2: Extract contact information data with metadata preservation
from tools.pdf_field_extractor import OpenAIDataExtractor
extractor = OpenAIDataExtractor()
extraction_results = extractor.process_all_parsed_texts("test-parsed", "test-extract")
```

## 📋 Extracted Data Fields

The system extracts the following contact information and delivery fields:

- **RECEIVING_VESSEL_NAME**: Name of the vessel receiving the delivery
- **DELIVERING_VESSEL_NAME**: Name of the vessel or vehicle delivering  
- **IMO_NUMBER**: International Maritime Organization number
- **PORT**: Port where the delivery took place
- **DELIVERY_DATE**: Date of delivery
- **SUPPLIER_NAME**: Name of the supplier company
- **SUPPLIER_ADDRESS**: Full address of the supplier
- **SUPPLIER_PHONE**: Phone number of the supplier
- **DELIVERY_METHOD**: Method of delivery (barge, truck, pipeline)
- **DELIVERY_LOCATION**: Specific location (berth, anchorage, etc.)
- **PRODUCT_NAME**: Type of product delivered
- **QUANTITY_METRIC_TONS**: Quantity delivered in metric tons
- **DENSITY_15C**: Density at 15°C
- **SULPHUR_CONTENT**: Sulphur content percentage
- **FLASH_POINT**: Flash point temperature
- **TIME_OF_COMMENCEMENT**: Start time of delivery
- **TIME_COMPLETED**: End time of delivery

## 📁 Output Files with Enhanced Metadata

The system generates several types of output files, **all with comprehensive metadata preservation**:

### Text Extraction Output (`test-parsed/`)
- `{original_pdf_name}.txt`: **Enhanced format** with metadata header + extracted text
- `{original_pdf_name}_info.txt`: Detailed metadata about extraction process

### Contact Information Data Output (`test-extract/`)
- `{original_pdf_name}_contact_information_data.json`: **Enhanced JSON** with metadata + structured data
- `contact_information_extraction_results.json`: **Enhanced consolidated results** with processing summary

### 🆕 Enhanced File Format Examples:

#### Enhanced Text File Format (`test-parsed/document.txt`):
```
=== DOCUMENT METADATA ===
Original Filename: important_document.pdf
Original File Path: /path/to/important_document.pdf
File Size: 123456 bytes
File Modified: 2024-01-15T10:30:00.123456
Processing Timestamp: 2024-01-15T11:00:00.123456
Extraction Method: OCR (Tesseract)
OCR Configuration: Enhanced for poor quality scanned documents
Text Length: 2500 characters
Parser Version: PDFTextParser v1.0
=== END METADATA ===

=== EXTRACTED TEXT CONTENT ===
[actual OCR extracted text content...]
=== END DOCUMENT ===
```

#### Enhanced JSON File Format (`test-extract/document_contact_information_data.json`):
```json
{
  "document_metadata": {
    "original_filename": "important_document.pdf",
    "original_file_path": "/path/to/important_document.pdf",
    "file_size": "123456 bytes",
    "file_modified": "2024-01-15T10:30:00.123456",
    "extraction_timestamp": "2024-01-15T11:00:00.123456",
    "extraction_method": "OCR",
    "parser_version": "PDFTextParser v1.0",
    "text_length": "2500 characters",
    "processed_by": "OpenAIDataExtractor",
    "extraction_processing_timestamp": "2024-01-15T11:05:00.123456",
    "source_text_file": "/path/to/test-parsed/document.txt",
    "filename_base": "document"
  },
  "extracted_fields": {
    "RECEIVING_VESSEL_NAME": "MV Example Ship",
    "SUPPLIER_NAME": "Example Supplier Co.",
    "DELIVERY_DATE": "2024-01-15",
    // ... other extracted fields
  }
}
```

### Example File Structure:
```
ws-doc-processing/
├── test/
│   ├── important_document.pdf
│   └── another_file.pdf
├── test-parsed/                         # Enhanced text files with metadata
│   ├── important_document.txt           # Metadata header + extracted text
│   ├── important_document_info.txt      # Processing details
│   ├── another_file.txt
│   └── another_file_info.txt
├── test-extract/                        # Enhanced JSON files with metadata
│   ├── important_document_contact_information_data.json  # Metadata + extracted data
│   ├── another_file_contact_information_data.json
│   └── contact_information_extraction_results.json      # Enhanced consolidated results
└── poppler/                             # Poppler binaries
    └── poppler-24.08.0/
        └── Library/
            └── bin/
```

## 📦 Dependencies

- **📄 OCR Processing**: pytesseract, pdf2image, Pillow, Tesseract OCR
- **🔧 PDF Processing**: Poppler Utils (for pdf2image)
- **🤖 Azure Integration**: openai (Azure OpenAI client)
- **🛠️ Utilities**: python-dotenv
- **☁️ Azure Storage** (optional): azure-storage-blob, azure-core

## 🐛 Troubleshooting

### Common Issues

1. **Poppler not found**: 
   - Download Poppler from the link above
   - Extract to `poppler/` directory in project root
   - Ensure `poppler/poppler-version/Library/bin/pdftoppm.exe` exists

2. **Tesseract OCR not found**: 
   - Install Tesseract OCR following the instructions above
   - Ensure it's added to your system PATH
   - Restart your terminal after installation

3. **Azure OpenAI connection failed**: 
   - Check your `OPENAI_ENDPOINT` and `OPENAI_KEY` in `.env`
   - Verify your Azure OpenAI deployment name

4. **No text extracted**: 
   - Ensure PDFs contain readable text (not just images without text)
   - Check if Poppler and Tesseract are properly installed
   - Try adjusting OCR settings for very poor quality documents

5. **Metadata not showing**: 
   - Ensure you're using the updated version of the code
   - Check that text files in `test-parsed/` contain metadata headers
   - Verify JSON files in `test-extract/` have `document_metadata` section

### Test Components

#### Test Poppler Installation:
```bash
# Check if Poppler binaries exist
dir poppler\poppler-*\Library\bin\pdftoppm.exe
```

#### Test Tesseract OCR Installation:
```bash
tesseract --version
```

#### Test Azure OpenAI Connection:
```python
from tools.pdf_field_extractor import test_azure_openai_connection
test_azure_openai_connection()
```

## 🔧 OCR Optimization for Poor Quality Documents

The system includes several optimizations for poor quality scanned documents:

- **📈 High DPI conversion** (300 DPI) for better image quality
- **⚙️ Enhanced OCR configuration** with character whitelisting
- **📄 Multi-page processing** with progress tracking
- **🛡️ Error handling** for corrupted or unreadable pages
- **🎯 Custom Tesseract settings** optimized for document formats
- **📊 Comprehensive metadata tracking** for quality assessment

## 🆕 Enhanced Metadata Features

### What's New:
- **📄 Source File Tracking**: Every output file knows its original PDF source
- **⏰ Timestamp Tracking**: Complete processing timeline from start to finish
- **📏 Size and Length Tracking**: File sizes and text lengths for quality assessment
- **🔧 Method Tracking**: Which extraction methods were used
- **📝 Version Tracking**: Parser and extractor version information
- **🔗 File Linking**: Clear links between original PDFs, parsed text, and extracted data

### Benefits:
- **🔍 Full Traceability**: Know exactly where any piece of data came from
- **📊 Quality Assessment**: Evaluate extraction quality with size and length metrics
- **🕒 Audit Trail**: Complete processing history for compliance
- **🔄 Reproducibility**: Recreate processing with version and method information
- **🗂️ Data Management**: Easy organization and reference of processed documents

## 📂 File Structure

```
ws-doc-processing/
├── main.py                              # Main processing pipeline with metadata
├── requirements.txt                     # Python dependencies
├── .env                                 # Configuration (create this)
├── test/                               # Input PDF files
├── test-parsed/                        # Enhanced parsed text with metadata headers
├── test-extract/                       # Enhanced JSON files with metadata + extracted data
├── poppler/                            # Poppler binaries (download and extract here)
│   └── poppler-24.08.0/
│       └── Library/
│           └── bin/
├── tools/
│   ├── pdf_text_parser.py             # Enhanced OCR text extraction with metadata
│   ├── pdf_field_extractor.py         # Enhanced Azure OpenAI extraction with metadata
│   └── blob_handler.py                # Azure Blob Storage (optional)
└── README.md                          # This file
```

## 📄 License

This project is for document processing applications with enhanced metadata tracking and traceability features. 