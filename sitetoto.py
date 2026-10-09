import os
import sqlite3
from datetime import date

import streamlit as st
import pandas as pd
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="ETB Real Estate Development",
    layout="wide"
)


# =========================================================
# FILE PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO_PATH = os.path.join(
    BASE_DIR,
    "ETB_Real_Estate_Development.png"
)

FONT_REGULAR = os.path.join(
    BASE_DIR,
    "Amiri-Regular.ttf"
)

FONT_BOLD = os.path.join(
    BASE_DIR,
    "Amiri-Bold.ttf"
)


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    os.path.join(BASE_DIR, "company.db"),
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material TEXT,
    transaction_date TEXT,
    item TEXT,
    quantity REAL,
    price REAL,
    total REAL
)
""")

conn.commit()


# =========================================================
# ARABIC SUPPORT
# =========================================================

def pdf_arabic(text):
    """Prepare Arabic text for display in PDF."""
    if text is None:
        return ""

    text = str(text)

    return get_display(
        arabic_reshaper.reshape(text)
    )


# =========================================================
# PDF FONT CHECK
# =========================================================

def check_pdf_fonts():
    missing = []

    if not os.path.isfile(FONT_REGULAR):
        missing.append("Amiri-Regular.ttf")

    if not os.path.isfile(FONT_BOLD):
        missing.append("Amiri-Bold.ttf")

    if missing:
        raise FileNotFoundError(
‎            "ملفات الخطوط التالية غير موجودة بجوار sitetoto.py: "
            + ", ".join(missing)
        )


# =========================================================
# CREATE PDF
# =========================================================

def create_pdf(
    material_name,
    data,
    report_title,
    month_text=None
):
    check_pdf_fonts()

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_margins(10, 10, 10)
    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    # Add Arabic fonts
    pdf.add_font(
        "Amiri",
        "",
        FONT_REGULAR
    )

    pdf.add_font(
        "Amiri",
        "B",
        FONT_BOLD
    )

    pdf.add_page()

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    if os.path.isfile(LOGO_PATH):
        pdf.image(
            LOGO_PATH,
            x=10,
            y=7,
            w=25
        )

    # -----------------------------------------------------
    # COMPANY NAME
    # -----------------------------------------------------

    pdf.set_y(10)
    pdf.set_font("Amiri", "B", 15)

    pdf.cell(
        0,
        8,
        "ETB REAL ESTATE DEVELOPMENT",
        align="C"
    )

    pdf.ln(10)

    # -----------------------------------------------------
    # REPORT TITLE
    # -----------------------------------------------------

    pdf.set_font("Amiri", "B", 14)

    pdf.cell(
        0,
        8,
        pdf_arabic(
            f"{report_title} - {material_name}"
        ),
        align="C"
    )

    pdf.ln(9)

    # -----------------------------------------------------
    # MONTH
    # -----------------------------------------------------

    if month_text:
        pdf.set_font("Amiri", "", 11)

        pdf.cell(
            0,
            7,
            pdf_arabic(
                f"الشهر: {month_text}"
            ),
            align="C"
        )

        pdf.ln(8)

    # -----------------------------------------------------
    # TABLE HEADERS
    # -----------------------------------------------------

    col_widths = [32, 60, 25, 32, 41]

    headers = [
‎        "التاريخ",
‎        "الصنف",
‎        "الكمية",
‎        "السعر",
‎        "الإجمالي"
    ]

    pdf.set_font("Amiri", "B", 10)
    pdf.set_fill_color(230, 230, 230)

    for header, width in zip(headers, col_widths):
        pdf.cell(
            width,
            10,
            pdf_arabic(header),
            border=1,
            align="C",
            fill=True
        )

    pdf.ln()

    # -----------------------------------------------------
    # TABLE DATA
    # -----------------------------------------------------

    total_all = 0.0
    operation_count = 0

    pdf.set_font("Amiri", "", 9)

    for _, row in data.iterrows():

        transaction_date = row.get("التاريخ", "")
        item = row.get("الصنف", "")

        if pd.isna(transaction_date):
            transaction_date = ""
        else:
            transaction_date = str(transaction_date)

        if pd.isna(item):
            item = ""
        else:
            item = str(item)

        try:
            quantity = float(row.get("الكمية", 0) or 0)
        except (TypeError, ValueError):
            quantity = 0.0

        try:
            price = float(row.get("السعر", 0) or 0)
        except (TypeError, ValueError):
            price = 0.0

        total = quantity * price

        total_all += total
        operation_count += 1

        pdf.cell(
            col_widths[0],
            9,
            pdf_arabic(transaction_date),
            border=1,
            align="C"
        )

        pdf.cell(
            col_widths[1],
            9,
            pdf_arabic(item),
            border=1,
            align="C"
        )

        pdf.cell(
            col_widths[2],
            9,
            f"{quantity:g}",
            border=1,
            align="C"
        )

        pdf.cell(
            col_widths[3],
            9,
            f"{price:.2f}",
            border=1,
            align="C"
        )

        pdf.cell(
            col_widths[4],
            9,
            f"{total:.2f}",
            border=1,
            align="C"
        )

        pdf.ln()

    # -----------------------------------------------------
    # TOTAL
    # -----------------------------------------------------

    pdf.ln(5)
    pdf.set_font("Amiri", "B", 12)

    pdf.cell(
        0,
        9,
        pdf_arabic(
            f"إجمالي العمليات: {total_all:.2f}"
        ),
        align="R"
    )

    pdf.ln(9)

    # -----------------------------------------------------
    # OPERATION COUNT
    # -----------------------------------------------------

    pdf.set_font("Amiri", "", 11)

    pdf.cell(
        0,
        8,
        pdf_arabic(
            f"عدد العمليات: {operation_count}"
        ),
        align="R"
    )

    # Return actual PDF bytes
    output = pdf.output()

    return bytes(output)


# =========================================================
# MONTH NAMES
# =========================================================

month_names = {
‎    "01": "يناير",
‎    "02": "فبراير",
‎    "03": "مارس",
‎    "04": "أبريل",
‎    "05": "مايو",
‎    "06": "يونيو",
‎    "07": "يوليو",
‎    "08": "أغسطس",
‎    "09": "سبتمبر",
‎    "10": "أكتوبر",
‎    "11": "نوفمبر",
‎    "12": "ديسمبر"
}


def format_month(month):
    year = month[:4]
    month_number = month[5:7]

    arabic_month = month_names.get(
        month_number,
        month_number
    )

    return f"{arabic_month} {year}"


# =========================================================
# EMPTY INPUT TABLE
# =========================================================

def empty_input_table():
    return pd.DataFrame({
‎        "التاريخ": [date.today()],
‎        "الصنف": [""],
‎        "الكمية": [0.0],
‎        "السعر": [0.0],
‎        "الإجمالي": [0.0]
    })


# =========================================================
# MATERIAL PAGE
# =========================================================

def material_page(material_name):

    st.title(f"حسابات {material_name}")

    input_key = f"input_table_{material_name}"
    version_key = f"input_version_{material_name}"

    # -----------------------------------------------------
    # INPUT TABLE
    # -----------------------------------------------------

    st.subheader("إضافة العمليات")

    if input_key not in st.session_state:
        st.session_state[input_key] = empty_input_table()

    if version_key not in st.session_state:
        st.session_state[version_key] = 0

    editor_key = (
        f"editor_{material_name}_"
        f"{st.session_state[version_key]}"
    )

    edited_df = st.data_editor(
        st.session_state[input_key],
        num_rows="dynamic",
        use_container_width=True,
        key=editor_key,
        column_config={
‎            "التاريخ": st.column_config.DateColumn(
‎                "التاريخ",
                format="DD/MM/YYYY"
            ),
‎            "الصنف": st.column_config.TextColumn(
‎                "الصنف"
            ),
‎            "الكمية": st.column_config.NumberColumn(
‎                "الكمية",
                min_value=0.0,
                step=1.0
            ),
‎            "السعر": st.column_config.NumberColumn(
‎                "السعر",
                min_value=0.0,
                step=0.01
            ),
‎            "الإجمالي": st.column_config.NumberColumn(
‎                "الإجمالي",
                disabled=True,
                format="%.2f"
            )
        }
    )

    # Work on a copy
    edited_df = edited_df.copy()

    edited_df["الكمية"] = pd.to_numeric(
        edited_df["الكمية"],
        errors="coerce"
    ).fillna(0)

    edited_df["السعر"] = pd.to_numeric(
        edited_df["السعر"],
        errors="coerce"
    ).fillna(0)

    edited_df["الإجمالي"] = (
        edited_df["الكمية"] * edited_df["السعر"]
    )

    st.session_state[input_key] = edited_df.copy()

    current_total = edited_df["الإجمالي"].sum()

    st.write(
        f"**إجمالي العمليات الحالية: {current_total:.2f}**"
    )

    # -----------------------------------------------------
    # SAVE ALL
    # -----------------------------------------------------

    if st.button(
‎        "حفظ الكل",
        type="primary",
        key=f"save_{material_name}"
    ):

        rows_saved = 0

        for _, row in edited_df.iterrows():

            item = str(row["الصنف"]).strip()

            try:
                quantity = float(row["الكمية"])
            except (TypeError, ValueError):
                quantity = 0.0

            try:
                price = float(row["السعر"])
            except (TypeError, ValueError):
                price = 0.0

            if not item or quantity <= 0:
                continue

            transaction_date = row["التاريخ"]

            if pd.isna(transaction_date):
                transaction_date = date.today()

            transaction_date = pd.Timestamp(
                transaction_date
            ).strftime("%Y-%m-%d")

            total = quantity * price

            cursor.execute(
                """
                INSERT INTO transactions (
                    material,
                    transaction_date,
                    item,
                    quantity,
                    price,
                    total
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    material_name,
                    transaction_date,
                    item,
                    quantity,
                    price,
                    total
                )
            )

            rows_saved += 1

        conn.commit()

        if rows_saved > 0:

            st.session_state[input_key] = empty_input_table()

            # Change the editor key to reset the visible table
            st.session_state[version_key] += 1

            st.success(
                f"تم حفظ {rows_saved} عملية بنجاح"
            )

            st.rerun()

        else:
            st.warning("مفيش عمليات صحيحة للحفظ")

    # -----------------------------------------------------
    # CURRENT / UNSAVED PDF
    # -----------------------------------------------------

    st.divider()
    st.subheader("PDF العمليات الحالية")

    if st.button(
‎        "توليد PDF للعمليات الحالية",
        key=f"current_pdf_{material_name}"
    ):

        current_data = edited_df.copy()

        current_data["الصنف"] = (
            current_data["الصنف"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        current_data = current_data[
            (current_data["الصنف"] != "")
            & (current_data["الكمية"] > 0)
        ].copy()

        if current_data.empty:
            st.warning("مفيش عمليات حالية لعمل PDF")

        else:
            try:
                pdf_data = create_pdf(
                    material_name,
                    current_data,
‎                    "تقرير العمليات الحالية"
                )

                st.session_state[
                    f"current_pdf_data_{material_name}"
                ] = pdf_data

                st.success("تم إنشاء PDF للعمليات الحالية")

            except Exception as error:
                st.error(f"حصل خطأ أثناء إنشاء PDF: {error}")

    current_pdf_key = f"current_pdf_data_{material_name}"

    if current_pdf_key in st.session_state:
        st.download_button(
‎            "تحميل PDF للعمليات الحالية",
            data=st.session_state[current_pdf_key],
            file_name=f"{material_name}_العمليات_الحالية.pdf",
            mime="application/pdf",
            key=f"download_current_{material_name}"
        )

    # -----------------------------------------------------
    # SAVED TRANSACTIONS
    # -----------------------------------------------------

    st.divider()
    st.subheader("العمليات المحفوظة")

    saved_df = pd.read_sql_query(
        """
        SELECT
            id,
            transaction_date AS التاريخ,
            item AS الصنف,
            quantity AS الكمية,
            price AS السعر,
            total AS الإجمالي
        FROM transactions
        WHERE material = ?
        ORDER BY transaction_date DESC, id DESC
        """,
        conn,
        params=(material_name,)
    )

    if not saved_df.empty:

        saved_df["مسح"] = False

        edited_saved = st.data_editor(
            saved_df,
            use_container_width=True,
            hide_index=True,
            key=f"saved_editor_{material_name}",
            column_config={
                "id": None,
‎                "التاريخ": st.column_config.TextColumn(
‎                    "التاريخ",
                    disabled=True
                ),
‎                "الصنف": st.column_config.TextColumn(
‎                    "الصنف",
                    disabled=True
                ),
‎                "الكمية": st.column_config.NumberColumn(
‎                    "الكمية",
                    disabled=True
                ),
‎                "السعر": st.column_config.NumberColumn(
‎                    "السعر",
                    disabled=True
                ),
‎                "الإجمالي": st.column_config.NumberColumn(
‎                    "الإجمالي",
                    disabled=True,
                    format="%.2f"
                ),
‎                "مسح": st.column_config.CheckboxColumn(
‎                    "مسح"
                )
            }
        )

        # -------------------------------------------------
        # DELETE SELECTED ONLY
        # -------------------------------------------------

        if st.button(
‎            "مسح المحدد",
            key=f"delete_{material_name}"
        ):

            selected_ids = edited_saved.loc[
                edited_saved["مسح"] == True,
                "id"
            ].tolist()

            if not selected_ids:
                st.warning("اختار عملية واحدة على الأقل")

            else:
                cursor.executemany(
                    "DELETE FROM transactions WHERE id = ?",
                    [(int(transaction_id),)
                     for transaction_id in selected_ids]
                )

                conn.commit()

                st.success(
                    f"تم مسح {len(selected_ids)} عملية"
                )

                st.rerun()

        saved_total = saved_df["الإجمالي"].sum()

        st.write(
            f"**إجمالي كل العمليات المحفوظة: {saved_total:.2f}**"
        )

    else:
        st.info("لا توجد عمليات محفوظة حتى الآن")

    # -----------------------------------------------------
    # SAVED PDF
    # -----------------------------------------------------

    st.divider()
    st.subheader("PDF العمليات المحفوظة")

    months_df = pd.read_sql_query(
        """
        SELECT DISTINCT
            substr(transaction_date, 1, 7) AS month
        FROM transactions
        WHERE material = ?
        ORDER BY month DESC
        """,
        conn,
        params=(material_name,)
    )

    available_months = (
        months_df["month"]
        .dropna()
        .tolist()
    )

    if available_months:

        selected_month = st.selectbox(
‎            "اختار الشهر",
            available_months,
            format_func=format_month,
            key=f"month_{material_name}"
        )

        if st.button(
‎            "توليد PDF للمحفوظات",
            key=f"saved_pdf_{material_name}"
        ):

            month_data = pd.read_sql_query(
                """
                SELECT
                    transaction_date AS التاريخ,
                    item AS الصنف,
                    quantity AS الكمية,
                    price AS السعر,
                    total AS الإجمالي
                FROM transactions
                WHERE material = ?
                  AND substr(transaction_date, 1, 7) = ?
                ORDER BY transaction_date ASC
                """,
                conn,
                params=(material_name, selected_month)
            )

            if month_data.empty:
                st.warning("مفيش عمليات في الشهر ده")

            else:
                try:
                    month_text = format_month(selected_month)

                    saved_pdf = create_pdf(
                        material_name,
                        month_data,
‎                        "تقرير العمليات المحفوظة",
                        month_text
                    )

                    pdf_state_key = (
                        f"saved_pdf_data_{material_name}"
                    )

                    st.session_state[pdf_state_key] = saved_pdf

                    # Remember which month this PDF belongs to
                    st.session_state[
                        f"saved_pdf_month_{material_name}"
                    ] = selected_month

                    st.success("تم إنشاء PDF للمحفوظات")

                except Exception as error:
                    st.error(
                        f"حصل خطأ أثناء إنشاء PDF: {error}"
                    )

        saved_pdf_key = f"saved_pdf_data_{material_name}"
        saved_month_key = f"saved_pdf_month_{material_name}"

        # Only offer the PDF if it matches the selected month
        if (
            saved_pdf_key in st.session_state
            and st.session_state.get(saved_month_key) == selected_month
        ):
            st.download_button(
‎                "تحميل PDF للمحفوظات",
                data=st.session_state[saved_pdf_key],
                file_name=f"{material_name}_{selected_month}.pdf",
                mime="application/pdf",
                key=f"download_saved_{material_name}"
            )

    else:
        st.info("مفيش بيانات محفوظة لعمل PDF")

    # -----------------------------------------------------
    # BACK BUTTON
    # -----------------------------------------------------

    st.divider()

    if st.button(
‎        "رجوع",
        key=f"back_{material_name}"
    ):
        st.session_state["selected_material"] = None
        st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

if "selected_material" not in st.session_state:
    st.session_state["selected_material"] = None


if st.session_state["selected_material"] is None:

    st.title("ETB REAL ESTATE DEVELOPMENT")

    st.write("اختار نوع الخامة")

    materials = [
‎        "خشب",
‎        "حديد",
‎        "أسمنت",
‎        "دهانات",
‎        "كهرباء",
‎        "سباكة"
    ]

    for material in materials:

        if st.button(
            material,
            use_container_width=True,
            key=f"material_{material}"
        ):
            st.session_state["selected_material"] = material
            st.rerun()

else:
    material_page(
        st.session_state["selected_material"]
    )












