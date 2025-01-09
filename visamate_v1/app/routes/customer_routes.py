from flask import Blueprint,session,redirect,url_for,render_template,request,jsonify
from .functions import get_db,UploadFileForm,get_file_names_without_extensions,secure_filename
import os,json
customer_bp  = Blueprint('customer', __name__)
@customer_bp.route("/api/template_customer",methods=['GET'])
def template_customer():
    allowed_roles = ["SuperAdmin","Admin","Customer"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = session["tckn"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    result = cursor.fetchone()
    conn.close()
    if result[0] == None:
        return jsonify([])
    else:
        return jsonify(json.loads(result[0]))

@customer_bp.route("/api/update_files_customer",methods=["POST"])
def update_files_customer():
    form = UploadFileForm()
    allowed_roles = ["SuperAdmin","Admin","Customer"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = session["tckn"]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    template_id = request.args.get("template_id")
    if form.validate_on_submit():
        file = form.file.data
        templateType = request.args.get('templateType')
        count = request.args.get('count')
        name = request.args.get('name')

        file_name = f"{name}.{file.content_type.split('/')[1]}"
        file_path = "../static/files" + "/" + secure_filename(file_name)
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),"../static/files",secure_filename(file_name)))
    else:
        return redirect(url_for('main.dashboard'))
    new_templates = []
    for template in json.loads(templates[0]):
        
        if template.get("template_id") == int(template_id):
            files = json.loads(template["files"])
            files.append(file_path)
            template["files"] = json.dumps(files)
            new_templates.append(template)
        else:
            new_templates.append(template)

    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(new_templates), tckn))
    conn.commit()
    conn.close()

    return redirect(url_for('main.dashboard'))


@customer_bp.route("/api/uploaded_files_customer")
def uploaded_files_customer():
    #check users role and if customer only let to see own files
    #upper roles can see anyones files
    allowed_roles = ["SuperAdmin","Admin","Customer"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = session["tckn"]
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

