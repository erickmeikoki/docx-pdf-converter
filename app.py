from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import subprocess
import base64
from datetime import datetime
import tempfile
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMP_FOLDER'] = 'temp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'docx'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    current_time = datetime.now()
    for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER']]:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (current_time - file_time).total_seconds() > 3600:  # 1 hour
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting file {file_path}: {e}")

@app.route('/')
def index():
    cleanup_old_files()
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check if required directories exist and are writable
        for folder in [app.config['UPLOAD_FOLDER'], app.config['TEMP_FOLDER']]:
            if not os.path.exists(folder):
                os.makedirs(folder)
            if not os.access(folder, os.W_OK):
                return jsonify({"status": "error", "message": f"Directory {folder} is not writable"}), 500
        
        # Check if LibreOffice is available
        try:
            subprocess.run(['libreoffice', '--version'], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            return jsonify({"status": "error", "message": "LibreOffice is not available"}), 500
        
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
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
                return jsonify({'error': f'Conversion failed: {str(e)}'}), 500
            except Exception as e:
                return jsonify({'error': f'An error occurred: {str(e)}'}), 500
            finally:
                # Clean up the uploaded file
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
        else:
            return jsonify({'error': 'Invalid file type. Only DOCX files are allowed.'}), 400
    
    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000))) 