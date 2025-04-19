import os
import json
from utils.encryptor import encrypt_file, decrypt_file, load_key

VAULT_FOLDER = "vault_data/.vault"
DATA_FOLDER = "vault_data"

def load_password():
    try:
        with open("password_store.json", "r") as f:
            return json.load(f)["password"]
    except:
        return None

def view_files():
    print("📁 Normal Files:")
    for file in os.listdir(DATA_FOLDER):
        if file != ".vault":
            print(f"- {os.path.join(DATA_FOLDER, file)}")

    print("\n🔐 Locked Files (Only visible via vault):")
    for file in os.listdir(VAULT_FOLDER):
        print(f"- {os.path.join(VAULT_FOLDER, file)}")

def encrypt():
    file_name = input("Enter the path of file to encrypt (inside vault_data/): ")
    file_path = os.path.join(DATA_FOLDER, file_name)
    if not os.path.exists(file_path):
        print("❌ File does not exist.")
        return

    key = load_key()
    out_path = os.path.join(VAULT_FOLDER, os.path.basename(file_path) + ".bin")
    encrypt_file(file_path, out_path, key)
    print(f"✅ File encrypted and stored in: {out_path}")

def decrypt():
    files = os.listdir(VAULT_FOLDER)
    if not files:
        print("No locked files.")
        return

    print("Select a locked file to decrypt:")
    for i, file in enumerate(files):
        print(f"[{i+1}] {file}")

    choice = int(input("Enter your choice: ")) - 1
    file_to_decrypt = os.path.join(VAULT_FOLDER, files[choice])
    password = input("🔑 Enter vault password: ")

    if password != load_password():
        print("❌ Failed to decrypt. Wrong key or corrupted file.")
        return

    key = load_key()
    output_file = os.path.join(VAULT_FOLDER, files[choice].replace(".bin", "_decrypted.txt"))
    decrypt_file(file_to_decrypt, output_file, key)
    print(f"✅ Decrypted to: {output_file}")

def main():
    while True:
        print("""
🔐 USB Vault - Menu
1. View Files
2. Encrypt File
3. Decrypt File (Password Protected)
0. Exit
""")
        option = input("Select an option: ")

        if option == "1":
            view_files()
        elif option == "2":
            encrypt()
        elif option == "3":
            decrypt()
        elif option == "0":
            print("👋 Exiting...")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
