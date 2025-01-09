from flask import Flask,request, redirect, url_for, render_template, g, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_mail import Mail
from flask_mail import Message

from wtforms.validators import InputRequired
from wtforms import SubmitField,HiddenField
from werkzeug.utils import secure_filename
from unidecode import unidecode

import bcrypt,sqlite3,time,os,json

def get_app():


    app = Flask(__name__,template_folder='app/templates',static_folder='app/static')
    app.secret_key = "!g2q_q*p#!6j)nmdnb170&)y4i54!l2)ji&w7u%e16i5n^2)" 

    app.config['DATABASE'] = 'app/main.db'
    app.config['UPLOAD_FOLDER'] = 'static/files'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587

    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'visamateinformation@gmail.com'
    app.config['MAIL_PASSWORD'] = 'nqmf lftv mhaw tiba'
    return app
def send_mail(title, message, recipients):
    app = get_app()
    mail = Mail(app)


    with app.app_context():
        msg = Message(title, sender="visamateinformation@gmail.com", recipients=recipients)
        msg.html = message

        mail.send(msg)

def get_db():
    import os
    logging.info("Current directory of functions: {}".format(os.getcwd()))
    app = get_app()
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

def verify_password(email, input_password):
    conn = get_db()
    cursor = conn.cursor()

    # Retrieve hashed password and salt from the database based on email
    cursor.execute("SELECT password, Salt FROM Users WHERE email = ?", (email,))
    result = cursor.fetchone()  # Fetch the first result



    if result:
        hashed_password = result[0]
        salt = result[1]

        # Use the stored salt to generate the hash of the input password
        input_hashed_password = bcrypt.hashpw(input_password.encode('utf-8'), salt)

        # Compare the hashed input password with the stored hashed password
        return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)
    else:
        return False  # Email not found in the database

