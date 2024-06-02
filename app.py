from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mail import Mail, Message
import os
import google.generativeai as genai

app = Flask(__name__)
load_dotenv()

# Set up Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)

# Set up Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Generate a secret key
secret_key = os.urandom(24)
app.config["SECRET_KEY"] = secret_key

# Rendering loader page
@app.route("/", methods=['GET', 'POST'])
def load():
    return render_template("loader.html")

# Rendering home page
@app.route("/home", methods=['GET', 'POST'])
def home():
    return render_template("home.html")

# Rendering about page
@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template("about.html")

# Rendering contact page
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template("contact.html")

# Endpoint to handle text and store it in the database
@app.route("/gemini", methods=['GET', 'POST'])
def text():
    data = session.get('data', [])

    if request.method == "POST":
        input_text = request.form.get("text")

        if input_text:
            # Using generative AI model to generate content
            model = genai.GenerativeModel(model_name="gemini-pro")
            response = model.generate_content(input_text)
            text_result = response.text
            
            data.append({'input': input_text, 'result': text_result})
            session['data'] = data

            return redirect(url_for('text'))
        
        else:
            flash("Please provide a valid input!", "error")

    return render_template("index.html", data=data[::-1])

@app.route("/logout")
def logout():
    session.pop('data', None)
    return redirect(url_for('load'))

# Endpoint to handle form submission for sending an email
@app.route('/send-mail', methods=['POST'])
def send_email():
    # Extracting data from the submitted form
    subject = request.form['text']
    mail_address = request.form['mail']
    message_content = request.form['text_area']

    # Checking if all required fields are filled before proceeding
    if subject and mail_address and message_content:
        # Creating an email message object using Flask-Mail's Message class
        msg = Message(subject, sender=mail_address, recipients=['ftkhnssss3@gmail.com'])
        
        # Rendering HTML content for the email using a Jinja template named 'mail.html'
        html_content = render_template('mail.html', subject=subject, mail_adress=mail_address, content=message_content)
        msg.html = html_content  # Setting the HTML content of the email message
        
        # Sending the email message using Flask-Mail's send method
        mail.send(msg)
        flash("Email sent!", "success")
    
    return render_template("contact.html")

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
