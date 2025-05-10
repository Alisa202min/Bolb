import streamlit as st
import re
import os
import zipfile
import shutil
from pathlib import Path

def extract_code_files(input_text, output_dir="code_files"):
    """
    Extract code snippets from input text, save them as files based on their titles,
    and create a ZIP archive of all files.
    
    Args:
        input_text (str): Text containing titled code blocks.
        output_dir (str): Directory to temporarily store files before zipping.
    
    Returns:
        tuple: (zip_path, files_created) where zip_path is the path to the ZIP file
               and files_created is the list of file paths, or (None, []) if no files.
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Regular expression to match titles and code blocks
        title_pattern = r'File \d+: ([^\n]+)\n```[^\n]*\n([\s\S]*?)(?:\n```|\Z)'
        matches = re.finditer(title_pattern, input_text)

        files_created = []

        # Process each match
        for match in matches:
            file_path = match.group(1).strip()  # e.g., tests/conftest.py
            code_content = match.group(2).strip()  # Code block content

            # Create directories if needed
            file_dir = os.path.dirname(file_path)
            if file_dir:
                os.makedirs(os.path.join(output_dir, file_dir), exist_ok=True)

            # Write code to file
            full_file_path = os.path.join(output_dir, file_path)
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(code_content)
            files_created.append(file_path)

        if not files_created:
            return None, []

        # Create ZIP archive
        zip_path = 'rfcbot_test_files.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_created:
                zipf.write(os.path.join(output_dir, file_path), file_path)

        return zip_path, files_created
    except Exception as e:
        st.error(f"Error processing input: {str(e)}")
        return None, []

# Streamlit app configuration
st.set_page_config(page_title="Code File Extractor", page_icon="📦", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header { font-size: 2.5em; color: #FF4B4B; text-align: center; }
    .sub-header { font-size: 1.5em; color: #333; }
    .success-box { background-color: #e6ffed; padding: 10px; border-radius: 5px; }
    .error-box { background-color: #ffe6e6; padding: 10px; border-radius: 5px; }
    .stButton>button { background-color: #FF4B4B; color: white; border-radius: 5px; }
    .stButton>button:hover { background-color: #e04343; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">استخراج فایل‌های کد</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">متن یا فایل متنی حاوی کدهای برنامه را وارد کنید تا به صورت ZIP دانلود شود</div>', unsafe_allow_html=True)

# Tabs for input method
tab1, tab2 = st.tabs(["متن را جای‌گذاری کنید", "فایل را آپلود کنید"])

with tab1:
    input_text = st.text_area("متن خود را اینجا جای‌گذاری کنید (مثال: 'File X: path/to/file' و کد)", height=300)

with tab2:
    uploaded_file = st.file_uploader("یک فایل متنی آپلود کنید", type=["txt"])
    if uploaded_file:
        input_text = uploaded_file.read().decode("utf-8")

# Process button
if st.button("تولید فایل ZIP"):
    if not input_text:
        st.markdown('<div class="error-box">خطا: لطفاً متن وارد کنید یا فایلی آپلود کنید.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("در حال پردازش..."):
            # Clear previous files
            if os.path.exists("code_files"):
                shutil.rmtree("code_files")
            if os.path.exists("rfcbot_test_files.zip"):
                os.remove("rfcbot_test_files.zip")

            # Extract and zip files
            zip_path, files_created = extract_code_files(input_text)
            
            if zip_path and files_created:
                st.markdown('<div class="success-box">فایل‌ها با موفقیت استخراج شدند!</div>', unsafe_allow_html=True)
                st.write("**فایل‌های استخراج‌شده:**")
                for file in files_created:
                    st.write(f"- {file}")
                
                # Provide download button
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="دانلود فایل ZIP",
                        data=f,
                        file_name="rfcbot_test_files.zip",
                        mime="application/zip"
                    )
            else:
                st.markdown('<div class="error-box">خطا: هیچ کد معتبری در ورودی یافت نشد.</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("ساخته‌شده با ❤️ با استفاده از Streamlit | برای تست RFCBot")
