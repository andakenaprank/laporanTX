import json
import os
from datetime import date

def buat_laporan_json(forward_power, reflected_power, active_exciter='UNKNOWN', power_data = None, output_dir='uploads'):
    tegangan_data = power_data or {}
    laporan = {
        "tanggal": str(date.today()),
        "lokasi": "SATUAN TRANSMISI TVRI BANJARMASIN",
        "pemancar": {
            "merk": "ROHDE & SCWHARZ",
            "power_normal": "3.5 kW",
            "power_real": f"{forward_power} kW",
            "reflect": f"{reflected_power} W",
            "status": "Normal"
        },
        "status": {
            "mux_A_B": "Ok",
            "ex_A": "Ok (In Use)" if active_exciter == 'A' else "Ok",
            "ex_B": "Ok (In Use)" if active_exciter == 'B' else "Ok",

            "layanan_terganggu": "-"
        },
        "kelistrikan": {
            "UPS": "Normal (Kondisi Baik)",
            "Genset": "Normal (Kondisi 100%)",
            "Tegangan_Listrik": "Normal",
            "tegangan": {
                "RS": tegangan_data.get("RS"),
                "RN": tegangan_data.get("RN"),
                "ST": tegangan_data.get("ST"),
                "SN": tegangan_data.get("SN"),
                "TR": tegangan_data.get("TR"),
                "TN": tegangan_data.get("TN"),
                "freq": tegangan_data.get("freq")
            },
            "arus" : tegangan_data.get("arus",{})
        }, 
        "mitra": {
            "RTV": "ON AIR",
            "NETTV": "ON AIR",
            "PRIMATV": "ON AIR",
            "BTV": "ON AIR",
            "SINPOTV": "ON AIR"
        }
    }

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'laporan_terkirim.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(laporan, f, ensure_ascii=False, indent=2)

    return path
