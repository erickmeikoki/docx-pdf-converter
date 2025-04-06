from flask import Flask, request, jsonify, send_file, render_template
import os
import subprocess
import tempfile
import shutil
import base64
from werkzeug.utils import secure_filename
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
TEMP_FOLDER = 'temp'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'docx'}

# Ensure upload and temp directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    current_time = datetime.now()
    for folder in [UPLOAD_FOLDER, TEMP_FOLDER]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (current_time - file_time).total_seconds() > 3600:  # 1 hour
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {e}")

def check_system_health():
    """Check if all system requirements are met"""
    try:
        # Check directories
        for folder in [UPLOAD_FOLDER, TEMP_FOLDER]:
            if not os.path.exists(folder):
                os.makedirs(folder)
            if not os.access(folder, os.W_OK):
                return False, f"Directory {folder} is not writable"
        
        # Check LibreOffice
        try:
            result = subprocess.run(['libreoffice', '--version'], capture_output=True, text=True, check=True)
            if not result.stdout:
                return False, "LibreOffice version check failed"
        except subprocess.CalledProcessError as e:
            return False, f"LibreOffice check failed: {str(e)}"
        
        # Check temp file creation
        try:
            with tempfile.NamedTemporaryFile(dir=TEMP_FOLDER, delete=True) as temp_file:
                temp_file.write(b'test')
                temp_file.flush()
        except Exception as e:
            return False, f"Temp file test failed: {str(e)}"
        
        return True, "System is healthy"
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    """Root endpoint that serves as health check"""
    try:
        cleanup_old_files()
        is_healthy, message = check_system_health()
        if not is_healthy:
            return jsonify({"status": "error", "message": message}), 500
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        is_healthy, message = check_system_health()
        if not is_healthy:
            return jsonify({"status": "error", "message": message}), 500
        
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')
    if not files or not files[0]:
        return jsonify({'error': 'No selected file'}), 400
    
    results = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            try:
                # Create a temporary directory for conversion
                with tempfile.TemporaryDirectory(dir=app.config['TEMP_FOLDER']) as temp_dir:
                    # Convert DOCX to PDF using LibreOffice
                    subprocess.run([
                        'libreoffice', '--headless', '--convert-to', 'pdf',
                        '--outdir', temp_dir, file_path
                    ], check=True)
                    
                    # Get the generated PDF file
                    pdf_filename = os.path.splitext(unique_filename)[0] + '.pdf'
                    pdf_path = os.path.join(temp_dir, pdf_filename)
                    
                    # Read the PDF file
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    # Encode PDF data in base64
                    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
                    
                    results.append({
                        'filename': pdf_filename,
                        'pdf_data': pdf_base64
                    })
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Conversion failed: {str(e)}")
                return jsonify({'error': f'Conversion failed: {str(e)}'}), 500
            except Exception as e:
                logger.error(f"An error occurred: {str(e)}")
                return jsonify({'error': f'An error occurred: {str(e)}'}), 500
            finally:
                # Clean up the uploaded file
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error deleting file {file_path}: {e}")
        else:
            return jsonify({'error': 'Invalid file type. Only DOCX files are allowed.'}), 400
    
    return jsonify({'results': results})

if __name__ == '__main__':
    # Check system health before starting
    is_healthy, message = check_system_health()
    if not is_healthy:
        logger.error(f"System health check failed: {message}")
        exit(1)
    
    logger.info("Starting Flask application...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000))) 