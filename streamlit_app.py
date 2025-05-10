import streamlit as st
import zipfile
import os

st.set_page_config(page_title="خواندن فایل‌های .htm.txt", layout="wide")

def process_zip(zip_file):
    output_lines = []
    logs = []

    with zipfile.ZipFile(zip_file) as z:
        file_list = [f for f in z.infolist() if f.filename.endswith(".html.txt") and not f.is_dir()]
        logs.append(f"✅ تعداد فایل‌های یافت‌شده با پسوند .html.txt: {len(file_list)}")

        for file_info in file_list:
            logs.append(f"\n🔹 پردازش فایل: {file_info.filename}")
            try:
                with z.open(file_info) as f:
                    content_bytes = f.read()
                    content = content_bytes.decode("utf-8")
                    lines = content.splitlines()
                    verified_line_count = content.count('\n') + 1 if content and not content.endswith('\n') else content.count('\n')

                    if len(lines) != verified_line_count:
                        logs.append(f"⚠ (اطلاع): اختلاف احتمالی در شمارش خطوط (splitlines: {len(lines)} vs count('\\n'): {verified_line_count})")

                    clean_filename = os.path.basename(file_info.filename)[:-4]  # حذف .txt
                    output_lines.append(f"{clean_filename}")
                    output_lines.append("---")
                    output_lines.append(content.strip())
                    output_lines.append("---\n")
                    logs.append(f"✅ فایل با موفقیت پردازش شد.")
            except Exception as e:
                logs.append(f"❌ خطا در خواندن فایل {file_info.filename}: {e}")

    return '\n'.join(output_lines), '\n'.join(logs)

st.title("📄 ابزار ترکیب فایل‌های .htm.txt از فایل ZIP")

st.markdown("""
این ابزار فایل‌های متنی با پسوند `.htm.txt` را از یک فایل ZIP می‌خواند و آن‌ها را به فرمت دلخواه شما ترکیب می‌کند.

- نام فایل با پسوند `.txt` حذف می‌شود.
- محتوای فایل با دو خط `---` جدا می‌شود.
- در پایین صفحه خروجی را می‌بینید.
""")

uploaded_file = st.file_uploader("📁 لطفاً فایل ZIP را آپلود کنید", type="zip")

if uploaded_file:
    with st.spinner("⏳ در حال پردازش فایل‌ها... لطفاً صبر کنید"):
        result_text, log_output = process_zip(uploaded_file)
        st.success("✅ پردازش با موفقیت انجام شد!")

        st.subheader("📜 گزارش مرحله‌به‌مرحله:")
        st.code(log_output, language="bash")

        st.subheader("📝 خروجی نهایی: محتوای دقیق فایل‌ها")
        st.text_area("🔍 محتوای ترکیب‌شده فایل‌ها", value=result_text, height=600)

        st.download_button(
            label="⬇️ دانلود فایل خروجی",
            data=result_text,
            file_name="combined_output.txt",
            mime="text/plain"
        )
else:
    st.info("🔺 ابتدا یک فایل ZIP آپلود کنید که شامل فایل‌های `.htm.txt` باشد.")
