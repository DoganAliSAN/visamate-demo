from html import unescape
from flask import Blueprint,session,render_template,redirect,url_for,request,jsonify
from functions import all_users,t_types,get_db,UploadFileForm,get_file_names_without_extensions,get_users,check_files,convert_name,send_mail,get_templates,update_templates,template_tasks
from werkzeug.utils import secure_filename
import datetime 

import json
import os

admin_bp = Blueprint("admin", __name__)
@admin_bp.route("/superadmin")
def superadmin():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return redirect(url_for("main.dashboard"))
    else:
        form = UploadFileForm()
        users = get_users(get_db(),get_db().cursor())
        return render_template("superadmin.html",
        session=session,
        users=users,json=json,t_type= t_types,
        form=form,check_files=check_files,
        convert_name=convert_name,enumerate=enumerate,str=str,
        len=len,secure_filename=secure_filename)
@admin_bp.route('/admin')
def admin():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return redirect(url_for("main.dashboard"))
    else:
        if session.get("Role") == "SuperAdmin":
            return redirect(url_for("admin.superadmin"))
            
        form = UploadFileForm()
        users = get_users(get_db(),get_db().cursor())
        conn = get_db()
        cursor = conn.cursor()
        contracts = cursor.execute('SELECT * FROM contractPaths').fetchall()

        return render_template("admin.html",
        session=session,
        users=users,json=json,t_type= t_types,
        form=form,check_files=check_files,
        convert_name=convert_name,enumerate=enumerate,str=str,
        len=len,secure_filename=secure_filename,contracts=contracts)


@admin_bp.route("/addtemplate",methods=["POST","GET"])
def add_user():
    allowed_roles = ["SuperAdmin", "Admin"]
    if "email" not in session or session.get("Role") not in allowed_roles:
        return jsonify({"Error": "Permission Denied"})

    users = get_users(get_db(),get_db().cursor())
    conn = get_db()
    cursor = conn.cursor()
    contracts = cursor.execute('SELECT * FROM contractPaths').fetchall()
    conn.close()

    return render_template("addtemplate.html",users=users,session=session,contracts=contracts)
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
    templates =get_templates(session,tckn)
    for template in templates:
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
    templates = get_templates(session,tckn)
    contracts = []
    for arg in request.args:
        if "contract" in arg:
            contracts.append({"signed":0,"contract":request.args.get(arg)})

    if templates == None:
        new_id = 1
    elif len(templates) == 0 :
        new_id = 1 
    elif templates[0] == None:
        new_id = 1
    else:
        old_template = templates
        new_id = old_template[-1].get("template_id") + 1

    templateType = request.args.get('type').replace("'",'\"')
    tasks = template_tasks(templateType)
    new_tasks = []
    for id_,task in enumerate(tasks):
        one_week_after = (datetime.datetime.now() + datetime.timedelta(weeks=1)).date()
        formatted_date = one_week_after.strftime("%Y-%m-%d")
        task = {"taskId":id_+1,"task":task,"status":0,"taskDate":formatted_date,"visibility":0}
        new_tasks.append(task)
    #new_tasks = f"{new_tasks}".replace("'",'"')
    template ={
        "template_id" : new_id,
        "incharge": request.args.get('incharge').replace("'",'\"'),
        "files": request.args.get('files').replace("'",'\"'),
        "description": request.args.get('description').replace("'",'\"'),
        "tasks":new_tasks,
        "comments": request.args.get('comments').replace("'",'\"'),
        "templateType": templateType,
        "templateStatus": 2,
        "contract": f"{contracts}".replace("'",'\"'),
        "contractSigned": 0,
        "superadmin": "[]"
    }
    
    try:

        old_template.append(template)
    except:
        old_template = [template]
    update_templates(session,tckn,old_template)

    return jsonify(f"{template}")

@admin_bp.route("/api/add_task",methods=["POST"])
def add_task():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('user_id')
    template_id = request.args.get("template_id")
    templates = get_templates(session,tckn)
    visibility =  0 if request.form.get("visibleToCustomer") == None else 1

    for temp_id,template in enumerate(templates):
        if template.get("template_id") == int(template_id):
            tasks = json.loads(template.get("tasks"))
            if len(tasks) == 0:
                task_id = 1
            else:
                task_id = int(tasks[-1].get("taskId")) + 1
            new_task = {"taskId":task_id,"task":request.form.get("task-content"),"status":0,"taskDate":request.form.get("taskDate"),"visibility":visibility}
            tasks.append(new_task)
            template["tasks"] = json.dumps(tasks)
        templates[temp_id] = template

    update_templates(session,tckn,templates)
    return redirect(url_for("admin.admin"))
