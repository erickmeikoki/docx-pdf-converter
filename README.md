# DOCX to PDF Converter

A simple web application that allows users to upload DOCX files and convert them to PDF format.

## Prerequisites

- Python 3.7 or higher
- LibreOffice (for DOCX to PDF conversion)
- pip (Python package manager)

## Installation

1. Install LibreOffice:

   ```bash
   # On macOS
   brew install --cask libreoffice

   # On Ubuntu/Debian
   sudo apt-get install libreoffice

   # On Windows
   # Download and install LibreOffice from https://www.libreoffice.org/download/download/
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Navigate to the project directory:

   ```bash
   cd docx_to_pdf
   ```

2. Run the Flask application:

   ```bash
   python app.py
   ```

3. Open your web browser and visit:
   ```
   http://localhost:5000
   ```

## Features

- Drag and drop interface for file upload
- Support for DOCX files up to 16MB
- Automatic conversion to PDF
- Clean and modern user interface
- Progress indicator during conversion
- Automatic file cleanup after conversion

## Security Notes

- Files are temporarily stored during conversion and automatically deleted afterward
- Only DOCX files are allowed for upload
- Maximum file size is limited to 16MB

## Troubleshooting

If you encounter any issues:

1. Ensure LibreOffice is properly installed and accessible from the command line
2. Check that all Python dependencies are installed correctly
3. Verify that the uploads directory has proper write permissions
4. Check the application logs for any error messages
