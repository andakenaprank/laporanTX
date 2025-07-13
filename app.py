from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import cv2
import json
from datetime import date, datetime
from pdf_utils import generate_pdf
import pymysql
from ocr_utils import detect_green_boxes_and_ocr
from laporan_utils import buat_laporan_json
from exciter_detector import detect_active_exciter
from power_detector import extract_power_info
from spreadsheet_utils import kirim_manual_ke_spreadsheet
from dotenv import load_dotenv
import hashlib
import uuid
from manual_utils import upload_to_drive_oauth
from spreadsheet_utils import save_json
load_dotenv()
FOLDER_TRANSMISI = "1P04NUThkyrXWz79y7BCNOxSUv05rJ9Pj"
FOLDER_UPS = "1YPggeP-kQGAeAfzgr-8v61jf9wnUCU10"
FOLDER_GENSET = "1_O-Fh5doVE1lWHobrG7DOugb6YUSs6Kx"

def generate_secure_id():
    # Kombinasi waktu + uuid acak
    raw = f"{datetime.now().timestamp()}-{uuid.uuid4()}"
    salt = "tvri-ocr-2024"  # Salt bisa disesuaikan
    return hashlib.sha256((raw + salt).encode()).hexdigest()[:12].upper()




connection = pymysql.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    db=os.getenv('DB_NAME')
)


app = Flask(__name__, static_url_path='/output', static_folder='output')
app.secret_key = 'rahasia-super-aman'
app.config["UPLOAD_FOLDER"] = "static"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ========================
# Helper: Database User
# ========================
# def get_user_by_username(username):
#     with connection.cursor() as cursor:
#         sql = "SELECT * FROM users WHERE username = %s"
#         cursor.execute(sql, (username,))
#         return cursor.fetchone()
# ========================
# ROUTE: Register
# ========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_pw = generate_password_hash(password)

        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(sql, (username, hashed_pw))
            connection.commit()

        return redirect('/login')
    return render_template('register.html')
# ========================
# ROUTE: Login
# ========================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            # Simpan info login ke session
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/')

        else:
            error = "Login gagal. Username atau password salah."
    
    return render_template("login.html", error=error)



# ========================
# ROUTE: Logout
# ========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ========================
# ROUTE: Home
# ========================
@app.route('/')
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    now = datetime.now().hour
    if now < 11:
        greet = "Selamat pagi"
    elif now < 15:
        greet = "Selamat siang"
    elif now < 18:
        greet = "Selamat sore"
    else:
        greet = "Selamat malam"

    return render_template("home.html", greeting=greet, username=session.get("username"))


# ========================
# ROUTE: Scanner Page
# ========================
@app.route('/scanner')
def scanner():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", mode="scanner")

# ========================
# ROUTE: Upload Gambar (Kamera / Upload)
# ========================
@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    forward, reflected, _ = detect_green_boxes_and_ocr(filepath)
    active_exciter = detect_active_exciter(filepath)
    power_data = extract_power_info(filepath)
    laporan = buat_laporan_json(forward, reflected, active_exciter, power_data)

    tanggal_str = date.today().strftime("%Y-%m-%d")
    laporan_filename = f"laporan_{tanggal_str}.json"
    laporan_path = os.path.join(app.config["UPLOAD_FOLDER"], laporan_filename)
    with open(laporan_path, "w", encoding="utf-8") as f:
        json.dump(laporan, f, ensure_ascii=False, indent=2)

    return jsonify({
        "forward_power": forward or "(Tidak Terdeteksi)",
        "reflected_power": reflected or "(Tidak Terdeteksi)",
        "laporan_url": f"/static/{laporan_filename}"
    })

# GET ➜ tampilkan form manual
@app.route("/manual", methods=["GET", "POST"])
def manual_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            # === 1) Ambil form data
            data = request.form.to_dict()
            bukti_transmisi = request.files['bukti_transmisi']
            bukti_ups = request.files['bukti_ups']
            bukti_genset = request.files['bukti_genset']

            # === 2) Upload ke Drive
            link_transmisi = upload_to_drive_oauth(bukti_transmisi, FOLDER_TRANSMISI)
            link_ups = upload_to_drive_oauth(bukti_ups, FOLDER_UPS)
            link_genset = upload_to_drive_oauth(bukti_genset, FOLDER_GENSET)

            # === 3) Bangun dict laporan
            laporan = {
                "id": generate_secure_id(),
                "tanggal": str(date.today()),
                "waktu": datetime.now().strftime("%H:%M:%S"),
                "petugas": session.get("username"),
                "lokasi": "SATUAN TRANSMISI TVRI",
                "pemancar": {
                    "merk": data.get("merk"),
                    "power_normal": "3.5 kW",
                    "power_real": f"{data.get('power_real')} kW",
                    "reflect": f"{data.get('reflect')} W",
                    "downtime": f"{data.get('downtime')} menit",
                    "status": "Normal",
                    "foto_bukti": link_transmisi
                },
                "status": {
                    "mux_A_B": "Ok",
                    "ex_A": "Ok (In Use)" if data.get("exciter") == "A" else "Ok",
                    "ex_B": "Ok (In Use)" if data.get("exciter") == "B" else "Ok",
                    "layanan_terganggu": "-"
                },
                "kelistrikan": {
                    "UPS": {
                        "RS": int(data.get("RS_UPS")),
                        "RN": int(data.get("RN_UPS")),
                        "ST": int(data.get("ST_UPS")),
                        "SN": int(data.get("SN_UPS")),
                        "TR": int(data.get("TR_UPS")),
                        "TN": int(data.get("TN_UPS")),
                        "freq": data.get("freq_UPS") + " Hz",
                        "link_foto": link_ups
                    },
                    "Genset": {
                        "RS": int(data.get("RS_Genset")),
                        "RN": int(data.get("RN_Genset")),
                        "ST": int(data.get("ST_Genset")),
                        "SN": int(data.get("SN_Genset")),
                        "TR": int(data.get("TR_Genset")),
                        "TN": int(data.get("TN_Genset")),
                        "freq": data.get("freq_Genset") + " Hz",
                        "link_foto": link_genset
                    }
                }
            }

            # === 4) Kirim ke Spreadsheet
            result = kirim_manual_ke_spreadsheet(laporan)
            print("✅ Kirim spreadsheet:", result)

            # === 5) Simpan JSON
            save_json(laporan)

            # === 6) Buat PDF
            pdf_filename = f"output/laporan_{laporan['id']}.pdf"
            generate_pdf(laporan, pdf_filename)

            # === 7) Response JSON untuk JS Fetch
            return jsonify({
                "status": "success",
                "id": laporan["id"],
                "petugas": laporan["petugas"],
                "laporan_url": f"/output/laporan_{laporan['id']}.json",
                "pdf_url": f"/output/laporan_{laporan['id']}.pdf"
            })

        except Exception as e:
            print("❌ Fatal error:", e)
            return jsonify({"status": "error", "message": str(e)}), 500

    return render_template("index.html", mode="manual")