@admin_bp.route("/api/delete_task")
def delete_task():
    tckn = request.args.get('tckn')
    taskId = request.args.get('taskId')
    templates = get_templates(session,tckn)
    template_id = request.args.get("template_id")
    new_templates = []
    for template in templates:
        if template.get("template_id") == int(template_id):
            tasks = json.loads(template["tasks"])
            [tasks.remove(x) for x in tasks if x.get("taskId") == int(taskId)]
            template["tasks"] = json.dumps(tasks)
            new_templates.append(template)
    update_templates(session,tckn,new_templates)
    return redirect(url_for("admin.admin"))


@admin_bp.route("/api/update_task",methods=['POST'])
def update_task():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('user_id')
    template_id = request.args.get("template_id")
    templates = get_templates(session,tckn)
    task_ids = [x.split("-")[1] for x in request.form]
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
    update_templates(session,tckn,templates)

    return redirect(url_for('admin.admin'))

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
    template_id = request.args.get("template_id")

    templates = get_templates(session,tckn)
    if form.validate_on_submit():
        file = form.file.data
        name = request.args.get('name')
        keyword = name.lower().split("_")[0]
        if keyword not in file.filename:
            return redirect(url_for('admin.admin'))
        file_name = f"{name}.{file.content_type.split('/')[1]}"
        file_path = "app/static/files/"+ secure_filename(file_name)

        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),"../static/files",secure_filename(file_name)))
    else:
        return redirect(url_for('admin.admin'))
    new_templates = []
    for template in templates:
        
        if template.get("template_id") == int(template_id):
            files = json.loads(template["files"])
            files.append(file_path)
            template["files"] = json.dumps(files)
            new_templates.append(template)
        else:
            new_templates.append(template)

    update_templates(session,tckn,new_templates)
    return redirect(url_for("admin.admin"))


@admin_bp.route("/api/update_staff",methods=['POST'])
def update_staff():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})

    tckn = request.args.get('tckn')
    staff_mail = request.form.get("staff_mail")
    template_id = request.args.get("template_id")
    templates = get_templates(session,tckn)

    new_templates = []
    for template in templates:

        if template.get("template_id") == int(template_id):
            incharge = json.loads(template["incharge"])
            incharge.append(staff_mail)
            template["incharge"] = json.dumps(incharge)
            new_templates.append(template)
        else:
            new_templates.append(template)
    
    update_templates(session,tckn,new_templates)


    return redirect(url_for("admin.admin"))

@admin_bp.route("/api/delete_staff")
def delete_staff():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})

    tckn = request.args.get('tckn')
    staff_mail = request.args.get("staff_mail")
    template_id = request.args.get("template_id")

    templates = get_templates(session,tckn)

    new_templates = []
    for template in templates:

        if template.get("template_id") == int(template_id):

            incharge = json.loads(template["incharge"])
            incharge.remove(staff_mail)
            template["incharge"] = json.dumps(incharge)
            new_templates.append(template)
        else:
            new_templates.append(template)
    
    update_templates(session,tckn,new_templates)
    return redirect(url_for("admin.admin"))

@admin_bp.route("/api/remove_template")
def remove_template():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    
    tckn = request.args.get('tckn')
    template_id = request.args.get("template_id")
    templates = get_templates(session,tckn)
    new_templates = []
    for template in templates:
        if template.get("template_id") == int(template_id):
            files = json.loads(template.get("files"))
            for i in files:
                try:
                    os.remove(i)
                except Exception as e:
                    print(e)
            
        else:
            new_templates.append(template)

    update_templates(session,tckn,new_templates)

    return redirect(url_for("admin.admin"))


