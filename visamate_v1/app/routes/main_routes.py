from flask import Blueprint,session,render_template,redirect,url_for,request,jsonify, send_from_directory
from .functions import get_db,UploadFileForm,get_file_names_without_extensions,get_app
from html import unescape
import json


main_bp = Blueprint('main', __name__)
@main_bp.route('/', methods=['GET','POST'])
def dashboard():
    form = UploadFileForm()
    if 'email' in session:
        tckn = session["tckn"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
        result = cursor.fetchone()
        conn.close()
        if result[0] == None:
            templates =  []
        else:
            templates =  json.loads(result[0])

        session['template'] = templates

        session_dict = dict(session)
        # Serialize the session dictionary into JSON format
        session_json = json.dumps(session_dict)
        session_json = unescape(session_json)

        return render_template("index.html",session= session,session_json=session_json,form = form,json=json)
    return redirect(url_for('auth.login'))


@main_bp.route('/api/delete_file')
def delete_file():
    allowed_roles = ["SuperAdmin","Admin","Customer"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('tckn')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    template_id = request.args.get("template_id")
    file_path = request.args.get("file_path")
    new_templates = []
    for template in json.loads(templates[0]):
        if template.get("template_id") == int(template_id):
            files = json.loads(template["files"])
            [files.remove(x)  for x in files if file_path in x]
            # Example usage
            folder_path = '../static/files'
            file_names_without_extensions = get_file_names_without_extensions(file_path,folder_path)


            template["files"] = json.dumps(files)
            new_templates.append(template)
        else:
            new_templates.append(template)
    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(new_templates), tckn))
    conn.commit()
    conn.close()

    return ("",204)
@main_bp.route("/api/uploaded_files")
def uploaded_files():
    #check users role and if customer only let to see own files
    #upper roles can see anyones files
    allowed_roles = ["SuperAdmin","Admin","Customer"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('tckn')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    templates= json.loads(templates[0])

    template_id = request.args.get("template_id")

    for template in templates:
        if template.get("template_id") == int(template_id):
            files = json.loads(template["files"])
    conn.close()

    return jsonify(files)

@main_bp.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    print(filename)
    return send_from_directory("../static/files", filename, as_attachment=True)
