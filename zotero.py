import sqlite3
import os
from pathlib import Path
import shutil

# === CONFIGURATION ===
ZOTERO_DIR = Path.home() / "Zotero"
DB_PATH = ZOTERO_DIR / "zotero.sqlite"
STORAGE_DIR = ZOTERO_DIR / "storage"
COLLECTION_NAME = "CAR Design/Properties"
OUTPUT_DIR = Path.cwd() / "zotero_pdfs"

# === Create output folder ===
OUTPUT_DIR.mkdir(exist_ok=True)

# === Connect to the Zotero database ===
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# === Step 1: Get collection key ===
cursor.execute("""
    SELECT collectionID FROM collections WHERE collectionName = ?
""", (COLLECTION_NAME,))
row = cursor.fetchone()

if not row:
    print(f"❌ Collection '{COLLECTION_NAME}' not found.")
    exit(1)

collection_id = row[0]
# print(row)

# === Step 2: Get itemIDs in the collection ===
cursor.execute("""
    SELECT ci.itemID
    FROM collectionItems ci
    JOIN items i ON ci.itemID = i.itemID
    WHERE ci.collectionID = ? AND i.itemTypeID = 22
""", (collection_id,))
item_ids = [row[0] for row in cursor.fetchall()]
# print(item_ids)


# === Step 3: Find attached PDFs ===
for item_id in item_ids:
    cursor.execute("""
        SELECT ia.itemID, i.key
        FROM itemAttachments ia
        JOIN items i ON ia.itemID = i.itemID
        WHERE ia.parentItemID = ? AND i.itemTypeID = 3  
    """, (item_id,))
    attachments = cursor.fetchall()
    print(attachments)
    
    for attachment_id, attachment_key in attachments:
        attachment_folder = STORAGE_DIR / attachment_key
        if not attachment_folder.exists():
            print(f"❌ Attachment folder not found: {attachment_folder}")
            continue

        for file in attachment_folder.iterdir():
            if file.suffix.lower() == ".pdf":
                output_path = OUTPUT_DIR / file.name
                shutil.copy(file, output_path)
                print(f"✅ Copied: {file.name}")
            else:
                print(f"⚠️ Skipped non-PDF file: {file.name}")

# === Close database ===
conn.close()