from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas as pd
from fastapi import FastAPI

# 🔹 Cesta k JSON klíči pro autentizaci
SERVICE_ACCOUNT_FILE = "C:/Users/SkSTP/credentials.json"

# 🔹 Oprávnění pro Google Drive API
SCOPES = ["https://www.googleapis.com/auth/drive"]

# 🔹 Autentizace k API
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# 🔹 Vytvoření klienta Google Drive API
drive_service = build("drive", "v3", credentials=credentials)

# 🔹 ID složky na Google Drive (získané z URL)
FOLDER_ID = "1UyApTKtmY2OvscPLcxdH-uwEy8l8rlfI"

# 🔹 Název souboru, který chceme stáhnout
FILE_NAME = "data.xlsx"

# 🔹 Funkce pro získání ID souboru podle názvu
def get_latest_file_id(folder_id, filename):
    query = f"'{folder_id}' in parents and name='{filename}' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        print(f"❌ Soubor '{filename}' nebyl nalezen ve složce.")
        return None
    return files[0]["id"]

# 🔹 Funkce pro stažení souboru
def download_file(file_id, filename):
    request = drive_service.files().get_media(fileId=file_id)
    with open(filename, "wb") as file:
        file.write(request.execute())
    print(f"✅ Soubor '{filename}' byl stažen!")

# 🔹 Spustíme stažení aktuálního `data.xlsx`
file_id = get_latest_file_id(FOLDER_ID, FILE_NAME)
if file_id:
    download_file(file_id, "C:/Users/SkSTP/data.xlsx")

# 🔹 Načtení souboru do Pandas (bez chyb)
try:
    df = pd.read_excel("C:/Users/SkSTP/data.xlsx")
    print("📊 Prvních 5 řádků souboru:")
    print(df.head())
except Exception as e:
    print("❌ Chyba při načítání Excel souboru:", e)

# 🔹 FastAPI server pro přístup k datům
app = FastAPI()

@app.get("/data")
def get_data():
    try:
        df = pd.read_excel("C:/Users/SkSTP/data.xlsx")
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"Chyba při načítání Excel souboru: {e}"}

# 🔹 Jak spustit API: uvicorn list_files:app --reload
