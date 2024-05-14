from flask import Flask, request, render_template, redirect, url_for, session, jsonify, make_response
import pandas as pd
import os
import json
from datetime import datetime
import urllib.parse  # Import the parse module

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace 'your_secret_key' with a real secret key

# Ensure the uploads directory exists
os.makedirs('/tmp/uploads', exist_ok=True)

def save_upload_details(file_name, upload_time):
    data = {}
    file_path = '/tmp/uploads/uploads.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
    data[file_name] = upload_time
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    files_info = {}
    try:
        with open('/tmp/uploads/uploads.json', 'r') as f:
            files_info = json.load(f)
    except FileNotFoundError:
        pass  # No uploads.json file yet

    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename != '':
            filename = file.filename.replace(' ', '_')
            file_path = os.path.join('/tmp/uploads', filename)
            file.save(file_path)
            upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_upload_details(filename, upload_time)
            session['file_path'] = file_path
            session['upload_time'] = upload_time
            return redirect(url_for('view_data'))
    return render_template('upload.html', files_info=files_info)

@app.route('/data', methods=['GET'])
def view_data():
    if 'file_path' in session:
        file_data = pd.read_csv(session['file_path'])
        variants = file_data['Variant'].value_counts()
        total_variants = file_data['Variant'].count()
        return render_template('data_view.html', variants=variants, total_variants=total_variants, upload_time=session['upload_time'])
    return redirect(url_for('index'))

@app.route('/variant/<path:variant_name>', methods=['GET'])
def variant_detail(variant_name):
    variant_name = urllib.parse.unquote(variant_name)  # Decode the variant name
    if 'file_path' in session:
        file_data = pd.read_csv(session['file_path'])
        variant_data = file_data[file_data['Variant'] == variant_name][['Surname', 'First Name/Nickname', 'Email', 'Variant', 'Company/University:']]
        return render_template('variant_detail.html', variant_data=variant_data, variant_name=variant_name)
    return redirect(url_for('index'))


@app.route('/all_variants', methods=['GET'])
def all_variants_detail():
    if 'file_path' in session:
        file_data = pd.read_csv(session['file_path'])
        all_data = file_data[['Surname', 'First Name/Nickname', 'Email', 'Variant', 'Company/University:']]
        return render_template('all_variants_detail.html', all_data=all_data)

@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = os.path.join('/tmp/uploads', filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        # Update JSON
        with open('/tmp/uploads/uploads.json', 'r+') as f:
            data = json.load(f)
            # Remove the entry for the deleted file
            if filename in data:
                del data[filename]
                f.seek(0)  # Reset file position to the beginning of the file
                json.dump(data, f, indent=4)  # Write the updated JSON data
                f.truncate()  # Remove any trailing data that is no longer part of the JSON
        return redirect(url_for('index'))
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
