import os
from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import timedelta
from flask import render_template
from rag import RAGChatbot  

app = Flask(__name__)
app.config['SECRET_KEY'] = 'helloworld123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24) #24 hours session according to the task requirements
app.config['UPLOAD_FOLDER'] = 'uploads'  

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database model for users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"message": "All fields are required"}), 400
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "Username or email already exists"}), 400
    if len(password) < 8:
        return jsonify({"message": "Password must be at least 8 characters long"}), 400

    # Hashing the password and create a new user
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Login endpoint for the user
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username_or_email')
    password = data.get('password')

    user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    login_user(user)
    session.permanent = True

    return jsonify({"message": "Logged in successfully"}), 200

# Logout endpoint
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200

# API for Question Answering with RAG Chatbot
@app.route('/rag', methods=['POST'])
def ask_question():
    question = request.form.get('question')
    api_key = request.form.get('api_key')
    file = request.files.get('file')

    if not question:
        return jsonify({"error": "Question is required"}), 400
    if not api_key:
        return jsonify({"error": "API key is required"}), 400
    if not file:
        return jsonify({"error": "File is required"}), 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        rag_chatbot = RAGChatbot(file_path, api_key)
        answer = rag_chatbot.ask(question)
    finally:
        os.remove(file_path)
    
    return jsonify({"answer": answer})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) 
    with app.app_context():
        db.create_all()
    app.run(debug=True)
