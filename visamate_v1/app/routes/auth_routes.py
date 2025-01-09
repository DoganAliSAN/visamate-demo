from flask import Blueprint,session,redirect,url_for,render_template,request
from .functions import verify_password,user_informations
auth_bp = Blueprint('auth', __name__)

#? User Login/Logout/Register system
#! database structure
#! username lastname tckn email phoneNumber password salt role parentRoles templates
@auth_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        surname = request.form['surname']
        tckn = request.form['tckn']
        email = request.form['email']
        phone_number = request.form['phone_number']
        phone_number = "+90" + phone_number
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            return render_template("register.html",status="Passwords do not match")

        # Hash the password
        salt =  bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'),salt)
        role = ROLES["Customer"]
        parent_roles = str({ROLES["SuperAdmin"],ROLES["Admin"]})
        # Insert user into the database
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO Users (firstname, lastname, tckn, email, phoneNumber, password, salt, role, parentRoles) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (username, surname, tckn, email, phone_number, hashed_password, salt, role, parent_roles))
            db.commit()
            render_template("register.html",status="Registered successfully")
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            return render_template("register.html",status="Email already exists")
    else:
        return render_template("register.html",status="Please enter your information")

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if verify_password(email, str(password)):
            user_info = user_informations(email)
            session['username'] = user_info[0] 
            session['surname'] = user_info[1] 
            session['tckn'] = user_info[2]
            session['email'] = email 
            session['phone_number'] = user_info[4]
            session['Role'] = user_info[7]
            session['role'] = user_info[7]
            session['parent_roles'] = user_info[8]
            session['template'] = user_info[9]

            render_template("login.html",status="Logged in successfully")
            return redirect(url_for('main.dashboard'))
        else:
            return render_template("login.html",status="Password or Email is incorrect")
    else:
        return render_template("login.html",status="Please enter your information")

@auth_bp.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('main.dashboard'))
