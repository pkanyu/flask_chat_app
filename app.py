from flask import Flask, render_template, request, jsonify,redirect,session
import pymysql
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = "34738y834rcehrcn45xy8n8r5y8ux379ntyhc c8rxuy78931xynhjDFBGYUGNH@#$%^&%!@#$%"

# Replace with your MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'chat_db'
}

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

@app.route('/')
def index():
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    return render_template('index.html', users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Fetch user data from the database based on username
        query = "SELECT id, username, password FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user_data = cursor.fetchone()
        
        if user_data and check_password_hash(user_data[2], password):
            # Successful login
            session['user_id'] = user_data[0]
            return redirect('/')
        else:
            # Failed login
            return "Login failed"
    
    return render_template('login.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_id = int(data['sender_id'])
    receiver_id = int(data['receiver_id'])
    content = data['content']
    
    query = "INSERT INTO messages (sender_id, receiver_id, content) VALUES (%s, %s, %s)"
    cursor.execute(query, (sender_id, receiver_id, content))
    conn.commit()

    return jsonify({'status': 'Message sent successfully'})



@app.route('/get_messages/<int:sender_id>/<int:receiver_id>')
def get_messages(sender_id, receiver_id):
    query = """
    SELECT sender_id, content, timestamp FROM messages
    WHERE (sender_id = %s AND receiver_id = %s)
    OR (sender_id = %s AND receiver_id = %s)
    ORDER BY timestamp
    """
    cursor.execute(query, (sender_id, receiver_id, receiver_id, sender_id))
    messages = cursor.fetchall()
    message_list = [{'sender_id': msg[0], 'content': msg[1], 'timestamp': msg[2]} for msg in messages]
    return jsonify(message_list)


from werkzeug.security import generate_password_hash

# ...

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password, method='sha256')
        
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))
        conn.commit()
        
        return "Registration successful"
    
    return render_template('register.html')

# ...

@app.route('/chat/<int:receiver_id>')
def chat(receiver_id):
    sender_id = session.get('user_id')  # Get the logged-in user's ID from the session
    if sender_id is None:
        # Handle the case where the user is not logged in
        return "You need to log in to use the chat."
    
    messages = get_messages(sender_id, receiver_id)
    return render_template('chat.html', sender_id=sender_id, receiver_id=receiver_id, messages=messages)


def get_messages(sender_id, receiver_id):
    query = """
    SELECT sender_id, content, timestamp FROM messages
    WHERE (sender_id = %s AND receiver_id = %s)
    OR (sender_id = %s AND receiver_id = %s)
    ORDER BY timestamp
    """
    cursor.execute(query, (sender_id, receiver_id, receiver_id, sender_id))
    messages = cursor.fetchall()
    return [{'sender_id': msg[0], 'content': msg[1], 'timestamp': msg[2]} for msg in messages]

# ...







if __name__ == '__main__':
    app.run(debug=True)     
