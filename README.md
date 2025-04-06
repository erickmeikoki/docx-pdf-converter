# DOCX to PDF Converter

A web application that converts DOCX files to PDF format using LibreOffice. Built with Flask, Docker, and deployed on Railway.

## Features

- Convert DOCX files to PDF
- Preview PDF files before downloading
- Multiple file upload support
- Batch conversion mode
- Automatic file cleanup
- File size limit: 16MB per file
- Modern, responsive UI with Tailwind CSS

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Document Conversion**: LibreOffice
- **Containerization**: Docker
- **Deployment**: Railway
- **Version Control**: Git

## Live Demo

The application is hosted on Railway and can be accessed at:
[https://web-production-c92a3.up.railway.app/](https://web-production-c92a3.up.railway.app/)

## Local Development

### Prerequisites

- Python 3.9+
- LibreOffice
- Docker (optional)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/erickmeikoki/docx-pdf-converter.git
   cd docx-pdf-converter
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

### Docker

To run the application using Docker:

```bash
docker build -t docx-pdf-converter .
docker run -p 8000:8000 docx-pdf-converter
```

## Deployment

The application is deployed on Railway using Docker. The deployment process includes:

1. Automatic builds from the main branch
2. Health checks for application availability
3. Automatic scaling based on demand
4. Environment variable management
5. Logging and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LibreOffice for document conversion capabilities
- Railway for hosting and deployment
- Tailwind CSS for the UI framework
