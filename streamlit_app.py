# ذخیره این فایل به نام: app.py

import streamlit as st
import zipfile
import os
import io

def process_zip(zip_file):
    output_lines = []
    with zipfile.ZipFile(zip_file) as z:
        for file_info in z.infolist():
            if file_info.filename.endswith(".htm.txt"):
                with z.open(file_info) as f:
                    try:
                        content_bytes = f.read()
                        content = content_bytes.decode("utf-8")
                        lines = content.splitlines()
                        verified_line_count = content.count('\n') + 1 if content else 0
                        if len(lines) != verified_line_count:
                            st.warning(f"⚠ تعداد خطوط ناسازگار در فایل: {file_info.filename}")
                            continue
                        clean_filename = os.path.basename(file_info.filename)[:-4]  # حذف .txt
                        output_lines.append(f"{clean_filename}")
                        output_lines.append("---")
                        output_lines.append(content.strip())
                        output_lines.append("---\n")
                    except Exception as e:
                        st.error(f"خطا در فایل {file_info.filename}: {e}")

    return '\n'.join(output_lines)


st.title("ادغام محتوای فایل‌های .htm.txt")

uploaded_file = st.file_uploader("یک فایل ZIP شامل فایل‌های `.htm.txt` آپلود کنید", type="zip")

if uploaded_file:
    with st.spinner("در حال پردازش فایل‌ها..."):
        result_text = process_zip(uploaded_file)
        st.success("پردازش انجام شد ✅")

        st.download_button(
            label="دانلود خروجی به صورت فایل متنی",
            data=result_text,
            file_name="output.txt",
            mime="text/plain"
        )
        st.text_area("پیش‌نمایش خروجی", value=result_text[:3000], height=400)
