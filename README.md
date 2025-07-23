# Marine Fuel Document Processing System

A comprehensive system for processing marine fuel delivery PDF documents using OCR and Azure OpenAI for structured data extraction.

## Features

- **OCR Text Extraction**: Uses Tesseract OCR optimized for poor quality scanned documents
- **Azure OpenAI Integration**: Leverages Azure OpenAI for intelligent entity extraction
- **Marine Fuel Specialization**: Specifically designed to extract marine fuel delivery data fields
- **Batch Processing**: Process multiple PDF documents at once
- **Structured Output**: Generates clean JSON output with standardized fields
- **Filename Preservation**: Maintains original PDF filenames in all output files

## System Architecture

The system works in two main steps:

1. **PDF OCR Extraction**: Extract text from scanned PDFs using Tesseract OCR and save to `test-parsed/` folder
2. **Data Extraction**: Use Azure OpenAI to extract structured marine fuel delivery data

## Installation

### Prerequisites

1. **Tesseract OCR** (Required for scanned document processing)

#### Installing Tesseract OCR on Windows:

1. **Download Tesseract installer:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-v5.3.3.20231005.exe`)

2. **Install Tesseract:**
   - Run the installer as Administrator (or under your user)
   - During installation, note the installation path (usually `C:\Program Files\Tesseract-OCR\`)
   - Make sure to check "Add to PATH" during installation

3. **Verify installation:**
   ```bash
   tesseract --version
   ```

4. **If PATH not set automatically:**
   - Add `C:\Program Files\Tesseract-OCR\` to your Windows PATH environment variable
   - Restart your command prompt/PowerShell

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

## Configuration

Create a `.env` file in the project root with your Azure configuration:

```env
# Azure Blob Storage Configuration (optional)
SAS_TOKEN=your_sas_token_here
CONTAINER_NAME=your_container_name_here

# Azure OpenAI Configuration (required)
OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
OPENAI_KEY=your_azure_openai_api_key_here
```

## Usage

### Process Multiple PDFs

Place your PDF files in the `test/` directory and run:

```bash
python main.py
```

This will:
1. Extract text from all PDFs in the `test/` directory using OCR
2. Save extracted text to `test-parsed/` folder (preserving original filenames)
3. Extract marine fuel delivery data using Azure OpenAI
4. Save results as JSON files

### Process Single PDF

```python
from main import process_single_pdf
process_single_pdf("path/to/your/document.pdf")
```

### Manual Steps

You can also run the components separately:

```python
# Step 1: Extract text from PDFs using OCR
from tools.pdf_text_parser import parse_multiple_pdfs
results = parse_multiple_pdfs("test", "test-parsed")

# Step 2: Extract marine fuel data
from tools.marine_fuel_extractor import MarineFuelDataExtractor
extractor = MarineFuelDataExtractor()
extraction_results = extractor.process_all_parsed_texts("test-parsed")
```

## Extracted Data Fields

The system extracts the following marine fuel delivery fields:

- **RECEIVING_VESSEL_NAME**: Name of the vessel receiving the fuel
- **DELIVERING_VESSEL_NAME**: Name of the vessel or barge delivering the fuel  
- **IMO_NUMBER**: International Maritime Organization number
- **PORT**: Port where the delivery took place
- **DELIVERY_DATE**: Date of fuel delivery
- **SUPPLIER_NAME**: Name of the fuel supplier company
- **SUPPLIER_ADDRESS**: Full address of the supplier
- **SUPPLIER_PHONE**: Phone number of the supplier
- **DELIVERY_METHOD**: Method of delivery (barge, truck, pipeline)
- **DELIVERY_LOCATION**: Specific location (berth, anchorage, etc.)
- **PRODUCT_NAME**: Type of fuel product (HFO, LSFO, VLSFO, MDO, MGO, etc.)
- **QUANTITY_METRIC_TONS**: Quantity delivered in metric tons
- **DENSITY_15C**: Density at 15°C
- **SULPHUR_CONTENT**: Sulphur content percentage
- **FLASH_POINT**: Flash point temperature
- **TIME_OF_COMMENCEMENT**: Start time of delivery
- **TIME_COMPLETED**: End time of delivery

## Output Files

The system generates several types of output files, **all preserving original PDF filenames**:

### Text Extraction Output (`test-parsed/`)
- `{original_pdf_name}.txt`: Extracted text from PDF using OCR
- `{original_pdf_name}_info.txt`: Metadata about extraction process

### Marine Fuel Data Output (`test-parsed/`)
- `{original_pdf_name}_marine_fuel_data.json`: Structured marine fuel data
- `marine_fuel_extraction_results.json`: Consolidated results for all files

### Example File Structure:
```
test-parsed/
├── 1. BUNKER LSMGO 13-01-2023.txt
├── 1. BUNKER LSMGO 13-01-2023_info.txt  
├── 1. BUNKER LSMGO 13-01-2023_marine_fuel_data.json
├── 1.B%20SMGO%20BDN%2027.01.2024%20-%20ONSAN.txt
├── 1.B%20SMGO%20BDN%2027.01.2024%20-%20ONSAN_info.txt
├── 1.B%20SMGO%20BDN%2027.01.2024%20-%20ONSAN_marine_fuel_data.json
└── marine_fuel_extraction_results.json
```

## Dependencies

- **OCR Processing**: pytesseract, pdf2image, Pillow, Tesseract OCR
- **Azure Integration**: openai (Azure OpenAI client)
- **Utilities**: python-dotenv
- **Azure Storage** (optional): azure-storage-blob, azure-core

## Troubleshooting

### Common Issues

1. **Tesseract OCR not found**: 
   - Install Tesseract OCR following the instructions above
   - Ensure it's added to your system PATH
   - Restart your terminal after installation

2. **Azure OpenAI connection failed**: 
   - Check your `OPENAI_ENDPOINT` and `OPENAI_KEY` in `.env`
   - Verify your Azure OpenAI deployment name

3. **No text extracted**: 
   - Ensure PDFs contain readable text (not just images without text)
   - Try adjusting OCR settings for very poor quality documents

4. **Poor OCR quality**:
   - The system is optimized for poor quality scans with custom OCR configuration
   - For extremely poor quality, consider pre-processing images with image enhancement tools

### Test Components

#### Test Tesseract OCR Installation:
```bash
tesseract --version
```

#### Test Azure OpenAI Connection:
```bash
python test-openai.py
```

#### Test PDF Text Extraction:
```bash
python tools/pdf_text_parser.py
```

#### Test Marine Fuel Data Extraction:
```bash
python tools/marine_fuel_extractor.py
```

## OCR Optimization for Poor Quality Documents

The system includes several optimizations for poor quality scanned documents:

- **High DPI conversion** (300 DPI) for better image quality
- **Enhanced OCR configuration** with character whitelisting
- **Multi-page processing** with progress tracking
- **Error handling** for corrupted or unreadable pages
- **Custom Tesseract settings** optimized for marine document formats

## File Structure

```
ws-doc-processing/
├── main.py                              # Main processing pipeline
├── requirements.txt                     # Python dependencies
├── .env                                 # Configuration (create this)
├── test/                               # Input PDF files
├── test-parsed/                        # Parsed text and extracted data
├── tools/
│   ├── pdf_text_parser.py             # OCR text extraction
│   ├── marine_fuel_extractor.py       # Azure OpenAI data extraction
│   └── blob_handler.py                # Azure Blob Storage (optional)
└── README.md                          # This file
```

## License

This project is for internal use and marine fuel document processing applications. 