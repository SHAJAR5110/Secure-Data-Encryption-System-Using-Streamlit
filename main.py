import streamlit as st
import hashlib
from cryptography.fernet import Fernet

# ✅ Set page config at the very top
st.set_page_config(page_title="Secure Vault", layout="centered")

# 🔐 Secure key generation and reuse
@st.cache_data
def get_cipher():
    key = Fernet.generate_key()
    return Fernet(key)

cipher = get_cipher()

# 💾 Initialize session state variables
if "storage" not in st.session_state:
    st.session_state.storage = {}

if "failed" not in st.session_state:
    st.session_state.failed = 0

# 🔑 Utility Functions
def hash_passkey(passkey):
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt(text, passkey):
    return cipher.encrypt(text.encode()).decode()

def decrypt(encrypted_text, passkey):
    hashed = hash_passkey(passkey)
    for etxt, meta in st.session_state.storage.items():
        if meta["passkey"] == hashed and etxt == encrypted_text:
            st.session_state.failed = 0
            return cipher.decrypt(encrypted_text.encode()).decode()
    st.session_state.failed += 1
    return None

# 🎯 App UI
st.title("🔐 Secure Data Vault")

menu = st.sidebar.radio("Menu", ["🏠 Home", "📝 Store", "🔍 Retrieve", "🔑 Admin Login"])

if menu == "🏠 Home":
    st.write("This tool helps you **encrypt and safely retrieve** your sensitive information.")
    st.info("Choose an option from the sidebar to get started.")

elif menu == "📝 Store":
    st.subheader("Store Secret Information")
    user_text = st.text_area("Data to Secure")
    passkey = st.text_input("Create a Passkey", type="password")

    if st.button("🔒 Encrypt & Store"):
        if user_text and passkey:
            hashed_key = hash_passkey(passkey)
            encrypted = encrypt(user_text, passkey)
            st.session_state.storage[encrypted] = {"passkey": hashed_key}
            st.success("✅ Encrypted & stored successfully!")
            st.code(encrypted, language="text")
        else:
            st.warning("Both fields are required.")

elif menu == "🔍 Retrieve":
    st.subheader("Retrieve Your Secret")
    encrypted_text = st.text_area("Paste Encrypted Text")
    passkey = st.text_input("Enter Your Passkey", type="password")

    if st.button("🔓 Decrypt"):
        if encrypted_text and passkey:
            result = decrypt(encrypted_text, passkey)
            if result:
                st.success("✅ Decryption Successful!")
                st.write("🔎 Retrieved Data:")
                st.code(result, language="text")
            else:
                remaining = 3 - st.session_state.failed
                st.error(f"❌ Incorrect! Attempts left: {remaining}")
                if st.session_state.failed >= 3:
                    st.warning("🔐 Too many failed attempts! Redirecting to Admin Login.")
                    st.experimental_rerun()
        else:
            st.warning("Fill in both fields.")

elif menu == "🔑 Admin Login":
    st.subheader("Admin Reauthentication")
    admin_input = st.text_input("Master Password", type="password")

    if st.button("Login"):
        if admin_input == "admin123":
            st.session_state.failed = 0
            st.success("🔓 Reauthenticated. Try again.")
            st.experimental_rerun()
        else:
            st.error("❌ Wrong master password.")
