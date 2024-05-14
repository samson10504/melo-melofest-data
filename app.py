from flask import Flask, request, render_template, redirect, url_for, session
import pandas as pd
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

os.makedirs('uploads', exist_ok=True)  # Ensure the uploads directory exists

def save_upload_details():
    with open('uploads/uploads.json', 'w') as f:
        json.dump(files_info, f, indent=4)

def load_upload_details():
    global files_info
    try:
        with open('uploads/uploads.json', 'r') as f:
            files_info = json.load(f)
    except FileNotFoundError:
        files_info = {}

@app.route('/delete_file/<file_name>')
def delete_file(file_name):
    file_path = os.path.join('uploads', file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    if file_name in files_info:
        del files_info[file_name]
        save_upload_details()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    load_upload_details()
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename != '':
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            files_info[file.filename] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_upload_details()
            return redirect(url_for('index'))
    return render_template('upload.html', files_info=files_info)

@app.route('/view_data/<file_name>')
def view_data(file_name):
    file_path = os.path.join('uploads', file_name)
    try:
        file_data = pd.read_csv(file_path)
        return render_template('view_file_data.html', file_data=file_data, file_name=file_name)
    except Exception as e:
        return f"Error loading file {file_name}: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