def user_informations(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
    result = cursor.fetchone()  # Fetch the first result
    conn.close()
    return result
def all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    result = cursor.fetchall()  # Fetch the first result
    conn.close()
    return result


def t_types(l_type):
    t_types = {
        "81A":["Başvuru Formu","Diploma (Yeminli tercümeli)","Transkript (Yeminli tercümeli)","Özgeçmiş(CV) ,(Almanca)","Pasaport ve kimlik fotokopisi","SSK Hizmet dökümü (ıslak imzalı,apostilli)","Çalışma belgesi","Referans yazısı","iş başvurusu veya iş sözleşmesi çıktısı","Staj belgesi (lise mezunları için) ,(opsiyonel)","Çerçeve eğitim programı (Kalfalık mezunları için ), (opsiyonel)"],
        "AUSBILDUNG":["Özgeçmiş Detaylı","Kimlik Belgesi (kimlik kartı fotokopisi ve pasaport fotokopisi ile kayıt belgesi fotokopisi)","Orijinal diplomanın/derecenin ve eyalet tanınırlığının kopyası(apostil)","Konunun ve not özetinin kopyası (örn. diploma eki, çalışma kitabı, kayıtların transkripti) ve apostili","İlgili mesleki deneyim ve diğer niteliklerin kanıtı (staj belgeleri ve sgk dökümü ve apostili)","dil sertifikası"],
        "MAVIKART": [
        "Pasaport ve kimlik fotokopisi ve 1 Adet Biyometrik Fotoğraf",
        "Üniversite Diplomasi, Transkript ve Anabin (veya ZAB) onayı",
        "İş sözleşmesi veya somut iş teklifi (ıslak imzalı-kaşeli)",
        "İş pozisyon tanımı formu (işveren tarafından doldurulacak)",
        "SSK Hizmet dökümü (ıslak imzalı,apostilli)",
        "Çalışma belgesi(Antetli Kağıda)",
        "Referans yazısı (ıslak imzalı , firma ise kaşeli ,referans olanın iletişim bilgileri)",
        "Özgeçmiş(CV) ,(Almanca)",
        "Evlilik Cüzdanı(ilk 4 sayfası)",
        "Eş-Çocuk için Pasaport ve Kimlik bilgileri",
        "Çocuklar için Öğrenci Belgesi",
        "Sahip olunan Sertifikalar, Belgeler ve katılımcılığı kanıtlanabilir programlar",
        "Meslek izni – (Sadece mühendislik, doktorluk gibi onay gerektiren meslekler için)",
        "Sağlık sigortası teyidi",
        "Staj belgesi (lise mezunları için) ,(opsiyonel)",
        "Çerçeve eğitim programı (Kalfalık mezunları için ), (opsiyonel)"],
        "SCHENGEN":[
        "Pasaport , Pasaport ilk sayfa fotokopisi ve kimlik fotokopisi ve 2 adet Biometrik fotoğraf",
        "Pasaport Protokol Evrağı (E-Devlet)",
        "Yerleşim Yeri ve Diğer Adres Belgesi (E-Devlet)",
        "Vukuatlı Nüfus Kayıt Örneği Belgesi (E-Devlet)",
        "Niyet Mektubu Yazılması İçin Kısaca Özgeçmiş",
        "Öğrenci Belgesi (Çocuklarınız İçin)",
        "İzin Yazısı (Antetli Kağıda)",
        "SGK Dökümü ve İşe Giriş Belgesi (E-Devlet)",
        "Son 3 Aylık Islak İmzalı Maaş Bordrosu",
        "Son 3 Aylık Banka Ekstresi",
        "Araç Ruhsatı ve Tapu Fotokopisi (varsa)",
        "Çalışma Belgesi (Antetli Kağıda)",
        "Sponsor Dilekçesi (Kaşe – İmza)",
        "Sponsor Vergi Levhası",
        "Sponsor Oda Kayıt/Faaliyet Belgesi",
        "Sponsor İmza Sirküleri",
        "Sponsor Ticaret Sicil Gazetesi",
        "Sponsor Vukuatlı Nüfus Kayıt Örneği (E-Devlet)",
        "Sponsor Yerleşim Yeri ve Diğer Adres Belgesi (E-Devlet)",
        "Kişiye Sponsorluğa dair Noter Onaylı Karar Örneği ve Bu kararın Kaymakamlık tarafından Apostili",
        "Sponsor Son 3 Aylık Banka Hesap Dökümü",
        "18 Yaşını doldurmamış bireylerin ebeveynleri Noterden alacağı Muvafakatname örneği"],
        "19C":["Pasaport","Ehliyet","Sgk Hizmet Dökümü","CV","Vekalet - Personel","Vekalet - İşveren","İş Sözleşmesi","İş ilişkisi beyanı","Diploma","Sertifika"]
    }
    conn = get_db()
    cursor = conn.cursor()
    filenames = [x[0] for x in cursor.execute("SELECT * FROM fileNames WHERE templateType = ? ",(l_type,)).fetchall()]
    return filenames
def t_types_backend(l_type):
    t_types = {
        "81A":[{'text': 'BAŞVURU_FORMU', 'id': 0}, {'text': 'DIPLOMA_(YEMINLI_TERCÜMELI)', 'id': 1}, {'text': 'TRANSKRIPT_(YEMINLI_TERCÜMELI)', 'id': 2}, {'text': 'ÖZGEÇMIŞ(CV)_(ALMANCA)', 'id': 3}, {'text': 'PASAPORT_VE_KIMLIK_FOTOKOPISI', 'id': 4}, {'text': 'SSK_HIZMET_DÖKÜMÜ_(ISLAK_IMZALIAPOSTILLI)', 'id': 5}, {'text': 'ÇALIŞMA_BELGESI', 'id': 6}, {'text': 'REFERANS_YAZISI', 'id': 7}, {'text': 'IŞ_BAŞVURUSU_VEYA_IŞ_SÖZLEŞMESI_ÇIKTISI', 'id': 8}, {'text': 'STAJ_BELGESI_(LISE_MEZUNLARI_IÇIN)_(OPSIYONEL)', 'id': 9}, {'text': 'ÇERÇEVE_EĞITIM_PROGRAMI_(KALFALIK_MEZUNLARI_IÇIN_)_(OPSIYONEL)', 'id': 10}],
        "AUSBILDUNG":[{'text': 'ÖZGEÇMIŞ_DETAYLI', 'id': 0}, {'text': 'KIMLIK_BELGESI_(KIMLIK_KARTI_FOTOKOPISI_VE_PASAPORT_FOTOKOPISI_ILE_KAYIT_BELGESI_FOTOKOPISI)', 'id': 1}, {'text': 'ORIJINAL_DIPLOMANIN/DERECENIN_VE_EYALET_TANINIRLIĞININ_KOPYASI(APOSTIL)', 'id': 2}, {'text': 'KONUNUN_VE_NOT_ÖZETININ_KOPYASI_(ÖRN._DIPLOMA_EKI_ÇALIŞMA_KITABI_KAYITLARIN_TRANSKRIPTI)_VE_APOSTILI', 'id': 3}, {'text': 'İLGILI_MESLEKI_DENEYIM_VE_DIĞER_NITELIKLERIN_KANITI_(STAJ_BELGELERI_VE_SGK_DÖKÜMÜ_VE_APOSTILI)', 'id': 4}, {'text': 'DIL_SERTIFIKASI', 'id': 5}],
        "MAVIKART":[{'text': 'PASAPORT_VE_KIMLIK_FOTOKOPISI_VE_1_ADET_BIYOMETRIK_FOTOĞRAF', 'id': 0}, {'text': 'ÜNIVERSITE_DIPLOMASI_TRANSKRIPT_VE_ANABIN_(VEYA_ZAB)_ONAYI', 'id': 1}, {'text': 'İŞ_SÖZLEŞMESI_VEYA_SOMUT_IŞ_TEKLIFI_(ISLAK_IMZALI-KAŞELI)', 'id': 2}, {'text': 'İŞ_POZISYON_TANIMI_FORMU_(IŞVEREN_TARAFINDAN_DOLDURULACAK)', 'id': 3}, {'text': 'SSK_HIZMET_DÖKÜMÜ_(ISLAK_IMZALIAPOSTILLI)', 'id': 4}, {'text': 'ÇALIŞMA_BELGESI(ANTETLI_KAĞIDA)', 'id': 5}, {'text': 'REFERANS_YAZISI_(ISLAK_IMZALI__FIRMA_ISE_KAŞELI_REFERANS_OLANIN_ILETIŞIM_BILGILERI)', 'id': 6}, {'text': 'ÖZGEÇMIŞ(CV)_(ALMANCA)', 'id': 7}, {'text': 'EVLILIK_CÜZDANI(ILK_4_SAYFASI)', 'id': 8}, {'text': 'EŞ-ÇOCUK_IÇIN_PASAPORT_VE_KIMLIK_BILGILERI', 'id': 9}, {'text': 'ÇOCUKLAR_IÇIN_ÖĞRENCI_BELGESI', 'id': 10}, {'text': 'SAHIP_OLUNAN_SERTIFIKALAR_BELGELER_VE_KATILIMCILIĞI_KANITLANABILIR_PROGRAMLAR', 'id': 11}, {'text': 'MESLEK_IZNI_–_(SADECE_MÜHENDISLIK_DOKTORLUK_GIBI_ONAY_GEREKTIREN_MESLEKLER_IÇIN)', 'id': 12}, {'text': 'SAĞLIK_SIGORTASI_TEYIDI', 'id': 13}, {'text': 'STAJ_BELGESI_(LISE_MEZUNLARI_IÇIN)_(OPSIYONEL)', 'id': 14}, {'text': 'ÇERÇEVE_EĞITIM_PROGRAMI_(KALFALIK_MEZUNLARI_IÇIN_)_(OPSIYONEL)', 'id': 15}],
        "SCHENGEN":[{'text': 'PASAPORT__PASAPORT_ILK_SAYFA_FOTOKOPISI_VE_KIMLIK_FOTOKOPISI_VE_2_ADET_BIOMETRIK_FOTOĞRAF', 'id': 0}, {'text': 'PASAPORT_PROTOKOL_EVRAĞI_(E-DEVLET)', 'id': 1}, {'text': 'YERLEŞIM_YERI_VE_DIĞER_ADRES_BELGESI_(E-DEVLET)', 'id': 2}, {'text': 'VUKUATLI_NÜFUS_KAYIT_ÖRNEĞI_BELGESI_(E-DEVLET)', 'id': 3}, {'text': 'NIYET_MEKTUBU_YAZILMASI_İÇIN_KISACA_ÖZGEÇMIŞ', 'id': 4}, {'text': 'ÖĞRENCI_BELGESI_(ÇOCUKLARINIZ_İÇIN)', 'id': 5}, {'text': 'İZIN_YAZISI_(ANTETLI_KAĞIDA)', 'id': 6}, {'text': 'SGK_DÖKÜMÜ_VE_İŞE_GIRIŞ_BELGESI_(E-DEVLET)', 'id': 7}, {'text': 'SON_3_AYLIK_ISLAK_İMZALI_MAAŞ_BORDROSU', 'id': 8}, {'text': 'SON_3_AYLIK_BANKA_EKSTRESI', 'id': 9}, {'text': 'ARAÇ_RUHSATI_VE_TAPU_FOTOKOPISI_(VARSA)', 'id': 10}, {'text': 'ÇALIŞMA_BELGESI_(ANTETLI_KAĞIDA)', 'id': 11}, {'text': 'SPONSOR_DILEKÇESI_(KAŞE_–_İMZA)', 'id': 12}, {'text': 'SPONSOR_VERGI_LEVHASI', 'id': 13}, {'text': 'SPONSOR_ODA_KAYIT/FAALIYET_BELGESI', 'id': 14}, {'text': 'SPONSOR_İMZA_SIRKÜLERI', 'id': 15}, {'text': 'SPONSOR_TICARET_SICIL_GAZETESI', 'id': 16}, {'text': 'SPONSOR_VUKUATLI_NÜFUS_KAYIT_ÖRNEĞI_(E-DEVLET)', 'id': 17}, {'text': 'SPONSOR_YERLEŞIM_YERI_VE_DIĞER_ADRES_BELGESI_(E-DEVLET)', 'id': 18}, {'text': 'KIŞIYE_SPONSORLUĞA_DAIR_NOTER_ONAYLI_KARAR_ÖRNEĞI_VE_BU_KARARIN_KAYMAKAMLIK_TARAFINDAN_APOSTILI', 'id': 19}, {'text': 'SPONSOR_SON_3_AYLIK_BANKA_HESAP_DÖKÜMÜ', 'id': 20}, {'text': '18_YAŞINI_DOLDURMAMIŞ_BIREYLERIN_EBEVEYNLERI_NOTERDEN_ALACAĞI_MUVAFAKATNAME_ÖRNEĞI', 'id': 21}],
    }
    return t_types.get(l_type)
def template_tasks(t_type):
    template_tasks = {
        "81AONAYLI": ["Danışmanlık Sözleşmesinin imzalanması","İlk ödemenin alınması","Muhasebe taahhuku","Muhasebe taahhuku","Whatsapp grubunun kurulması ","Danışandan evrakların istenmesi","Danışana cv-oturum formlarının doldurtulması cv hazirlama formu: https://forms.gle/DMD5uUMxr4mLir2V9 oturma izni basvuru formu: https://forms.gle/czV9vx7u6yq1Aa567 ","Evrakların çeviri-noter-apostil yaptırılması","Dil kursunun başlatılması","İş Sözleşmesi ve İş İlişkisi beyanının hazırlanması","Danışandan vekalet alınması","İşverenden vekalet alınması ve imzaların tamamlanması","Evrak asıllarının Almanya’ya gönderilmesi","Ön onay başvurusunun teslimi","Konsolosluktan randevu alınması","İkinci ödemenin alınması","Vize dosyasının hazırlanması (Türkiye)","Vize onayı","Oturum işleminin tamamlanması (Almanya)"],
        "81A": ["Danışmanlık Sözleşmesinin imzalanması","İlk ödemenin alınması","Muhasebe taahhuku","Whatsapp grubunun kurulması","Danışandan evrakların istenmesi","Danışana cv-oturum formlarının doldurtulması cv hazirlama formu: https://forms.gle/DMD5uUMxr4mLir2V9 oturma izni basvuru formu: https://forms.gle/czV9vx7u6yq1Aa567 ","Evrakların çeviri-noter-apostil yaptırılması","Dil kursunun başlatılması","İş Sözleşmesi ve İş İlişkisi beyanının hazırlanması","İşçi imzasının alınması","İşveren imzalarının tamamlanması","Konsolosluktan randevu alınması","İkinci ödemenin alınması","Vize dosyasının hazırlanması (Türkiye)","Vize onayı","Oturum işleminin tamamlanması (Almanya)"],
        "AUSBILDUNG": ["Danışmanlık Sözleşmesinin imzalanması","İlk ödemenin alınması","Muhasebe taahhuku","Whatsapp grubunun kurulması","Danışandan evrakların istenmesi ","Danışana cv-oturum formlarının doldurtulması cv hazirlama formu: https://forms.gle/DMD5uUMxr4mLir2V9 oturma izni basvuru formu: https://forms.gle/czV9vx7u6yq1Aa567 ","Evrakların çeviri-noter-apostil yaptırılması","Dil kursunun başlatılması","Dil sertiffikasının tamamlanması","Referans mektubunun alınması","Evrak asıllarının Almanya’ya gönderilmesi","Denklik işlemleri için senatoya evrakların gönderilmesi","Konsolosluktan randevu alınması","İkinci ödemenin alınması","Vize dosyasının hazırlanması (Türkiye)","Vize onayı","Oturum işleminin tamamlanması (Almanya)"],
        "19C": ["Danışmanlık Sözleşmesinin imzalanması","İlk ödemenin alınması","Muhasebe taahhuku","Whatsapp grubunun kurulması","Danışandan evrakların istenmesi ","Danışana cv-oturum formlarının doldurtulması cv hazirlama formu: https://forms.gle/DMD5uUMxr4mLir2V9 oturma izni basvuru formu: https://forms.gle/czV9vx7u6yq1Aa567 ","Evrakların çeviri-noter-apostil yaptırılması","Dil kursunun başlatılması","İş Sözleşmesi ve İş İlişkisi beyanının hazırlanması","Danışandan vekalet alınması","İşverenden vekalet alınması ve imzaların tamamlanması","Evrak asıllarının Almanya’ya gönderilmesi","Ön onay başvurusunun teslimi","Konsolosluktan randevu alınması","İkinci ödemenin alınması","Vize dosyasının hazırlanması (Türkiye)","Vize onayı","Oturum işleminin tamamlanması (Almanya)"],
        "MAVIKART":["Danışmanlık Sözleşmesinin imzalanması","İlk ödemenin alınması","Muhasebe taahhuku","Whatsapp grubunun kurulması","Danışandan evrakların istenmesi ","Danışana cv-oturum formlarının doldurtulması cv hazirlama formu: https://forms.gle/DMD5uUMxr4mLir2V9 oturma izni basvuru formu: https://forms.gle/czV9vx7u6yq1Aa567 ","Evrakların çeviri-noter-apostil yaptırılması","İş Sözleşmesi ve İş İlişkisi beyanının hazırlanması","Danışandan vekalet alınması","İşverenden vekalet alınması ve imzaların tamamlanması","Evrak asıllarının Almanya'ya gönderilmesi","Ön onay başvurusunun teslimi","Konsolosluktan randevu alınması","İkinci ödemenin alınması","Vize dosyasının hazırlanması (Türkiye)","Vize onayı ","Oturum işleminin tamamlanması (Almanya) "],
        "21MADDEISVEREN":["Danışmanlık Sözleşmesinin imzalanması","İlk ödemenin alınması","Muhasebe taahhuku","Whatsapp grubunun kurulması","Danışandan evrakların istenmesi ","Danışana cv-oturum formlarının doldurtulması cv hazirlama formu: https://forms.gle/DMD5uUMxr4mLir2V9 oturma izni basvuru formu: https://forms.gle/czV9vx7u6yq1Aa567 ","Evrakların çeviri-noter-apostil yaptırılması","Danışandan vekalet alınması","Evrak asıllarının Almanya'ya gönderilmesi","Business Plan yazılması","Noterden randevu alınması","IHK Fosa-Berlin Partner'a başvuru yapılması","Ön onayın alınması","Konsolosluktan randevu alınması","İkinci ödemenin alınması","Vize dosyasının hazırlanması (Türkiye)","Vize onayı","Oturum işleminin tamamlanması (Almanya)"]
    }
    conn = get_db()
    cursor = conn.cursor()
    tasknames = [x[0] for x in cursor.execute("SELECT * FROM preTasks WHERE templateType = ? ",(t_type,)).fetchall()]

    return tasknames
class UploadFileForm(FlaskForm):
    file = FileField("file",validators=[InputRequired(),  FileAllowed(['pdf', 'doc', 'docx'], message='Only PDF files allowed.')])
    submit_button = SubmitField("Upload File")
def get_file_names_without_extensions(file_path,folder_path):
    file_names_without_extensions = []
    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)):
            splitted_file_path = file_path.split("/")
            splitted_os_path = os.path.splitext(file_name) 
            
            if file_path.split("/")[3] == os.path.splitext(file_name)[0]:

                new_file_path = file_path + splitted_os_path[1]
                os.remove(new_file_path)
            file_name_without_extension = os.path.splitext(file_name)[0]
            file_names_without_extensions.append(file_name_without_extension)
    
    return file_names_without_extensions

