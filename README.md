🔐 Hidden Safety Vault
Hidden Safety Vault is a simple yet powerful file protection system built with Python and PySide6. It allows users to securely hide sensitive files inside a USB or local drive using a hidden vault folder and per-drive password protection — all without using complex encryption.

 Features
 Creates a hidden .vault folder in any selected drive

 Allows you to set a unique password per drive

 Move files into the vault (not just copy)

Restore files to their original location

 Remove files securely

 Delete vault from individual drives without affecting others

 Tracks original file paths using hidden metadata

 How It Works
User selects a drive from the GUI.

App auto-creates a hidden .vault folder inside the drive.

Prompts the user to set a password for that specific vault.

Files added to the vault are hidden from normal users.

Files can only be accessed via the app and correct password.

Restore or delete files anytime securely through the GUI.

Tech Stack

Tech	Purpose
Python	Core logic and backend
PySide6	GUI interface
psutil	Detecting USB/Drive paths
os, shutil	File handling and movement
JSON	Password & metadata storage
 Future Enhancements
Face recognition unlock 

Drag-and-drop support 

Optional encryption mode 

Build standalone .exe app for Windows 

 Why Use This?
If you’re looking for a quick, lightweight, and reliable way to hide personal or sensitive files inside any drive, Hidden Safety Vault is the perfect tool. No complex setup, no slow encryption — just fast, secure, and private file handling!

