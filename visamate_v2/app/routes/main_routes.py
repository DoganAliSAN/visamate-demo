from argparse import Namespace
from html import unescape
from flask import Blueprint,session,render_template,redirect,url_for,request,jsonify, send_from_directory
from functions import get_db,UploadFileForm,get_file_names_without_extensions,get_app,t_types,get_users,check_files,convert_name
from signature import sign_pdf
from unidecode import unidecode
from werkzeug.utils import secure_filename

import argparse
import base64
import json
import os
import tempfile
import traceback

parser = argparse.ArgumentParser(description="DALİŞ")

main_bp = Blueprint('main', __name__)

@main_bp.route('/index', methods=['GET','POST'])
@main_bp.route('/', methods=['GET','POST'])
def dashboard():
    form = UploadFileForm()
    if 'email' in session:
        tckn = session["tckn"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
        result = cursor.fetchone()
        
        templates= [] if result[0] == None else json.loads(result[0])
        session["template"]=templates
        
        return render_template("index.html",session=session,json=json,t_type= t_types,
        form=form,check_files=check_files,
        convert_name=convert_name,enumerate=enumerate,str=str,
        len=len)
    return redirect(url_for('auth.login'))


@main_bp.route('/signature',methods=['GET','POST'])
def signature():
    form = UploadFileForm()
    if request.method == 'GET':
        return render_template("signature.html",form=form)
    else:

        if form.validate_on_submit():
            file = form.file.data
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),"../static/files",secure_filename(file.filename)))
        return ('',204)

@main_bp.route('/save_superadmin_signature', methods=['POST'])
def save_superadminsignature():
    try:
        data = request.get_json()
        signature_data = data.get('signature')
        filename = f"app/static/files/signature{secure_filename(data.get('filename'))}.png"
        contract = data.get('contract')
        tckn = data.get('tckn')
        conn = get_db()
        cursor = conn.cursor()
        #contractPath contractName startX startY width height

        contract_info = cursor.execute('SELECT * from contractPaths WHERE contractPath = ?', (contract,)).fetchone()
        pdfHeight,startX,startY,width,height,page_num = round(float(contract_info[7])),int(contract_info[2]),int(contract_info[3]),int(contract_info[4]),int(contract_info[5]),int(contract_info[6])
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(signature_data.split(',')[1]))

        args = Namespace(
            pdf=contract,
            signature=filename,
            date=False,
            output =f"app/static/superadmin_contracts/contract{secure_filename(data.get('filename') + data.get('mail'))}.pdf",
            coords=f"{page_num}x{startX}x{pdfHeight-height -startY}x{width}x{height}"
        )
        result = sign_pdf(args)
        # change contractSigned status on database
        cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
        templates = cursor.fetchone()
        templates = json.loads(templates[0])
        template_id = data.get('template_id')
        new_templates = []
        for template in templates:
            if template.get("template_id") == int(template_id):
                template['superadmin_sign'] = 1
                new_templates.append(template)
            else:

                new_templates.append(template)

        cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(templates), tckn))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Signature saved successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
@main_bp.route('/save_signature', methods=['POST'])
def save_signature():
    #imzalanan dosya değişmiyor hep aynı 
    try:
        data = request.get_json()
        signature_data = data.get('signature')
        filename = f"app/static/files/signature{secure_filename(data.get('filename'))}.png"
        contract = data.get('contract')
        print(contract)
        tckn = data.get('tckn')
        conn = get_db()
        cursor = conn.cursor()
        #contractPath contractName startX startY width height

        contract_info = cursor.execute('SELECT * from contractPaths WHERE contractPath = ?', (contract,)).fetchone()
        pdfHeight,startX,startY,width,height,page_num = round(float(contract_info[7])),int(contract_info[2]),int(contract_info[3]),int(contract_info[4]),int(contract_info[5]),int(contract_info[6])
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(signature_data.split(',')[1]))

        args = Namespace(
            pdf=contract,
            signature=filename,
            date=False,
            output =f"app/static/customer_contracts/contract{contract.split('/')[-1].split('.')[0]}{secure_filename(data.get('filename'))}.pdf",
            coords=f"{page_num}x{startX}x{pdfHeight-height -startY}x{width}x{height}"
        )
        result = sign_pdf(args)
        # change contractSigned status on database
        cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
        templates = cursor.fetchone()
        templates = json.loads(templates[0])
        template_id = data.get('template_id')
        new_templates = []
        for template in templates:
            if template.get("template_id") == int(template_id):
                count= 0 
                new_contracts = []
                for cont in json.loads(template.get("contract")):
                    if cont.get("contract") == contract:
                        
                        if cont['signed'] == 1:
                            count += 1
                        else:
                            cont['signed'] = 1
                        new_contracts.append(cont)
                    else:
                        if cont['signed' ] == 1:
                            count+=1
                        new_contracts.append(cont)

                if count == len(json.loads(template.get("contract"))):
                    template["contractSigned"] = 1
                template['contract'] = json.dumps(new_contracts)
                new_templates.append(template)
            else:
                new_templates.append(template)

        cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(templates), tckn))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Signature saved successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@main_bp.route('/save_contract',methods=['GET','POST'])
def save_contract():
    form = UploadFileForm()
    if request.method == 'GET':
        return render_template("signature.html",form=form)
    else:

        if form.validate_on_submit():
            file = form.file.data
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),"../static/contracts",secure_filename(file.filename)))
            return ('',204)

        else:
            data = request.get_json()
            pdf_data = f"app/static/contracts/{secure_filename(data['filename'])}"

            conn = get_db()
            cursor = conn.cursor()


            startY = int(data['startY'])
            startX = int(data['startX'])
            width = int(data['width'])
            height = int(data['height'])
            page_num = data['page_num']
            signature_path = "signature.png"

            output = data.get('output', None)


            cursor.execute("INSERT OR REPLACE INTO contractPaths (contractPath,contractName,startX,startY,width,height,page,pdfHeight) VALUES (?,?,?,?,?,?,?,?)",(pdf_data,secure_filename(data['filename']),startX,startY,width,height,page_num,data['pdfHeight']))
            conn.commit()
            conn.close()

            return jsonify({"status":"saved"})


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
            folder_path = 'app/static/files'
            file_names_without_extensions = get_file_names_without_extensions(file_path,folder_path)


            template["files"] = json.dumps(files)
            new_templates.append(template)
        else:
            new_templates.append(template)
    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(new_templates), tckn))
    conn.commit()
    conn.close()

    if request.referrer:
        return redirect(request.referrer)
    else:
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
    return send_from_directory("app/static/", filename, as_attachment=True)


