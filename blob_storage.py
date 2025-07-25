from tools.blob_handler import AzureBlobHandler
import os 
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
today = datetime.now().strftime("%Y%m%d")
ACCOUNT_URL = "https://stdatapprdev002.blob.core.windows.net/"
SAS_TOKEN = os.getenv("SAS_TOKEN") or ""
CONTAINER_NAME = os.getenv("CONTAINER_NAME") or ""
blob_handler = AzureBlobHandler(ACCOUNT_URL, SAS_TOKEN, CONTAINER_NAME)
print("✓ Successfully connected to Azure Blob Storage")


def list_blobs_example() -> None:
    try:
        print("\nListing all blobs:")
        blobs = blob_handler.list_blobs()
        if blobs:
            for blob in blobs:
                print(f"   - {blob}")
        else:
            print("   No blobs found in container")
    except Exception as e:
        print(f"✗ Error: {e}")


def upload_directory_example(upload_dir: str) -> None:
    try:
        print("\nUploading directory:")
        local_dir = upload_dir
        if os.path.exists(local_dir):
            uploaded_count = blob_handler.upload_directory(local_dir, f"outputs/{today}/")
            print(f"   ✓ Uploaded {uploaded_count} files")
        else:
            print(f"   Directory not found: {local_dir}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def download_blob_example(download_dir: str) -> None:
    try:
        
        print("\nDownloading all blobs:")
        os.makedirs(download_dir, exist_ok=True)
        print(f"   Download directory: {download_dir}")
        
        blobs = blob_handler.list_blobs()
        if not blobs:
            print("   No blobs found in container")
            return
        
        print(f"   Found {len(blobs)} blobs to download:")
        for blob in blobs:
            print(f"     - {blob}")
        
        print(f"\n   Starting download of {len(blobs)} blobs...")
        downloaded_count = 0
        failed_count = 0
        
        for blob_name in blobs:
            # Create local file path maintaining directory structure
            local_file_path = os.path.join(download_dir, blob_name)
            
            # Ensure the directory structure exists
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            # Download the blob
            if blob_handler.download_file(blob_name, local_file_path):
                print(f"     ✓ Downloaded: {blob_name}")
                downloaded_count += 1
            else:
                print(f"     ✗ Failed to download: {blob_name}")
                failed_count += 1
        
        print(f"\n   Download completed!")
        print(f"   ✓ Successfully downloaded: {downloaded_count} files")
        if failed_count > 0:
            print(f"   ✗ Failed to download: {failed_count} files")
        print(f"   Files saved to: {os.path.abspath(download_dir)}")
                    
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    # list_blobs_example()
    upload_directory_example(upload_dir = "files/")
    # download_blob_example(download_dir = "files/")