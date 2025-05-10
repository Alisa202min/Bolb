import streamlit as st
import re
import os
import zipfile
import shutil
from pathlib import Path

def extract_code_files(input_text, output_dir="code_files"):
    """
    استخراج کدهای برنامه از متن ورودی، ذخیره به صورت فایل با نام‌های مشخص‌شده در عنوان‌ها،
    و ایجاد یک آرشیو ZIP از تمام فایل‌ها.
    
    Args:
        input_text (str): متن حاوی بلوک‌های کد با عنوان.
        output_dir (str): پوشه موقت برای ذخیره فایل‌ها قبل از فشرده‌سازی.
    
    Returns:
        tuple: (zip_path, files_created) که zip_path مسیر فایل ZIP و files_created لیست مسیرهای فایل‌هاست،
               یا (None, []) در صورت عدم وجود فایل.
    """
    try:
        # ایجاد پوشه خروجی در صورت عدم وجود
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # الگوی منظم برای تطبیق عنوان‌ها و بلوک‌های کد
        title_pattern = r'File \d+: ([^\n]+)\n```(?:\w+)?\n([\s\S]*?)(?:\n```|\Z)'
        matches = re.finditer(title_pattern, input_text)

        files_created = []

        # پردازش هر تطبیق
        for match in matches:
            file_path = match.group(1).strip()  # مثال: tests/conftest.py
            code_content = match.group(2).strip()  # محتوای بلوک کد

            # ایجاد پوشه‌ها در صورت نیاز
            file_dir = os.path.dirname(file_path)
            if file_dir:
                os.makedirs(os.path.join(output_dir, file_dir), exist_ok=True)

            # نوشتن کد در فایل
            full_file_path = os.path.join(output_dir, file_path)
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(code_content)
            files_created.append(file_path)

        if not files_created:
            st.warning("هشدار: هیچ بلوک کد معتبری در متن ورودی یافت نشد.")
            return None, []

        # ایجاد آرشیو ZIP
        zip_path = 'rfcbot_test_files.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_created:
                zipf.write(os.path.join(output_dir, file_path), file_path)

        return zip_path, files_created
    except Exception as e:
        st.error(f"خطا در پردازش ورودی: {str(e)}")
        return None, []

# تنظیمات برنامه Streamlit
st.set_page_config(page_title="استخراج فایل‌های کد", page_icon="📦", layout="centered")

# استایل‌های سفارشی
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

# سربرگ
st.markdown('<div class="main-header">استخراج فایل‌های کد</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">متن یا فایل متنی حاوی بلوک‌های کد (مانند "File X: path/to/file") را وارد کنید</div>', unsafe_allow_html=True)

# تب‌ها برای روش‌های ورودی
tab1, tab2 = st.tabs(["متن را جای‌گذاری کنید", "فایل را آپلود کنید"])

with tab1:
    input_text = st.text_area("متن خود را اینجا جای‌گذاری کنید", height=300, help="مثال: File 1: tests/conftest.py\n```python\nکد...\n```")

with tab2:
    uploaded_file = st.file_uploader("یک فایل متنی (.txt) آپلود کنید", type=["txt"])
    if uploaded_file:
        input_text = uploaded_file.read().decode("utf-8")

# دکمه پردازش
if st.button("تولید فایل ZIP"):
    if not input_text:
        st.markdown('<div class="error-box">خطا: لطفاً متن وارد کنید یا فایلی آپلود کنید.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("در حال پردازش..."):
            # پاکسازی فایل‌های قبلی
            if os.path.exists("code_files"):
                shutil.rmtree("code_files")
            if os.path.exists("rfcbot_test_files.zip"):
                os.remove("rfcbot_test_files.zip")

            # استخراج و فشرده‌سازی فایل‌ها
            zip_path, files_created = extract_code_files(input_text)
            
            if zip_path and files_created:
                st.markdown('<div class="success-box">فایل‌ها با موفقیت استخراج شدند!</div>', unsafe_allow_html=True)
                st.write("**فایل‌های استخراج‌شده:**")
                for file in files_created:
                    st.write(f"- {file}")
                
                # ارائه دکمه دانلود
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="دانلود فایل ZIP",
                        data=f,
                        file_name="rfcbot_test_files.zip",
                        mime="application/zip"
                    )
            else:
                st.markdown('<div class="error-box">خطا: هیچ کد معتبری در ورودی یافت نشد.</div>', unsafe_allow_html=True)

# پاورقی
st.markdown("---")
st.markdown("ساخته‌شده با ❤️ با استفاده از Streamlit | برای تست RFCBot")
