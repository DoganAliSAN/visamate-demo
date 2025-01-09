from flask import Blueprint,session,redirect,url_for,render_template,request
from functions import verify_password,user_informations,send_mail,get_db,get_app
import bcrypt,sqlite3,time,os,json

auth_bp = Blueprint('auth', __name__)

ROLES = {
    "SuperAdmin":"SuperAdmin",
    "Admin":"Admin",
    "Customer":"Customer"
}
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
        kvkk = request.form['kvkk_acceptance']
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
            cursor.execute("INSERT INTO Users (firstname, lastname, tckn, email, phoneNumber, password, salt, role, parentRoles, templates,kvkk) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (username, surname, tckn, email, phone_number, hashed_password, salt, role, parent_roles,"[]",kvkk))
            db.commit()
            render_template("register.html",status="Registered successfully")
            message_html =f"""
                <!DOCTYPE html>
                <html lang="tr">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Kayıt Başarılı</title>
                    </head>
                    <body>
                        <h1>Hoş Geldiniz!</h1>
                        <p>Merhaba { username },</p>
                        <p>Başarılı bir şekilde kayıt oldunuz. Artık uygulamamıza giriş yapabilirsiniz.</p>
                        <p>Detaylarınız:</p>
                        <ul>
                            <li><strong>Adı:</strong> { username }</li>
                            <li><strong>Soyadı:</strong> { surname }</li>
                            <li><strong>TC Kimlik Numarası:</strong> { tckn }</li>
                            <li><strong>Email:</strong> { email }</li>
                            <li><strong>Telefon Numarası:</strong> { phone_number }</li>
                        </ul>
                        <p>Giriş yapmak için aşağıdaki linke tıklayabilirsiniz:</p>
                        <p><a href="{ url_for('auth.login') }">Giriş Yap</a></p>
                        <p>Sorularınız için bize ulaşmaktan çekinmeyin. İyi günler dileriz!</p>
                    </body>
                </html>
            """
            

            send_mail(title="Kayıt Başarılı",message=message_html,recipients=[email])
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError as e:

            if "phoneNumber" in e.args[0]:
                return render_template("register.html",status="Numara Önceden Kaydedilmiş")
            elif "email" in e.args[0]:
                return render_template("register.html",status="Email Önceden Kaydedilmiş")
        except sqlite3.OperationalError:
            db.close()
            
    else:
        return render_template("register.html",status="Lütfen Bilgilerinizi Giriniz")

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
            session['cookies'] = request.form.get('cookies')
            render_template("login.html",status="Logged in successfully")
            return redirect(url_for('main.dashboard'))
        else:
            return render_template("login.html",status="Şifre veya Email Yanlış")
    else:
        return render_template("login.html",status="Lütfen Bilgilerinizi Giriniz")

@auth_bp.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('main.dashboard'))
