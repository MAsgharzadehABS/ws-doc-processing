import os
import json
import logging
from typing import Dict, List, Optional
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenAIDataExtractor:
    """
    Extracts structured marine fuel delivery data from OCRed PDF text
    using Azure OpenAI with specialized prompts.
    """
    
    def __init__(self):
        """Initialize the Marine Fuel Data Extractor with Azure OpenAI client."""
        self.azure_endpoint = os.getenv("OPENAI_ENDPOINT") or ""
        self.api_key = os.getenv("OPENAI_KEY") or ""
        self.api_version = "2024-02-01"
        self.model_name = "gpt-4.1-mini"  # Adjust based on your deployment
        
        if not self.azure_endpoint or not self.api_key:
            raise ValueError("Azure OpenAI configuration missing. Please set OPENAI_ENDPOINT and OPENAI_KEY in your .env file.")
        
        try:
            self.client = AzureOpenAI(
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )
            logger.info("Successfully initialized Azure OpenAI client")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise
    
    def get_extraction_prompt(self, document_text: str) -> str:
        """
        Generate the specialized prompt for marine fuel delivery data extraction.
        """
        prompt = f"""You are an AI agent specialized in extracting structured data from OCRed PDF documents related to marine fuel deliveries. Your task is to carefully analyze the provided document text and extract the following specific fields.
 
            ## Required Fields to Extract:
 
            Extract the following information and return it in JSON format. If any field cannot be found or determined from the document, return "NA" for that field:
 
            - **RECEIVING_VESSEL_NAME**: Name of the vessel receiving the fuel (e.g., "Kan Wo", "MV Ocean Explorer")
            - **DELIVERING_VESSEL_NAME**: Name of the vessel or barge delivering the fuel (e.g., "Teluge", "MV Fuel Carrier")  
            - **IMO_NUMBER**: International Maritime Organization number of the receiving vessel (e.g., "9811074")
            - **PORT**: Port where the delivery took place (e.g., "SINGAPORE", "Vancouver")
            - **DELIVERY_DATE**: Date of fuel delivery (format as found in document, e.g., "1/5/2024")
            - **SUPPLIER_NAME**: Name of the fuel supplier company (e.g., "Hyundai Oilbank Co. Ltd")
            - **SUPPLIER_ADDRESS**: Full address of the supplier (e.g., "Building 123 Industrial District Seoul Korea")
            - **SUPPLIER_PHONE**: Phone number of the supplier (e.g., "402-500-4500")
            - **DELIVERY_METHOD**: Method of delivery (e.g., "lighter", "Barge", "Tanker")
            - **DELIVERY_LOCATION**: Specific location where delivery occurred (e.g., "SINGAPORE ANCHORAGE", "Vancouver Harbor")
            - **PRODUCT_NAME**: Type of fuel product delivered (e.g., "VLSFO", "LSMGO")
            - **QUANTITY_METRIC_TONS**: Quantity delivered in metric tons (e.g., "86", "150")
            - **DENSITY_15C**: Density at 15°C (include units if specified, e.g., "985.2")
            - **SULPHUR_CONTENT**: Sulphur content percentage or specification (e.g., "0.35")
            - **FLASH_POINT**: Flash point temperature (include units, e.g., "65°C")
            - **TIME_OF_COMMENCEMENT**: Start time of delivery operation (e.g., "08:00" or "08:00:00")
            - **TIME_COMPLETED**: End time of delivery operation (e.g., "10:00" or "10:00:00")
 
            ## Product Reference Guide:
            The PRODUCT_NAME should match one of these common marine fuels if identified:
            - HFO (Heavy Fuel Oil)
            - LSFO (Low Sulphur Fuel Oil)
            - VLSFO (Very Low Sulphur Fuel Oil)
            - MDO (Marine Diesel Oil)
            - MGO (Marine Gas Oil)
            - BIO (Biofuel)
            - FAME (Fatty Acid Methyl Ester)
            - LNG (Liquefied Natural Gas)
            - LPG (Liquefied Petroleum Gas)
            - Methanol
 
            ## Instructions:
            1. Carefully read through the entire OCRed document text
            2. Look for variations in terminology (e.g., "vessel name" vs "ship name", "mt" vs "metric tons")
            3. Pay attention to tables, headers, and structured sections
            4. Cross-reference information if the same data appears in multiple locations
            5. For dates and times, preserve the original format found in the document
            6. Return "NA" for any field that cannot be definitively determined
            7. Format your response as clean, valid JSON      
 
            ## Output Format:
            Return your findings in the following JSON structure:
 
            ```json
            {{
            "RECEIVING_VESSEL_NAME": "",
            "DELIVERING_VESSEL_NAME": "",
            "IMO_NUMBER": "",
            "PORT": "",
            "DELIVERY_DATE": "",
            "SUPPLIER_NAME": "",
            "SUPPLIER_ADDRESS": "",
            "SUPPLIER_PHONE": "",
            "DELIVERY_METHOD": "",
            "DELIVERY_LOCATION": "",
            "PRODUCT_NAME": "",
            "QUANTITY_METRIC_TONS": "",
            "DENSITY_15C": "",
            "SULPHUR_CONTENT": "",
            "FLASH_POINT": "",
            "TIME_OF_COMMENCEMENT": "",
            "TIME_COMPLETED": ""
            }}
            ```
 
            ## Document Text to Analyze:
 
            {document_text}
 
            Now please analyze the provided OCRed document text and extract the requested information."""
       
        return prompt
    
    def extract_marine_fuel_data(self, document_text: str) -> Dict:
        """
        Extract marine fuel delivery data from document text using Azure OpenAI.
        
        Args:
            document_text (str): The OCRed text from the PDF document
            
        Returns:
            Dict: Extracted marine fuel delivery data
        """
        try:
            prompt = self.get_extraction_prompt(document_text)
            
            # Truncate text if too long (Azure OpenAI has token limits)
            max_chars = 12000  # Conservative limit to avoid token issues
            if len(document_text) > max_chars:
                document_text = document_text[:max_chars] + "\n[...TRUNCATED...]"
                logger.warning(f"Document text truncated to {max_chars} characters due to length")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at extracting structured marine fuel delivery data from documents. Always return valid JSON with the exact field names specified."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.0,  # Low temperature for consistent results
                max_tokens=1000,   # Enough for the JSON response
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content or "{}"
            
            # Try to parse the JSON response
            try:
                # Extract JSON from the response (in case there's extra text)
                extracted_data = json.loads(result_text)
                
                logger.info("Successfully extracted marine fuel data using Azure OpenAI")
                return extracted_data
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {result_text}")
                return {
                    "error": "JSON parsing failed",
                    "raw_response": result_text
                }
                
        except Exception as e:
            logger.error(f"Failed to extract marine fuel data: {e}")
            return {
                "error": str(e)
            }
    
    def process_parsed_text_file(self, text_file_path: str, output_dir: str = "test-extract") -> Dict:
        """
        Process a single parsed text file and extract marine fuel data.
        Includes comprehensive metadata in the extracted data.
        
        Args:
            text_file_path (str): Path to the text file containing parsed PDF content
            output_dir (str): Directory to save the extraction results
            
        Returns:
            Dict: Processing results including extracted data with metadata
        """
        if not os.path.exists(text_file_path):
            logger.error(f"Text file not found: {text_file_path}")
            return {"error": "Text file not found"}
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Read the parsed text
            with open(text_file_path, 'r', encoding='utf-8') as f:
                full_content = f.read()
            
            logger.info(f"Processing text file: {text_file_path}")
            
            # Extract metadata from the text file if it exists
            metadata = {}
            document_text = full_content
            
            # Check if the file contains metadata header
            if "=== DOCUMENT METADATA ===" in full_content:
                try:
                    # Split content to extract metadata and document text
                    parts = full_content.split("=== EXTRACTED TEXT CONTENT ===")
                    if len(parts) >= 2:
                        metadata_section = parts[0]
                        document_text = parts[1].replace("=== END DOCUMENT ===", "").strip()
                        
                        # Parse metadata from the header
                        metadata_lines = metadata_section.split('\n')
                        for line in metadata_lines:
                            if ':' in line and not line.startswith('==='):
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip()
                                
                        logger.info(f"Extracted metadata from text file: {len(metadata)} fields")
                    else:
                        document_text = full_content
                except Exception as e:
                    logger.warning(f"Failed to parse metadata from text file: {e}")
                    document_text = full_content
            
            logger.info(f"Document length: {len(document_text)} characters")
            
            # Extract marine fuel data
            extracted_data = self.extract_marine_fuel_data(document_text)
            
            # Add metadata to the extracted data
            import datetime
            processing_timestamp = datetime.datetime.now().isoformat()
            
            # Create comprehensive result with metadata
            filename_base = os.path.splitext(os.path.basename(text_file_path))[0]
            
            # Enhanced extracted data structure with metadata
            enhanced_extracted_data = {
                "document_metadata": {
                    "original_filename": metadata.get("Original Filename", ""),
                    "original_file_path": metadata.get("Original File Path", ""),
                    "file_size": metadata.get("File Size", ""),
                    "file_modified": metadata.get("File Modified", ""),
                    "extraction_timestamp": metadata.get("Processing Timestamp", ""),
                    "extraction_method": metadata.get("Extraction Method", "OCR"),
                    "parser_version": metadata.get("Parser Version", ""),
                    "text_length": metadata.get("Text Length", ""),
                    "processed_by": "OpenAIDataExtractor",
                    "extraction_processing_timestamp": processing_timestamp,
                    "source_text_file": text_file_path,
                    "filename_base": filename_base
                },
                "extracted_fields": extracted_data
            }
            
            # Prepare result
            result = {
                "text_file": text_file_path,
                "filename_base": filename_base,
                "document_length": len(document_text),
                "extracted_data": enhanced_extracted_data,
                "success": "error" not in extracted_data
            }
            
            # Save enhanced extracted data as JSON
            output_file = os.path.join(output_dir, f"{filename_base}_contact_information_data.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_extracted_data, f, indent=2, ensure_ascii=False)
            
            result["output_file"] = output_file
            
            logger.info(f"Enhanced data with metadata saved to: {output_file}")
            logger.info(f"Original filename preserved: {metadata.get('Original Filename', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process text file {text_file_path}: {e}")
            return {
                "text_file": text_file_path,
                "error": str(e),
                "success": False
            }
    
    def process_all_parsed_texts(self, parsed_dir: str = "test-parsed", output_dir: str = "test-extract") -> List[Dict]:
        """
        Process all parsed text files in the directory and extract marine fuel data.
        
        Args:
            parsed_dir (str): Directory containing parsed text files
            output_dir (str): Directory to save the extracted JSON files
            
        Returns:
            List[Dict]: Results for each processed file
        """
        if not os.path.exists(parsed_dir):
            logger.error(f"Parsed directory not found: {parsed_dir}")
            return []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all text files (excluding info files)
        text_files = [
            f for f in os.listdir(parsed_dir) 
            if f.endswith('.txt') and not f.endswith('_info.txt')
        ]
        
        if not text_files:
            logger.warning(f"No text files found in {parsed_dir}")
            return []
        
        logger.info(f"Found {len(text_files)} text files to process")
        
        results = []
        for text_file in text_files:
            text_file_path = os.path.join(parsed_dir, text_file)
            try:
                result = self.process_parsed_text_file(text_file_path, output_dir)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {text_file}: {e}")
                results.append({
                    "text_file": text_file_path,
                    "error": str(e),
                    "success": False
                })
        
        return results


def test_azure_openai_connection():
    """Test the Azure OpenAI connection."""
    try:
        extractor = OpenAIDataExtractor()
        logger.info("✓ Azure OpenAI connection test successful")
        return True
    except Exception as e:
        logger.error(f"✗ Azure OpenAI connection test failed: {e}")
        return False
