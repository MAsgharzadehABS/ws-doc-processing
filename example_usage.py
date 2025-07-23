from tools.blob_handler import AzureBlobHandler
import os 
from dotenv import load_dotenv
load_dotenv()


def list_blobs_example():
    # Configuration - using environment variables
    ACCOUNT_URL = "https://stdatapprdev002.blob.core.windows.net/"
    SAS_TOKEN = os.getenv("SAS_TOKEN")
    CONTAINER_NAME = os.getenv("CONTAINER_NAME")
    
    try:
        # Initialize the blob handler
        print("Initializing Azure Blob Handler...")
        blob_handler = AzureBlobHandler(ACCOUNT_URL, SAS_TOKEN, CONTAINER_NAME)
        print("✓ Successfully connected to Azure Blob Storage")
        
        # Test 1: List all blobs in the container
        print("\n1. Listing all blobs:")
        blobs = blob_handler.list_blobs()
        if blobs:
            for blob in blobs:
                print(f"   - {blob}")
        else:
            print("   No blobs found in container")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def upload_directory_example():
    # Configuration - using environment variables
    ACCOUNT_URL = "https://stdatapprdev002.blob.core.windows.net/"
    SAS_TOKEN = os.getenv("SAS_TOKEN")
    CONTAINER_NAME = os.getenv("CONTAINER_NAME")
    
    try:
        # Initialize the blob handler
        print("Initializing Azure Blob Handler...")
        blob_handler = AzureBlobHandler(ACCOUNT_URL, SAS_TOKEN, CONTAINER_NAME)
        print("✓ Successfully connected to Azure Blob Storage")
        
        # Test 2: Upload entire directory
        print("\n2. Uploading directory:")
        local_dir = "raw_inputs/"  # Replace with your actual directory path
        if os.path.exists(local_dir):
            uploaded_count = blob_handler.upload_directory(local_dir, "test_upload/")
            print(f"   ✓ Uploaded {uploaded_count} files")
        else:
            print(f"   Directory not found: {local_dir}")
            print("   Please update the 'local_dir' variable with a valid directory path")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def download_blob_example():
    # Configuration - using environment variables
    ACCOUNT_URL = "https://stdatapprdev002.blob.core.windows.net/"
    SAS_TOKEN = os.getenv("SAS_TOKEN")
    CONTAINER_NAME = os.getenv("CONTAINER_NAME")
    
    try:
        # Initialize the blob handler
        print("Initializing Azure Blob Handler...")
        blob_handler = AzureBlobHandler(ACCOUNT_URL, SAS_TOKEN, CONTAINER_NAME)
        print("✓ Successfully connected to Azure Blob Storage")
        
        # Test 3: Download a specific blob
        print("\n3. Downloading a blob:")
        blob_to_download = "test_file.txt"  # Replace with an actual blob name from your container
        local_download_path = "downloaded_file.txt"
        
        # Check if blob exists first
        blobs = blob_handler.list_blobs()
        if blob_to_download in blobs:
            download_success = blob_handler.download_file(blob_to_download, local_download_path)
            if download_success:
                print(f"   ✓ Successfully downloaded '{blob_to_download}' to '{local_download_path}'")
            else:
                print(f"   ✗ Failed to download '{blob_to_download}'")
        else:
            print(f"   Blob '{blob_to_download}' does not exist in container")
            if blobs:
                print("   Available blobs to download:")
                for blob in blobs[:5]:  # Show first 5 blobs as examples
                    print(f"     - {blob}")
                    
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    # list_blobs_example()
    upload_directory_example()
    # download_blob_example()