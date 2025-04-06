from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import subprocess
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'docx'}

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        docx_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{original_filename}")
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{original_filename.replace('.docx', '.pdf')}")
        
        # Save the uploaded file
        file.save(docx_path)
        
        try:
            # Convert DOCX to PDF using LibreOffice
            subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', app.config['UPLOAD_FOLDER'], docx_path], 
                         check=True)
            
            # Read the PDF file
            with open(pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            
            # Convert to base64 for preview
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            # Return both the PDF data and filename
            return jsonify({
                'filename': original_filename.replace('.docx', '.pdf'),
                'pdf_data': pdf_base64
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up files
            if os.path.exists(docx_path):
                os.remove(docx_path)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    return jsonify({'error': 'Invalid file type. Please upload a DOCX file.'}), 400

if __name__ == '__main__':
    app.run(debug=True) 