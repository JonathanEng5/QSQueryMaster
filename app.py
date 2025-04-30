from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "🎉 QSQueryMaster backend is live. Use the /upload endpoint to POST a spreadsheet."

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        df = pd.read_excel(file_path)
        analysis_result = basic_analysis(df)
        return jsonify({'insights': analysis_result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def basic_analysis(df):
    issues = []
    if df.empty:
        issues.append("The spreadsheet appears to be empty.")
    else:
        issues.append(f"Spreadsheet has {len(df.columns)} columns and {len(df)} rows.")
        issues.append("First few column headers: " + ", ".join(df.columns[:5]))

        if 'Cost' in df.columns:
            if df['Cost'].isnull().any():
                issues.append("There are missing values in the 'Cost' column.")
            if (df['Cost'] <= 0).any():
                issues.append("There are zero or negative costs. Please review.")

    return issues

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)