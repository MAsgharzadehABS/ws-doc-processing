# Azure Blob Storage Handler

A comprehensive Python class for handling Azure Blob Storage operations including listing, uploading, and downloading files using SAS (Shared Access Signature) token authentication.

## 🚀 Features

- **List Blobs** - List all blobs or filter by prefix
- **Upload Files** - Upload single files or entire directories
- **Download Files** - Download individual blobs or entire directory structures
- **Delete Blobs** - Remove blobs from storage
- **Blob Operations** - Check existence and get properties
- **SAS Token Authentication** - Secure authentication using SAS keys
- **Error Handling** - Comprehensive error handling and logging
- **Directory Support** - Maintains folder structure for bulk operations

## 📋 Requirements

- Python 3.7+
- Azure Storage Account with SAS token
- Azure Blob Container

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file in the project root:**
   ```env
   SAS_TOKEN=your_sas_token_here
   CONTAINER_NAME=your_container_name
   ```

## 📁 Project Structure

```
wavesight-doc-processing/
├── tools/
│   └── blob_handler.py      # Main AzureBlobHandler class
├── example_usage.py         # Usage examples
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables (create this)
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Your SAS token from Azure Storage Account
SAS_TOKEN=

# Your blob container name
CONTAINER_NAME=
```

### Getting Your SAS Token

1. Go to your Azure Storage Account
2. Navigate to "Shared access signature" in the left menu
3. Configure permissions (Read, Add, Create, Write, Delete, List)
4. Set expiry date
5. Generate SAS token
6. Copy the token (without the leading `?`)

## 📚 Usage

### Basic Usage

```python
from tools.blob_handler import AzureBlobHandler

# Initialize
handler = AzureBlobHandler(
    account_url="https://yourstorageaccount.blob.core.windows.net/",
    sas_token="your_sas_token",
    container_name="your_container"
)

# List all blobs
blobs = handler.list_blobs()

# Upload a file
handler.upload_file("local_file.txt", "remote_file.txt")

# Download a file
handler.download_file("remote_file.txt", "downloaded_file.txt")

# Upload entire directory
handler.upload_directory("local_folder/", "remote_folder/")
```

### Available Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `list_blobs(prefix=None)` | List all blobs or filter by prefix | `prefix`: Optional filter |
| `upload_file(local_path, blob_name, overwrite=True)` | Upload single file | `local_path`, `blob_name`, `overwrite` |
| `download_file(blob_name, local_path=None)` | Download single file | `blob_name`, `local_path` |
| `upload_directory(local_dir, blob_prefix="", overwrite=True)` | Upload entire directory | `local_dir`, `blob_prefix`, `overwrite` |
| `download_directory(blob_prefix, local_dir)` | Download directory by prefix | `blob_prefix`, `local_dir` |
| `delete_blob(blob_name)` | Delete a blob | `blob_name` |
| `blob_exists(blob_name)` | Check if blob exists | `blob_name` |
| `get_blob_properties(blob_name)` | Get blob metadata | `blob_name` |

## 🧪 Running Examples

The `example_usage.py` file contains three separate example functions:

### 1. List Blobs Example
```python
def list_blobs_example():
    # Lists all blobs in your container
```

### 2. Upload Directory Example
```python
def upload_directory_example():
    # Uploads all files from 'raw_inputs/' directory
```

### 3. Download Blob Example
```python
def download_blob_example():
    # Downloads a specific blob file
```

### Running Examples

```bash
# Run the active example (currently upload_directory_example)
python example_usage.py
```

To run different examples, edit the `if __name__ == "__main__":` section in `example_usage.py`:

```python
if __name__ == "__main__":
    list_blobs_example()        # Uncomment to run
    # upload_directory_example()  # Currently active
    # download_blob_example()     # Uncomment to run
```

## 📂 Directory Structure Examples

### Upload Directory Structure
When uploading `raw_inputs/` directory:
```
raw_inputs/
├── file1.txt
├── subfolder/
│   ├── file2.pdf
│   └── file3.docx
└── another_file.xlsx
```

Results in Azure Blob Storage:
```
test_upload/file1.txt
test_upload/subfolder/file2.pdf
test_upload/subfolder/file3.docx
test_upload/another_file.xlsx
```

## 🔍 Error Handling

The handler includes comprehensive error handling:

- **File not found errors** - Clear messages when local files don't exist
- **Azure service errors** - Proper handling of Azure API errors
- **Authentication errors** - Clear feedback on SAS token issues
- **Network errors** - Timeout and connection error handling
- **Logging** - Detailed logs for debugging

## 🛡️ Security Best Practices

1. **Never commit SAS tokens** - Always use `.env` files
2. **Set appropriate permissions** - Only grant necessary permissions in SAS token
3. **Set expiry dates** - SAS tokens should have reasonable expiry times
4. **Use HTTPS only** - Always use secure connections

## 🐛 Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Check your SAS token is correct and not expired
   - Ensure SAS token has required permissions

2. **"Container not found"**
   - Verify container name in `.env` file
   - Check container exists in your storage account

3. **"File not found" during upload**
   - Verify local file/directory path exists
   - Check file permissions

4. **Import errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're in the correct Python environment

### Enable Debug Logging

To see detailed logs, modify the logging level in `blob_handler.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Dependencies

- `azure-storage-blob` - Azure Blob Storage SDK
- `azure-core` - Azure SDK core functionality  
- `python-dotenv` - Environment variable management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review Azure Blob Storage documentation
3. Check Azure SDK for Python documentation 