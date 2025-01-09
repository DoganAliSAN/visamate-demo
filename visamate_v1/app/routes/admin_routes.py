from flask import Blueprint,session,render_template,redirect,url_for,request,jsonify
from .functions import all_users,t_types,get_db,UploadFileForm,get_file_names_without_extensions
from werkzeug.utils import secure_filename
import json,os
from html import unescape
admin_bp = Blueprint("admin", __name__)
@admin_bp.route('/admin')
def admin():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return redirect(url_for("main.dashboard"))
    else:
        form = UploadFileForm()
        session_dict = dict(session)
        # Serialize the session dictionary into JSON format
        session_json = json.dumps(session_dict)
        session_json = unescape(session_json)

        return render_template("admin.html",session= session,session_json=session_json,form = form,json=json)


@admin_bp.route("/addtemplate",methods=["POST","GET"])
def add_user():
    return render_template("addtemplate.html")
@admin_bp.route("/api/all_users")
def users():
    allowed_roles = ["SuperAdmin", "Admin"]
    if "email" not in session or session.get("Role") not in allowed_roles:
        return jsonify({"Error": "Permission Denied"})

    results = all_users()

    users = []
    for id, user_tuple in enumerate(results):
        user_dict = []
        for item in user_tuple:
            if isinstance(item, bytes):
                item = item.decode('utf-8')
            user_dict.append(item)
        users.append(user_dict)

    return jsonify(users)

@admin_bp.route("/api/template",methods=['GET'])
def template():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('tckn')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    result = cursor.fetchone()
    conn.close()
    for template in json.loads(result[0]):
        if session["email"] in template["incharge"]:
            return jsonify(json.loads(result[0]))
        else:
            continue



@admin_bp.route("/api/add_template",methods=['POST'])
def add_template():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('tckn')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()

    if templates == None:
        new_id = 1
    elif templates[0] == None:
        new_id = 1
    elif len(json.loads(templates[0])) == 0 :
        new_id = 1 
    else:

        old_template = json.loads(templates[0])
        new_id = old_template[-1].get("template_id") + 1

    template ={
        "template_id" : new_id,
        "incharge": request.args.get('incharge').replace("'",'\"'),
        "files": request.args.get('files').replace("'",'\"'),
        "description": request.args.get('description').replace("'",'\"'),
        "tasks": request.args.get('tasks').replace("'",'\"'),
        "comments": request.args.get('comments').replace("'",'\"'),
        "templateType": request.args.get('type').replace("'",'\"'),
        "templateStatus": 0
    }
    
    try:

        old_template.append(template)
    except:
        old_template = [template]
    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(old_template), tckn))
    conn.commit()
    conn.close()
    return jsonify(f"{template}")

@admin_bp.route("/api/add_task",methods=["POST"])
def add_task():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('user_id')
    template_id = request.args.get("template_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    templates = json.loads(templates[0])
    template_id = request.args.get("template_id")


    for temp_id,template in enumerate(templates):
        if template.get("template_id") == int(template_id):
            tasks = json.loads(template.get("tasks"))
            if len(tasks) == 0:
                task_id = 1
            else:
                task_id = int(tasks[-1].get("taskId")) + 1
            new_task = {"taskId":task_id,"task":request.form.get("task-content"),"status":0}
            tasks.append(new_task)
            template["tasks"] = json.dumps(tasks)
        templates[temp_id] = template

    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(templates), tckn))
    conn.commit()
    conn.close()

    return ("",204)
@admin_bp.route("/api/update_task",methods=['POST'])
def update_task():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('user_id')
    template_id = request.args.get("template_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()

    task_ids = [x.split("-")[1] for x in request.form]
    templates = json.loads(templates[0])


    for temp_id,template in enumerate(templates):
        if template.get("template_id") == int(template_id):

            tasks = json.loads(template.get("tasks"))
            for id,task in enumerate(tasks):
                if str(task.get("taskId")) in task_ids:
                    task["status"] = 1
                else:
                    task["status"] = 0 
                tasks[id] = task

            template["tasks"] = json.dumps(tasks)
    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(templates), tckn))
    conn.commit()
    conn.close()

    return redirect(url_for('main.dashboard'))

@admin_bp.route("/api/template_type")
def templatetype():
    allowed_roles = ["SuperAdmin","Admin","Customer"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    t_type = request.args.get('templateType')
    return jsonify(t_types(t_type))
@admin_bp.route("/api/update_files",methods=["POST"])
def update_files():
    form = UploadFileForm()
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('tckn')
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

    return redirect(url_for("admin.admin"))


@admin_bp.route("/api/update_staff")
def update_staff():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    
    conn = get_db()
    cursor = conn.cursor()

    tckn = request.args.get('tckn')
    staff_mail = request.args.get("staff_mail")
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    template_id = request.args.get("template_id")

    new_templates = []
    for template in json.loads(templates[0]):

        if template.get("template_id") == int(template_id):

            incharge = json.loads(template["incharge"])
            incharge.append(staff_mail)
            template["incharge"] = json.dumps(incharge)
            new_templates.append(template)
        else:
            new_templates.append(template)
    #save template
    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(new_templates), tckn))
    conn.commit()
    conn.close()


    return jsonify({"Success":"Staff Updated"})

#remove template
@admin_bp.route("/api/remove_template")
def remove_template():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    
    tckn = request.args.get('tckn')
    template_id = request.args.get("template_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    new_templates = []
    for template in json.loads(templates[0]):
        if template.get("template_id") == int(template_id):
            continue
        else:
            new_templates.append(template)

    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(new_templates), tckn))
    conn.commit()
    conn.close()

    return redirect(url_for("admin.admin"))


@admin_bp.route("/api/template_status")
def template_status():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('tckn')
    template_id = request.args.get("template_id")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    new_templates = []
    for template in json.loads(templates[0]):
        if template.get("template_id") == int(template_id):

            if template.get("templateStatus") == 0:
                template["templateStatus"] = 1
            else:
                template["templateStatus"] = 0
        new_templates.append(template)

    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(new_templates), tckn))
    conn.commit()
    conn.close()
    return redirect(url_for("admin.admin"))

@admin_bp.route("/api/change_templatetype")
def change_templatetype():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('tckn')
    template_id = request.args.get("template_id")
    template_type =request.args.get("templateType")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    new_templates = []
    for template in json.loads(templates[0]):
        if template.get("template_id") == int(template_id):

            template["templateType"] = template_type
        new_templates.append(template)

    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(new_templates), tckn))
    conn.commit()
    conn.close()
    return redirect(url_for("admin.admin"))