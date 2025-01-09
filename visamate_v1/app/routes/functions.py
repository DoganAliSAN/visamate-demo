from flask import Flask,request, redirect, url_for, render_template, g, jsonify
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import InputRequired
from wtforms import SubmitField,HiddenField
from werkzeug.utils import secure_filename
import bcrypt 
import sqlite3
import time
import os
import json
def get_app():
    app = Flask(__name__,template_folder='../templates',static_folder='../static')
    app.secret_key = "!g2q_q*p#!6j)nmdnb170&)y4i54!l2)ji&w7u%e16i5n^2)" 

    app.config['DATABASE'] = '../main.db'
    app.config['UPLOAD_FOLDER'] = 'static/files'
    return app
def get_db():
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
    }
    return t_types.get(l_type)
def t_types_backend(l_type):
    t_types = {
        "81A":[{'text': 'BAŞVURU_FORMU', 'id': 0}, {'text': 'DIPLOMA_(YEMINLI_TERCÜMELI)', 'id': 1}, {'text': 'TRANSKRIPT_(YEMINLI_TERCÜMELI)', 'id': 2}, {'text': 'ÖZGEÇMIŞ(CV)_(ALMANCA)', 'id': 3}, {'text': 'PASAPORT_VE_KIMLIK_FOTOKOPISI', 'id': 4}, {'text': 'SSK_HIZMET_DÖKÜMÜ_(ISLAK_IMZALIAPOSTILLI)', 'id': 5}, {'text': 'ÇALIŞMA_BELGESI', 'id': 6}, {'text': 'REFERANS_YAZISI', 'id': 7}, {'text': 'IŞ_BAŞVURUSU_VEYA_IŞ_SÖZLEŞMESI_ÇIKTISI', 'id': 8}, {'text': 'STAJ_BELGESI_(LISE_MEZUNLARI_IÇIN)_(OPSIYONEL)', 'id': 9}, {'text': 'ÇERÇEVE_EĞITIM_PROGRAMI_(KALFALIK_MEZUNLARI_IÇIN_)_(OPSIYONEL)', 'id': 10}],
        "AUSBILDUNG":[{'text': 'ÖZGEÇMIŞ_DETAYLI', 'id': 0}, {'text': 'KIMLIK_BELGESI_(KIMLIK_KARTI_FOTOKOPISI_VE_PASAPORT_FOTOKOPISI_ILE_KAYIT_BELGESI_FOTOKOPISI)', 'id': 1}, {'text': 'ORIJINAL_DIPLOMANIN/DERECENIN_VE_EYALET_TANINIRLIĞININ_KOPYASI(APOSTIL)', 'id': 2}, {'text': 'KONUNUN_VE_NOT_ÖZETININ_KOPYASI_(ÖRN._DIPLOMA_EKI_ÇALIŞMA_KITABI_KAYITLARIN_TRANSKRIPTI)_VE_APOSTILI', 'id': 3}, {'text': 'İLGILI_MESLEKI_DENEYIM_VE_DIĞER_NITELIKLERIN_KANITI_(STAJ_BELGELERI_VE_SGK_DÖKÜMÜ_VE_APOSTILI)', 'id': 4}, {'text': 'DIL_SERTIFIKASI', 'id': 5}],
        "MAVIKART":[{'text': 'PASAPORT_VE_KIMLIK_FOTOKOPISI_VE_1_ADET_BIYOMETRIK_FOTOĞRAF', 'id': 0}, {'text': 'ÜNIVERSITE_DIPLOMASI_TRANSKRIPT_VE_ANABIN_(VEYA_ZAB)_ONAYI', 'id': 1}, {'text': 'İŞ_SÖZLEŞMESI_VEYA_SOMUT_IŞ_TEKLIFI_(ISLAK_IMZALI-KAŞELI)', 'id': 2}, {'text': 'İŞ_POZISYON_TANIMI_FORMU_(IŞVEREN_TARAFINDAN_DOLDURULACAK)', 'id': 3}, {'text': 'SSK_HIZMET_DÖKÜMÜ_(ISLAK_IMZALIAPOSTILLI)', 'id': 4}, {'text': 'ÇALIŞMA_BELGESI(ANTETLI_KAĞIDA)', 'id': 5}, {'text': 'REFERANS_YAZISI_(ISLAK_IMZALI__FIRMA_ISE_KAŞELI_REFERANS_OLANIN_ILETIŞIM_BILGILERI)', 'id': 6}, {'text': 'ÖZGEÇMIŞ(CV)_(ALMANCA)', 'id': 7}, {'text': 'EVLILIK_CÜZDANI(ILK_4_SAYFASI)', 'id': 8}, {'text': 'EŞ-ÇOCUK_IÇIN_PASAPORT_VE_KIMLIK_BILGILERI', 'id': 9}, {'text': 'ÇOCUKLAR_IÇIN_ÖĞRENCI_BELGESI', 'id': 10}, {'text': 'SAHIP_OLUNAN_SERTIFIKALAR_BELGELER_VE_KATILIMCILIĞI_KANITLANABILIR_PROGRAMLAR', 'id': 11}, {'text': 'MESLEK_IZNI_–_(SADECE_MÜHENDISLIK_DOKTORLUK_GIBI_ONAY_GEREKTIREN_MESLEKLER_IÇIN)', 'id': 12}, {'text': 'SAĞLIK_SIGORTASI_TEYIDI', 'id': 13}, {'text': 'STAJ_BELGESI_(LISE_MEZUNLARI_IÇIN)_(OPSIYONEL)', 'id': 14}, {'text': 'ÇERÇEVE_EĞITIM_PROGRAMI_(KALFALIK_MEZUNLARI_IÇIN_)_(OPSIYONEL)', 'id': 15}],
        "SCHENGEN":[{'text': 'PASAPORT__PASAPORT_ILK_SAYFA_FOTOKOPISI_VE_KIMLIK_FOTOKOPISI_VE_2_ADET_BIOMETRIK_FOTOĞRAF', 'id': 0}, {'text': 'PASAPORT_PROTOKOL_EVRAĞI_(E-DEVLET)', 'id': 1}, {'text': 'YERLEŞIM_YERI_VE_DIĞER_ADRES_BELGESI_(E-DEVLET)', 'id': 2}, {'text': 'VUKUATLI_NÜFUS_KAYIT_ÖRNEĞI_BELGESI_(E-DEVLET)', 'id': 3}, {'text': 'NIYET_MEKTUBU_YAZILMASI_İÇIN_KISACA_ÖZGEÇMIŞ', 'id': 4}, {'text': 'ÖĞRENCI_BELGESI_(ÇOCUKLARINIZ_İÇIN)', 'id': 5}, {'text': 'İZIN_YAZISI_(ANTETLI_KAĞIDA)', 'id': 6}, {'text': 'SGK_DÖKÜMÜ_VE_İŞE_GIRIŞ_BELGESI_(E-DEVLET)', 'id': 7}, {'text': 'SON_3_AYLIK_ISLAK_İMZALI_MAAŞ_BORDROSU', 'id': 8}, {'text': 'SON_3_AYLIK_BANKA_EKSTRESI', 'id': 9}, {'text': 'ARAÇ_RUHSATI_VE_TAPU_FOTOKOPISI_(VARSA)', 'id': 10}, {'text': 'ÇALIŞMA_BELGESI_(ANTETLI_KAĞIDA)', 'id': 11}, {'text': 'SPONSOR_DILEKÇESI_(KAŞE_–_İMZA)', 'id': 12}, {'text': 'SPONSOR_VERGI_LEVHASI', 'id': 13}, {'text': 'SPONSOR_ODA_KAYIT/FAALIYET_BELGESI', 'id': 14}, {'text': 'SPONSOR_İMZA_SIRKÜLERI', 'id': 15}, {'text': 'SPONSOR_TICARET_SICIL_GAZETESI', 'id': 16}, {'text': 'SPONSOR_VUKUATLI_NÜFUS_KAYIT_ÖRNEĞI_(E-DEVLET)', 'id': 17}, {'text': 'SPONSOR_YERLEŞIM_YERI_VE_DIĞER_ADRES_BELGESI_(E-DEVLET)', 'id': 18}, {'text': 'KIŞIYE_SPONSORLUĞA_DAIR_NOTER_ONAYLI_KARAR_ÖRNEĞI_VE_BU_KARARIN_KAYMAKAMLIK_TARAFINDAN_APOSTILI', 'id': 19}, {'text': 'SPONSOR_SON_3_AYLIK_BANKA_HESAP_DÖKÜMÜ', 'id': 20}, {'text': '18_YAŞINI_DOLDURMAMIŞ_BIREYLERIN_EBEVEYNLERI_NOTERDEN_ALACAĞI_MUVAFAKATNAME_ÖRNEĞI', 'id': 21}],
    }
    return t_types.get(l_type)
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired(),  FileAllowed(['pdf', 'doc', 'docx'], message='Only PDF, DOC, and DOCX files allowed.')])
    submit = SubmitField("Upload File")
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