@admin_bp.route("/api/template_status")
def template_status():
    #leaving this one with no get_templates because it can make things complicated for now 
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    conn = get_db()
    cursor = conn.cursor()
    tckn = request.args.get('tckn')
    if len(tckn) == 4:

        cursor.execute("SELECT templates FROM Users WHERE substr(tckn, -4) = ?", (tckn[-4:],))
        templates= cursor.fetchone()
        cursor.execute("SELECT email FROM Users WHERE substr(tckn, -4) = ?", (tckn[-4:],))
        user_email = cursor.fetchone()

    else:

        cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
        templates = cursor.fetchone()
        cursor.execute("SELECT email FROM Users WHERE tckn = ?", (tckn,))
        user_email = cursor.fetchone()

    template_id = request.args.get("template_id")
    template_status = request.args.get("templateStatus")

    user_email = user_email[0]
    new_templates = []
    for template in json.loads(templates[0]):
        if template.get("template_id") == int(template_id):

            if int(template.get("templateStatus")) == 0:
                template["templateStatus"] = int(template_status)
            else:
                template["templateStatus"] = int(template_status)

            msg= open("app/static/email_msg/msg.html","r").read().format(email=session["email"],status=template["templateStatus"],type=template["templateType"],incharge=template["incharge"],template_id=template_id,tckn=tckn,template=template)
            send_mail(title="Template Durumu değiştirildi",message=msg,recipients=["sandoganali187@gmail.com"])
        new_templates.append(template)
    if len(tckn) == 4 :

        cursor.execute("UPDATE Users SET templates = ? WHERE substr(tckn, -4) = ?", (json.dumps(new_templates), tckn[-4:]))
        conn.commit()
        conn.close()
    else:

        cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(new_templates), tckn))
        conn.commit()
        conn.close()

    return ("",204)

@admin_bp.route("/api/change_templatetype")
def change_templatetype():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    tckn = request.args.get('tckn')
    template_id = request.args.get("template_id")
    template_type =request.args.get("templateType")

    templates = get_templates(session,tckn)
    new_templates = []
    for template in templates:
        if template.get("template_id") == int(template_id):

            template["templateType"] = template_type
        new_templates.append(template)

    update_templates(session,tckn,new_templates)
    return redirect(url_for("admin.admin"))

@admin_bp.route("/api/add_comment",methods=["POST"])
def add_comment():

    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    
    tckn = request.args.get("tckn")
    comment = request.form.get("comment")

    template_id = request.args.get("template_id")

    templates = get_templates(session,tckn)
    new_templates = []
    for template in templates:
        if template.get("template_id") == int(template_id):

            comments = json.loads(template.get("comments"))
            comment = {"id":session["email"],"comment":comment}
            comments.append(comment)
            template["comments"] = json.dumps(comments)
            new_templates.append(template)
        else:
            new_templates.append(template)
    
    update_templates(session,tckn,new_templates)
    return redirect(url_for("admin.admin"))

@admin_bp.route("/api/remove_contract")
def remove_contract():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    
    tckn = request.args.get('tckn')
    template_id = request.args.get('template_id')
    contract = request.args.get('contract').replace("'",'"')
    templates = get_templates(session,tckn)
    new_templates = []
    for template in templates:
        if template.get("template_id") == int(template_id):
            contracts = []
            for cont in json.loads(template["contract"]):
                if cont.get("contract") == json.loads(contract).get("contract"):

                    cont['signed']= 0
                    contracts.append(cont)
                else:
                    contracts.append(cont)
            template["contract"] = json.dumps(contracts)
            template["contractSigned"] = 0
            new_templates.append(template)
        else:
            new_templates.append(template)

    update_templates(session,tckn,new_templates)
    return redirect(url_for("admin.admin"))

@admin_bp.route("/api/superadmin_contract",methods=["POST"])
def superadmin_contract():
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})

    tckn = request.args.get('tckn')
    template_id = request.args.get('template_id')
    superadmin_email = request.form.get("superadmin")
    templates = get_templates(session,tckn)

    new_templates = []
    for template in templates:

        if template.get("template_id") == int(template_id):
            try:
                incharge = json.loads(template["superadmin"])
            except:
                incharge = []
            incharge.append(superadmin_email)
            template["superadmin_contract"] = request.form.get("contract")
            template["superadmin"] = json.dumps(incharge)
            template["superadmin_sign"] = 0 

            new_templates.append(template)
        else:
            new_templates.append(template)
    
    update_templates(session,tckn,new_templates)

    return redirect(url_for("admin.admin"))
