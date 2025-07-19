import os
import requests
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key_here')

# Theme Configuration
THEME = {
    'primary_color': '#2563EB',      # Blue-600
    'secondary_color': '#1E40AF',    # Blue-700
    'accent_color': '#10B981',       # Emerald-500
    'text_primary': '#2563EB',       # Blue-600
    'text_secondary': '#1E40AF',     # Blue-700
    'background_light': '#F2F2F2',   # White
    'background_dark': '#1E40AF',    # Blue-700
    'success_color': '#10B981',      # Green-500
    'warning_color': '#F59E0B',      # Yellow-500
    'error_color': '#EF4444',        # Red-500
    'border_radius': '0.5rem',
    'transition': 'all 0.3s ease'
}

# Email configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# NTFY configuration
NTFY_TOPIC = os.getenv('NTFY_TOPIC', 'aavetech_contact_form')
NTFY_SERVER = os.getenv('NTFY_SERVER', 'https://ntfy.sh')

# Initialize Flask-Mail
mail = Mail(app)

def send_ntfy_notification(name, email, subject, message):
    """Send notification via ntfy.sh"""
    try:
        title = f"New Contact Form: {subject}"
        notification = f"""
        New message from contact form:
        
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message}
        """
       
        response = requests.post(
            f"https://ntfy.sh/FngMW6MdMVya0s7A",
            data=notification.strip().encode('utf-8'),
            headers={
                'Title': title,
                'Priority': 'high',
                'Tags': 'envelope,email'
            }
        )
        print(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending ntfy notification: {e}")
        return False

def send_contact_email(name, email, subject, message):
    """Send email notification"""
    try:
        msg = Message(
            subject=f"New Contact Form: {subject}",
            recipients=[app.config['MAIL_DEFAULT_SENDER']],
            reply_to=email
        )
        
        msg.body = f"""
        You have received a new contact form submission:
        
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message}
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def home():
    return render_template('home.html', theme=THEME)

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            subject = request.form.get('subject', '').strip()
            message = request.form.get('message', '').strip()
            
            # Validate required fields
            if not all([name, email, subject, message]):
                return jsonify({
                    'success': False,
                    'message': 'All fields are required.'
                }), 400
            
            # Send email notification
            # email_sent = send_contact_email(name, email, subject, message)
            email_sent = None
            
            # Send ntfy.sh notification
            ntfy_sent = send_ntfy_notification(name, email, subject, message)
            
            if email_sent or ntfy_sent:
                return jsonify({
                    'success': True,
                    'message': 'Thank you for your message! We will get back to you soon.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to send notifications. Please try again later.'
                }), 500
                
        except Exception as e:
            print(f"Error processing contact form: {e}")
            return jsonify({
                'success': False,
                'message': 'An error occurred while processing your request.'
            }), 500
    
    return jsonify({
        'success': False,
        'message': 'Invalid request method.'
    }), 405

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)