# # POST ➜ proses data manual
# # @app.route("/manual", methods=["POST"])
# # def manual_input():
# #     if "user_id" not in session:
# #         return jsonify({"error": "Unauthorized"}), 401
# #     # proses simpan data

# #     data = request.form.to_dict()
# #     bukti_transmisi = request.files['bukti_transmisi']
# #     bukti_ups = request.files['bukti_ups']
# #     bukti_genset = request.files['bukti_genset']

# #     link_transmisi = upload_to_drive_oauth(bukti_transmisi, FOLDER_TRANSMISI)
# #     link_ups = upload_to_drive_oauth(bukti_ups, FOLDER_UPS)
# #     link_genset = upload_to_drive_oauth(bukti_genset, FOLDER_GENSET)

# #     laporan = {
# #         "id": generate_secure_id(),
# #         "tanggal": str(date.today()),
# #         "waktu": datetime.now().strftime("%H:%M:%S"),
# #         "petugas": session.get("username"),
# #         "lokasi": "SATUAN TRANSMISI TVRI",
# #         "pemancar": {
# #             "merk": data.get("merk"),
# #             "power_normal": "3.5 kW",
# #             "power_real": f"{data.get('power_real')} kW",
# #             "reflect": f"{data.get('reflect')} W",
# #             "downtime": f"{data.get('downtime')} menit",
# #             "status": "Normal",
# #              "foto_bukti": link_transmisi
# #         },
# #         "status": {
# #             "mux_A_B": "Ok",
# #             "ex_A": "Ok (In Use)" if data.get("exciter") == "A" else "Ok",
# #             "ex_B": "Ok (In Use)" if data.get("exciter") == "B" else "Ok",
# #             "layanan_terganggu": "-"
# #         },
# #         "kelistrikan": {
# #             "UPS": {
# #                 "RS": int(data.get("RS_UPS")),
# #                 "RN": int(data.get("RN_UPS")),
# #                 "ST": int(data.get("ST_UPS")),
# #                 "SN": int(data.get("SN_UPS")),
# #                 "TR": int(data.get("TR_UPS")),
# #                 "TN": int(data.get("TN_UPS")),
# #                 "freq": data.get("freq_UPS") + " Hz",
# #                 "link_foto": link_ups 
# #             },
# #             "Genset": {
# #                 "RS": int(data.get("RS_Genset")),
# #                 "RN": int(data.get("RN_Genset")),
# #                 "ST": int(data.get("ST_Genset")),
# #                 "SN": int(data.get("SN_Genset")),
# #                 "TR": int(data.get("TR_Genset")),
# #                 "TN": int(data.get("TN_Genset")),
# #                 "freq": data.get("freq_Genset") + " Hz",
# #                 "link_foto": link_genset
# #             }
# #         }
# #     }
       
    
# #     # Kirim ke Google Spreadsheet
# #     try:
# #         kirim_manual_ke_spreadsheet(laporan)
# #         print("✅ Kirim spreadsheet sukses")
# #     except Exception as e:
# #         print("❌ Kirim spreadsheet GAGAL:", e)


#     # Simpan JSON
#     filename = f"laporan_{laporan['id']}.json"
#     output_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#     with open(output_path, "w", encoding="utf-8") as f:
#         json.dump(laporan, f, ensure_ascii=False, indent=2)

#     # Generate PDF
#     pdf_filename = f"laporan_{laporan['id']}.pdf"
#     pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_filename)
#     generate_pdf(laporan, pdf_path)

#     return jsonify({
#         **laporan,
#         "laporan_url": f"/static/{filename}",
#         "pdf_url": f"/static/{pdf_filename}"
#     })
# # ========================

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)