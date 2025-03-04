import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import pandas as pd
from fastapi import FastAPI

# ✅ Ověření, jaké přihlašovací údaje jsou k dispozici
credentials = None

# 🔹 🏆 METODA 1: Použití `GOOGLE_CREDENTIALS` z Environment Variables (Render.com)
if os.getenv("GOOGLE_CREDENTIALS"):
    try:
        credentials_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
        credentials = service_account.Credentials.from_service_account_info(credentials_json)
        print("✅ Používám GOOGLE_CREDENTIALS z Environment Variables.")
    except json.JSONDecodeError as e:
        print(f"❌ Chyba při načítání GOOGLE_CREDENTIALS: {e}")

# 🔹 🏆 METODA 2: Použití `credentials.json` (GitHub)
elif os.path.exists("credentials.json"):
    try:
        credentials = service_account.Credentials.from_service_account_file("credentials.json")
        print("✅ Používám `credentials.json` ze souboru.")
    except Exception as e:
        print(f"❌ Chyba při načítání credentials.json: {e}")

# 🔹 Pokud žádná metoda nefunguje → chyba
if credentials is None:
    raise FileNotFoundError("❌ CHYBA: Nebyly nalezeny žádné přihlašovací údaje!")

# ✅ Vytvoření klienta Google Drive API
drive_service = build("drive", "v3", credentials=credentials)

# ✅ ID složky na Google Drive (získané z URL)
FOLDER_ID = "1UyApTKtmY2OvscPLcxdH-uwEy8l8rlfI"

# ✅ Název souboru, který chceme stáhnout
FILE_NAME = "data.xlsx"

# 🔹 Funkce pro získání ID souboru podle názvu
def get_latest_file_id(folder_id, filename):
    try:
        query = f"'{folder_id}' in parents and name='{filename}' and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get("files", [])

        if not files:
            print(f"❌ Soubor '{filename}' nebyl nalezen ve složce.")
            return None
        return files[0]["id"]
    except Exception as e:
        print(f"❌ Chyba při získávání ID souboru: {e}")
        return None

# 🔹 Funkce pro stažení souboru
def download_file(file_id, filename):
    try:
        request = drive_service.files().get_media(fileId=file_id)
        with open(filename, "wb") as file:
            file.write(request.execute())
        print(f"✅ Soubor '{filename}' byl stažen!")
    except Exception as e:
        print(f"❌ Chyba při stahování souboru '{filename}': {e}")

# ✅ Spustíme stažení aktuálního `data.xlsx`
file_id = get_latest_file_id(FOLDER_ID, FILE_NAME)
if file_id:
    download_file(file_id, "data.xlsx")

# 🔹 Načtení souboru do Pandas (bez chyb)
try:
    df = pd.read_excel("data.xlsx")
    print("📊 Prvních 5 řádků souboru:")
    print(df.head())
except Exception as e:
    print(f"❌ Chyba při načítání Excel souboru: {e}")

# 🔹 FastAPI server pro přístup k datům
app = FastAPI()

@app.get("/data")
def get_data():
    try:
        df = pd.read_excel("data.xlsx")
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"Chyba při načítání Excel souboru: {e}"}

# 🔹 Jak spustit API na serveru: uvicorn list_files:app --host 0.0.0.0 --port 10000
