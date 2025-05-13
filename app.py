from flask import Flask, render_template, request, redirect, url_for, session
from models import init_db, User, Contact
import os

class ContactBookApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'your_secret_key'
        self.setup_routes()

        if not os.path.exists("contact_book.db"):
            init_db()

    def setup_routes(self):
        app = self.app

        @app.route('/')
        def home():
            if 'username' not in session:
                return redirect(url_for('login'))
            user = User.get_by_username(session['username'])
            query = request.args.get('q', '').lower()
            contacts = Contact.get_all(user['id'], query)
            return render_template('home.html', contacts=contacts, username=user['username'], query=query)

        @app.route('/register', methods=['GET', 'POST'])
        def register():
            if request.method == 'POST':
                if User.register(request.form['username'], request.form['password']):
                    return redirect(url_for('login'))
                return 'Username already exists!'
            return render_template('register.html')

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                if User.authenticate(request.form['username'], request.form['password']):
                    session['username'] = request.form['username']
                    return redirect(url_for('home'))
                return 'Invalid credentials!'
            return render_template('login.html')

        @app.route('/logout')
        def logout():
            session.pop('username', None)
            return redirect(url_for('login'))

        @app.route('/add', methods=['GET', 'POST'])
        def add_contact():
            if 'username' not in session:
                return redirect(url_for('login'))
            if request.method == 'POST':
                user = User.get_by_username(session['username'])
                Contact.add(user['id'], request.form)
                return redirect(url_for('home'))
            return render_template('add_contact.html')

        @app.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
        def edit_contact(contact_id):
            if 'username' not in session:
                return redirect(url_for('login'))
            user = User.get_by_username(session['username'])
            if request.method == 'POST':
                Contact.update(contact_id, request.form)
                return redirect(url_for('home'))
            contact = Contact.get_by_id(contact_id)
            return render_template('edit_contact.html', contact=contact)

        @app.route('/delete/<int:contact_id>')
        def delete_contact(contact_id):
            if 'username' not in session:
                return redirect(url_for('login'))
            Contact.delete(contact_id)
            return redirect(url_for('home'))

    def run(self, debug=True):
        self.app.run(debug=debug)


# Create an instance and expose the app for Gunicorn
contact_book_app = ContactBookApp()
app = contact_book_app.app  # This line is critical for Gunicorn to work: gunicorn app:app

# Local dev execution
if __name__ == '__main__':
    contact_book_app.run()
