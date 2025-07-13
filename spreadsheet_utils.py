import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Muat file .env sekali di awal program Anda (misal di app.py)
load_dotenv()

def connect_to_sheet(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Ambil path credential dan ID spreadsheet dari env
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    spreadsheet_id = os.getenv("SPREADSHEET_ID")

    # Autentikasi pakai credential file
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    # Buka sheet
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    return sheet
# ========================
# Setup koneksi ke Google Sheets
# ========================
load_dotenv()
def connect_to_sheet(sheet_name, spreadsheet_id="1GEMp_JlUJPYvdlUQiezqqqHu49FJ4wWAoJB15-3xVBA"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("secrets/ocrcam-463906-1aca4783a1e9.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    return sheet

# ========================
# Kirim masing-masing baris ke Sheet berbeda
# ========================
def kirim_manual_ke_spreadsheet(data_dict):
    sukses = False  # Flag status global

    # === TRANSMISI ===
    try:
        sheet_transmisi = connect_to_sheet("Transmisi")
        row_transmisi = [
            data_dict.get("id", ""),
            data_dict.get("tanggal"),
            data_dict.get("waktu", ""),
            data_dict.get("petugas", ""),
            data_dict["pemancar"].get("merk"),
            data_dict["pemancar"].get("power_real"),
            data_dict["pemancar"].get("reflect"),
            data_dict["pemancar"].get("downtime"),
            data_dict.get("status", {}).get("ex_A", "-"),
            data_dict.get("status", {}).get("ex_B", "-"),
            data_dict["pemancar"].get("foto_bukti"),
        ]
        sheet_transmisi.append_row(row_transmisi)
        print("✅ Sheet Transmisi OK")
        sukses = True
    except Exception as e:
        print(f"❌ Gagal Transmisi: {e}")

    # === UPS ===
    try:
        ups = data_dict["kelistrikan"]["UPS"]
        sheet_ups = connect_to_sheet("UPS")
        row_ups = [
            data_dict.get("id", ""),
            data_dict.get("tanggal"),
            data_dict.get("waktu", ""),
            ups.get("RS"),
            ups.get("RN"),
            ups.get("ST"),
            ups.get("SN"),
            ups.get("TR"),
            ups.get("TN"),
            ups.get("freq"),
            ups.get("link_foto"),
        ]
        sheet_ups.append_row(row_ups)
        print("✅ Sheet UPS OK")
        sukses = True
    except Exception as e:
        print(f"❌ Gagal UPS: {e}")

    # === Genset ===
    try:
        genset = data_dict["kelistrikan"]["Genset"]
        sheet_genset = connect_to_sheet("Genset")
        row_genset = [
            data_dict.get("id", ""),
            data_dict.get("tanggal"),
            data_dict.get("waktu", ""),
            genset.get("RS"),
            genset.get("RN"),
            genset.get("ST"),
            genset.get("SN"),
            genset.get("TR"),
            genset.get("TN"),
            genset.get("freq"),
            genset.get("link_foto"),
        ]
        sheet_genset.append_row(row_genset)
        print("✅ Sheet Genset OK")
        sukses = True
    except Exception as e:
        print(f"❌ Gagal Genset: {e}")

    return sukses  # 🚩 PENTING!

import json
import os

def save_json(data):
    # Buat folder 'output' kalau belum ada
    os.makedirs("output", exist_ok=True)

    filename = f"laporan_{data['id']}.json"

    with open(f"output/{filename}", "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ JSON berhasil disimpan ke output/{filename}")
