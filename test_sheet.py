from spreadsheet_utils import connect_to_sheet

sheet = connect_to_sheet('Transmisi')
print("Berhasil konek! Jumlah baris:", len(sheet.get_all_values()))
