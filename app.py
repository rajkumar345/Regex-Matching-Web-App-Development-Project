from flask import Flask, render_template, request, session
import re
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

HISTORY_FILE = 'history.json'
file_content = ''

def load_history():
    try:
        with open(HISTORY_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_history(history):
    with open(HISTORY_FILE, 'w') as file:
        json.dump(history, file)

@app.route('/')
def home():
    history = load_history()
    return render_template('index.html', history=history, file_content=file_content)

@app.route('/results', methods=['POST'])
def results():
    global file_content
    test_string = request.form.get('test_string', '')
    regex = request.form['regex']
    use_file_content = 'use_file_content' in request.form
    input_text = file_content if use_file_content else test_string
    
    matches = re.findall(regex, input_text)

    # Save history
    history = load_history()
    history.append({'type': 'regex', 'input': input_text, 'regex': regex, 'matches': matches})
    save_history(history)
    
    return render_template('index.html', matches=matches, test_string=test_string, regex=regex, file_content=file_content, history=history)

@app.route('/validate_email', methods=['POST'])
def validate_email():
    global file_content
    email_text = request.form.get('email', '')
    use_file_content = 'use_file_content' in request.form
    input_text = file_content if use_file_content else email_text
    email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    valid_emails = re.findall(email_regex, input_text)
    all_emails = re.split(r'\s|,|\n', input_text)  # Split by space, comma, or newline
    invalid_emails = [email for email in all_emails if email and email not in valid_emails]
    
    explanation = "Some emails are invalid because they don't match the expected format (e.g., example@domain.com)." if invalid_emails else ''
    
    # Save history
    history = load_history()
    history.append({'type': 'email', 'input': input_text, 'valid_emails': valid_emails, 'invalid_emails': invalid_emails, 'explanation': explanation})
    save_history(history)
    
    return render_template('index.html', email=email_text, valid_emails=valid_emails, invalid_emails=invalid_emails, explanation=explanation, file_content=file_content, history=history)

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_content
    file = request.files['file']
    file_content = file.read().decode('utf-8')
    
    return render_template('index.html', file_content=file_content, history=load_history())

if __name__ == '__main__':
    app.run(debug=True)