def get_users(conn,cursor):
    cursor.execute("SELECT * FROM Users")
    results = cursor.fetchall()     
    users = []
    for id, user_tuple in enumerate(results):
        user_dict = []
        for item in user_tuple:
            if isinstance(item, bytes):
                item = item.decode('utf-8')
            user_dict.append(item)
        users.append(user_dict)
    return users
def check_files(tckn,template_id,name):
    conn=get_db()
    cursor=conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    templates= json.loads(templates[0])

    for template in templates:

        if template.get("template_id") == int(template_id):
            files = template["files"]

            return  [ True for link in files  if name in link ]

def convert_name(text,tckn):
    return unidecode(text.upper()).replace("-","").replace(" ","_").replace("(","").replace(")","").replace(",","").replace("/","_") + tckn[-4:]

def get_templates(session,tckn):
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT templates FROM Users WHERE tckn = ?", (tckn,))
    templates = cursor.fetchone()
    templates = json.loads(templates[0])

    return templates
def update_templates(session,tckn,templates):
    allowed_roles = ["SuperAdmin","Admin"]
    if not "email" in session or not session.get("Role") in allowed_roles:
        return jsonify({"Error":"Permission Denied"})
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET templates = ? WHERE tckn = ?", (json.dumps(templates), tckn))
    conn.commit()
    conn.close()
    return True