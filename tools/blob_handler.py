import os
import logging
from typing import List, Optional, Union
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import AzureError, ResourceNotFoundError
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureBlobHandler:
    """
    A class to handle Azure Blob Storage operations including listing, uploading, and downloading files.
    Uses SAS (Shared Access Signature) key for authentication.
    """
    
    def __init__(self, account_url: str, sas_token: str, container_name: str):
        """
        Initialize the Azure Blob Handler.
        
        Args:
            account_url (str): The URL of the storage account (e.g., https://mystorageaccount.blob.core.windows.net/)
            sas_token (str): The SAS token for authentication
            container_name (str): The name of the blob container
        """
        self.account_url = account_url
        self.sas_token = sas_token
        self.container_name = container_name
        
        try:
            # Initialize the BlobServiceClient with SAS token
            self.blob_service_client = BlobServiceClient(
                account_url=self.account_url,
                credential=self.sas_token
            )
            
            # Get container client
            self.container_client = self.blob_service_client.get_container_client(
                container=self.container_name
            )
            
            logger.info(f"Successfully initialized Azure Blob Handler for container: {container_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure Blob Handler: {str(e)}")
            raise
    
    def list_blobs(self, prefix: str = None) -> List[str]:
        """
        List all blobs in the container.
        
        Args:
            prefix (str, optional): Filter blobs by prefix
            
        Returns:
            List[str]: List of blob names
        """
        try:
            blob_list = []
            blobs = self.container_client.list_blobs(name_starts_with=prefix)
            
            for blob in blobs:
                blob_list.append(blob.name)
                
            logger.info(f"Found {len(blob_list)} blobs in container")
            return blob_list
            
        except AzureError as e:
            logger.error(f"Failed to list blobs: {str(e)}")
            raise
    
    def upload_file(self, local_file_path: str, blob_name: str = None, overwrite: bool = True) -> bool:
        """
        Upload a file to the blob container.
        
        Args:
            local_file_path (str): Path to the local file to upload
            blob_name (str, optional): Name for the blob. If None, uses the filename
            overwrite (bool): Whether to overwrite if blob already exists
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            # Validate local file exists
            if not os.path.exists(local_file_path):
                logger.error(f"Local file not found: {local_file_path}")
                return False
            
            # Use filename if blob_name not provided
            if blob_name is None:
                blob_name = os.path.basename(local_file_path)
            
            # Get blob client
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            
            # Upload file
            with open(local_file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=overwrite)
            
            logger.info(f"Successfully uploaded {local_file_path} as {blob_name}")
            return True
            
        except FileNotFoundError:
            logger.error(f"File not found: {local_file_path}")
            return False
        except AzureError as e:
            logger.error(f"Failed to upload file: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            return False
    
    def download_file(self, blob_name: str, local_file_path: str = None) -> bool:
        """
        Download a file from the blob container.
        
        Args:
            blob_name (str): Name of the blob to download
            local_file_path (str, optional): Path where to save the file. If None, uses blob name
            
        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            # Use blob name as filename if local_file_path not provided
            if local_file_path is None:
                local_file_path = blob_name
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(local_file_path) if os.path.dirname(local_file_path) else '.', exist_ok=True)
            
            # Get blob client
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            
            # Download blob
            with open(local_file_path, 'wb') as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())
            
            logger.info(f"Successfully downloaded {blob_name} to {local_file_path}")
            return True
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            return False
        except AzureError as e:
            logger.error(f"Failed to download blob: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during download: {str(e)}")
            return False
    
    def upload_directory(self, local_directory: str, blob_prefix: str = "", overwrite: bool = True) -> int:
        """
        Upload all files from a local directory to the blob container.
        
        Args:
            local_directory (str): Path to the local directory
            blob_prefix (str): Prefix to add to blob names
            overwrite (bool): Whether to overwrite if blobs already exist
            
        Returns:
            int: Number of files successfully uploaded
        """
        if not os.path.exists(local_directory):
            logger.error(f"Directory not found: {local_directory}")
            return 0
        
        uploaded_count = 0
        
        for root, dirs, files in os.walk(local_directory):
            for file in files:
                local_file_path = os.path.join(root, file)
                
                # Create relative path for blob name
                relative_path = os.path.relpath(local_file_path, local_directory)
                blob_name = os.path.join(blob_prefix, relative_path).replace('\\', '/')
                
                if self.upload_file(local_file_path, blob_name, overwrite):
                    uploaded_count += 1
        
        logger.info(f"Uploaded {uploaded_count} files from {local_directory}")
        return uploaded_count
    
    def download_directory(self, blob_prefix: str, local_directory: str) -> int:
        """
        Download all blobs with a specific prefix to a local directory.
        
        Args:
            blob_prefix (str): Prefix to filter blobs
            local_directory (str): Local directory to save files
            
        Returns:
            int: Number of files successfully downloaded
        """
        try:
            blobs = self.list_blobs(prefix=blob_prefix)
            downloaded_count = 0
            
            for blob_name in blobs:
                # Create local file path maintaining directory structure
                relative_path = blob_name
                if blob_prefix and blob_name.startswith(blob_prefix):
                    relative_path = blob_name[len(blob_prefix):].lstrip('/')
                
                local_file_path = os.path.join(local_directory, relative_path)
                
                if self.download_file(blob_name, local_file_path):
                    downloaded_count += 1
            
            logger.info(f"Downloaded {downloaded_count} files to {local_directory}")
            return downloaded_count
            
        except Exception as e:
            logger.error(f"Failed to download directory: {str(e)}")
            return 0
    
    def delete_blob(self, blob_name: str) -> bool:
        """
        Delete a blob from the container.
        
        Args:
            blob_name (str): Name of the blob to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            blob_client.delete_blob()
            
            logger.info(f"Successfully deleted blob: {blob_name}")
            return True
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            return False
        except AzureError as e:
            logger.error(f"Failed to delete blob: {str(e)}")
            return False
    
    def blob_exists(self, blob_name: str) -> bool:
        """
        Check if a blob exists in the container.
        
        Args:
            blob_name (str): Name of the blob to check
            
        Returns:
            bool: True if blob exists, False otherwise
        """
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False
        except AzureError as e:
            logger.error(f"Error checking blob existence: {str(e)}")
            return False
    
    def get_blob_properties(self, blob_name: str) -> Optional[dict]:
        """
        Get properties of a blob.
        
        Args:
            blob_name (str): Name of the blob
            
        Returns:
            dict: Blob properties or None if blob doesn't exist
        """
        try:
            blob_client = self.container_client.get_blob_client(blob=blob_name)
            properties = blob_client.get_blob_properties()
            
            return {
                'name': blob_name,
                'size': properties.size,
                'last_modified': properties.last_modified,
                'content_type': properties.content_settings.content_type,
                'etag': properties.etag
            }
            
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {blob_name}")
            return None
        except AzureError as e:
            logger.error(f"Failed to get blob properties: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    # Example configuration - replace with your actual values
    ACCOUNT_URL = "https://yourstorageaccount.blob.core.windows.net/"
    SAS_TOKEN = "your_sas_token_here"
    CONTAINER_NAME = "your_container_name"
    
    # Initialize the blob handler
    try:
        blob_handler = AzureBlobHandler(ACCOUNT_URL, SAS_TOKEN, CONTAINER_NAME)
        
        # Example operations
        print("Listing blobs:")
        blobs = blob_handler.list_blobs()
        for blob in blobs:
            print(f"  - {blob}")
        
        # Upload a file
        # blob_handler.upload_file("local_file.txt", "remote_file.txt")
        
        # Download a file
        # blob_handler.download_file("remote_file.txt", "downloaded_file.txt")
        
    except Exception as e:
        print(f"Error: {e}")
