import streamlit as st
import re
import os
import zipfile
from io import BytesIO

st.title("استخراج کد از فایل متنی و بسته‌بندی ZIP")

uploaded_file = st.file_uploader("لطفاً یک فایل متنی آپلود کنید", type=["txt", "md"])

if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    
    # استخراج بلوک‌های کد بر اساس قالب Markdown
    code_blocks = re.findall(r"```(?:[\w+]*\n)?(.*?)```", text, re.DOTALL)

    if code_blocks:
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for i, code in enumerate(code_blocks):
                file_name = f"code_block_{i+1}.py"
                zipf.writestr(file_name, code.strip())

        zip_buffer.seek(0)
        st.success(f"{len(code_blocks)} بلوک کد استخراج شد و داخل فایل ZIP قرار گرفت.")
        st.download_button("دانلود فایل ZIP", zip_buffer, "code_blocks.zip", "application/zip")
    else:
        st.warning("هیچ بلوک کدی در فایل پیدا نشد.")
