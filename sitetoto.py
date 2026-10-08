import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
import os


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="ETB Real Estate Development",
    layout="wide"
)


# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "company.db",
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
# LOGO
# =========================================================

LOGO_PATH = "ETB_Real_Estate_Development.png"


# =========================================================
# ARABIC PDF SUPPORT
# =========================================================

def pdf_arabic(text):

    if text is None:
        return ""

    text = str(text)

    reshaped = arabic_reshaper.reshape(text)

    return get_display(reshaped)


# =========================================================
# GET PDF FONT
# =========================================================

def get_pdf_font():

    fonts = [

        # Font uploaded with the project
        "DejaVuSans.ttf",

        "./DejaVuSans.ttf",

        # Linux - Streamlit Cloud
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

        # Windows - local computer
        "C:/Windows/Fonts/arial.ttf",

        "C:/Windows/Fonts/tahoma.ttf"
    ]

    for font in fonts:

        if os.path.exists(font):
            return font

    return None


# =========================================================
# CREATE PDF
# =========================================================

def create_pdf(
    material_name,
    data,
    report_title,
    month_text=None
):

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.add_page()


    # =====================================================
    # FONT
    # =====================================================

    font_path = get_pdf_font()

    if font_path is None:

        st.error(
            "Arabic font not found. "
            "Please upload DejaVuSans.ttf "
            "to the same folder as sitetoto.py"
        )

        return None


    # Add Unicode font

    pdf.add_font(
        "Arabic",
        "",
        font_path
    )

    pdf.set_font(
        "Arabic",
        "",
        10
    )


    # =====================================================
    # LOGO
    # =====================================================

    if os.path.exists(LOGO_PATH):

        pdf.image(
            LOGO_PATH,
            x=10,
            y=7,
            w=25
        )


    # =====================================================
    # COMPANY NAME
    # =====================================================

    pdf.set_y(10)

    pdf.set_font(
        "Arabic",
        "",
        15
    )

    pdf.cell(
        0,
        8,
        "ETB REAL ESTATE DEVELOPMENT",
        align="C"
    )

    pdf.ln(10)


    # =====================================================
    # REPORT TITLE
    # =====================================================

    pdf.set_font(
        "Arabic",
        "",
        14
    )

    pdf.cell(
        0,
        8,
        pdf_arabic(
            f"{report_title} - {material_name}"
        ),
        align="C"
    )

    pdf.ln(8)


    # =====================================================
    # MONTH
    # =====================================================

    if month_text:

        pdf.set_font(
            "Arabic",
            "",
            10
        )

        pdf.cell(
            0,
            7,
            pdf_arabic(
                f"الشهر: {month_text}"
            ),
            align="C"
        )

        pdf.ln(6)


    # =====================================================
    # TABLE
    # =====================================================

    pdf.set_font(
        "Arabic",
        "",
        9
    )


    # A4 width = 210
    # Margins = 10 + 10
    # Available = 190

    col_widths = [
        32,   # التاريخ
        60,   # الصنف
        25,   # الكمية
        32,   # السعر
        41    # الإجمالي
    ]


    headers = [
        "التاريخ",
        "الصنف",
        "الكمية",
        "السعر",
        "الإجمالي"
    ]


    # =====================================================
    # TABLE HEADER
    # =====================================================

    pdf.set_fill_color(
        230,
        230,
        230
    )


    for header, width in zip(
        headers,
        col_widths
    ):

        pdf.cell(
            width,
            9,
            pdf_arabic(header),
            border=1,
            align="C",
            fill=True
        )

    pdf.ln()


    # =====================================================
    # TABLE DATA
    # =====================================================

    total_all = 0


    for _, row in data.iterrows():

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        transaction_date = row.get(
            "التاريخ",
            ""
        )

        if pd.isna(
            transaction_date
        ):

            transaction_date = ""

        else:

            transaction_date = str(
                transaction_date
            )


        # -------------------------------------------------
        # ITEM
        # -------------------------------------------------

        item = row.get(
            "الصنف",
            ""
        )

        if pd.isna(item):

            item = ""

        else:

            item = str(item)


        # -------------------------------------------------
        # QUANTITY
        # -------------------------------------------------

        try:

            quantity = float(
                row.get(
                    "الكمية",
                    0
                )
            )

        except:

            quantity = 0.0


        # -------------------------------------------------
        # PRICE
        # -------------------------------------------------

        try:

            price = float(
                row.get(
                    "السعر",
                    0
                )
            )

        except:

            price = 0.0


        # -------------------------------------------------
        # TOTAL
        # -------------------------------------------------

        total = quantity * price

        total_all += total


        # -------------------------------------------------
        # DATE CELL
        # -------------------------------------------------

        pdf.cell(
            col_widths[0],
            8,
            pdf_arabic(
                transaction_date
            ),
            border=1,
            align="C"
        )


        # -------------------------------------------------
        # ITEM CELL
        # -------------------------------------------------

        pdf.cell(
            col_widths[1],
            8,
            pdf_arabic(
                item
            ),
            border=1,
            align="C"
        )


        # -------------------------------------------------
        # QUANTITY CELL
        # -------------------------------------------------

        pdf.cell(
            col_widths[2],
            8,
            f"{quantity:g}",
            border=1,
            align="C"
        )


        # -------------------------------------------------
        # PRICE CELL
        # -------------------------------------------------

        pdf.cell(
            col_widths[3],
            8,
            f"{price:.2f}",
            border=1,
            align="C"
        )


        # -------------------------------------------------
        # TOTAL CELL
        # -------------------------------------------------

        pdf.cell(
            col_widths[4],
            8,
            f"{total:.2f}",
            border=1,
            align="C"
        )


        pdf.ln()


    # =====================================================
    # TOTAL
    # =====================================================

    pdf.ln(5)

    pdf.set_font(
        "Arabic",
        "",
        12
    )

    pdf.cell(
        0,
        8,
        pdf_arabic(
            f"إجمالي العمليات: {total_all:.2f}"
        ),
        align="R"
    )

    pdf.ln(7)


    # =====================================================
    # NUMBER OF OPERATIONS
    # =====================================================

    pdf.set_font(
        "Arabic",
        "",
        10
    )

    pdf.cell(
        0,
        7,
        pdf_arabic(
            f"عدد العمليات: {len(data)}"
        ),
        align="R"
    )


    # =====================================================
    # PDF OUTPUT
    # =====================================================

    pdf_bytes = pdf.output()

    if isinstance(
        pdf_bytes,
        bytearray
    ):

        pdf_bytes = bytes(
            pdf_bytes
        )

    elif isinstance(
        pdf_bytes,
        bytes
    ):

        pass

    else:

        pdf_bytes = bytes(
            pdf_bytes
        )

    return pdf_bytes


# =========================================================
# MONTH NAMES
# =========================================================

month_names = {

    "01": "يناير",

    "02": "فبراير",

    "03": "مارس",

    "04": "أبريل",

    "05": "مايو",

    "06": "يونيو",

    "07": "يوليو",

    "08": "أغسطس",

    "09": "سبتمبر",

    "10": "أكتوبر",

    "11": "نوفمبر",

    "12": "ديسمبر"
}


# =========================================================
# MATERIAL PAGE
# =========================================================

def material_page(material_name):

    st.title(
        f"حسابات {material_name}"
    )


    # =====================================================
    # INPUT TABLE
    # =====================================================

    st.subheader(
        "إضافة العمليات"
    )


    input_key = (
        f"input_table_{material_name}"
    )


    # -----------------------------------------------------
    # FIRST TIME
    # -----------------------------------------------------

    if input_key not in st.session_state:

        st.session_state[input_key] = pd.DataFrame({

            "التاريخ": [
                date.today()
            ],

            "الصنف": [
                ""
            ],

            "الكمية": [
                0.0
            ],

            "السعر": [
                0.0
            ],

            "الإجمالي": [
                0.0
            ]
        })


    # =====================================================
    # INPUT EDITOR
    # =====================================================

    edited_df = st.data_editor(

        st.session_state[input_key],

        num_rows="dynamic",

        use_container_width=True,

        key=f"editor_{material_name}",

        column_config={

            "التاريخ": st.column_config.DateColumn(
                "التاريخ",
                format="DD/MM/YYYY"
            ),

            "الصنف": st.column_config.TextColumn(
                "الصنف"
            ),

            "الكمية": st.column_config.NumberColumn(
                "الكمية",
                min_value=0.0,
                step=1.0
            ),

            "السعر": st.column_config.NumberColumn(
                "السعر",
                min_value=0.0,
                step=0.01
            ),

            "الإجمالي": st.column_config.NumberColumn(
                "الإجمالي",
                disabled=True,
                format="%.2f"
            )
        }
    )


    # Save current table

    st.session_state[input_key] = (
        edited_df.copy()
    )


    # =====================================================
    # CALCULATIONS
    # =====================================================

    edited_df["الكمية"] = pd.to_numeric(
        edited_df["الكمية"],
        errors="coerce"
    ).fillna(0)


    edited_df["السعر"] = pd.to_numeric(
        edited_df["السعر"],
        errors="coerce"
    ).fillna(0)


    edited_df["الإجمالي"] = (
        edited_df["الكمية"]
        *
        edited_df["السعر"]
    )


    current_total = (
        edited_df["الإجمالي"].sum()
    )


    st.write(
        f"**إجمالي العمليات الحالية: {current_total:.2f}**"
    )


    # =====================================================
    # SAVE ALL
    # =====================================================

    if st.button(
        "حفظ الكل",
        type="primary",
        key=f"save_{material_name}"
    ):

        rows_saved = 0


        for _, row in edited_df.iterrows():

            item = str(
                row["الصنف"]
            ).strip()


            quantity = float(
                row["الكمية"]
            )


            price = float(
                row["السعر"]
            )


            if item == "":
                continue


            if quantity <= 0:
                continue


            # Date

            transaction_date = (
                row["التاريخ"]
            )


            if pd.isna(
                transaction_date
            ):

                transaction_date = (
                    date.today()
                )


            transaction_date = (
                pd.Timestamp(
                    transaction_date
                ).strftime(
                    "%Y-%m-%d"
                )
            )


            total = (
                quantity
                *
                price
            )


            # Insert

            cursor.execute(

                """
                INSERT INTO transactions
                (
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

            st.success(
                f"تم حفظ {rows_saved} عملية بنجاح"
            )


            # Reset input table

            st.session_state[input_key] = pd.DataFrame({

                "التاريخ": [
                    date.today()
                ],

                "الصنف": [
                    ""
                ],

                "الكمية": [
                    0.0
                ],

                "السعر": [
                    0.0
                ],

                "الإجمالي": [
                    0.0
                ]
            })


            st.rerun()


        else:

            st.warning(
                "مفيش عمليات صحيحة للحفظ"
            )


    # =====================================================
    # CURRENT / UNSAVED PDF
    # =====================================================

    st.divider()

    st.subheader(
        "PDF العمليات الحالية"
    )


    if st.button(
        "توليد PDF للعمليات الحالية",
        key=f"current_pdf_{material_name}"
    ):

        current_data = (
            edited_df.copy()
        )


        # Remove empty items

        current_data["الصنف"] = (

            current_data["الصنف"]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        current_data = current_data[
            current_data["الصنف"] != ""
        ]


        # Remove zero quantity

        current_data = current_data[
            current_data["الكمية"] > 0
        ]


        if current_data.empty:

            st.warning(
                "مفيش عمليات حالية لعمل PDF"
            )


        else:

            current_data["الإجمالي"] = (

                current_data["الكمية"]
                *
                current_data["السعر"]
            )


            current_pdf = create_pdf(

                material_name,

                current_data,

                "تقرير العمليات الحالية"
            )


            if current_pdf is not None:

                st.success(
                    "تم إنشاء PDF للعمليات الحالية"
                )


                st.download_button(

                    "تحميل PDF للعمليات الحالية",

                    data=current_pdf,

                    file_name=(
                        f"{material_name}_"
                        "العمليات_الحالية.pdf"
                    ),

                    mime="application/pdf",

                    key=(
                        f"download_current_"
                        f"{material_name}"
                    )
                )


    # =====================================================
    # SAVED DATA
    # =====================================================

    st.divider()

    st.subheader(
        "العمليات المحفوظة"
    )


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

        params=(
            material_name,
        )
    )


    # =====================================================
    # SAVED TABLE
    # =====================================================

    if not saved_df.empty:

        saved_df["مسح"] = False


        edited_saved = st.data_editor(

            saved_df,

            use_container_width=True,

            hide_index=True,

            key=f"saved_editor_{material_name}",

            column_config={

                "id": None,

                "التاريخ": st.column_config.TextColumn(
                    "التاريخ",
                    disabled=True
                ),

                "الصنف": st.column_config.TextColumn(
                    "الصنف",
                    disabled=True
                ),

                "الكمية": st.column_config.NumberColumn(
                    "الكمية",
                    disabled=True
                ),

                "السعر": st.column_config.NumberColumn(
                    "السعر",
                    disabled=True
                ),

                "الإجمالي": st.column_config.NumberColumn(
                    "الإجمالي",
                    disabled=True,
                    format="%.2f"
                ),

                "مسح": st.column_config.CheckboxColumn(
                    "مسح"
                )
            }
        )


        # =================================================
        # DELETE SELECTED
        # =================================================

        if st.button(
            "مسح المحدد",
            key=f"delete_{material_name}"
        ):


            selected_ids = (
                edited_saved.loc[
                    edited_saved["مسح"] == True,
                    "id"
                ]
                .tolist()
            )


            if not selected_ids:

                st.warning(
                    "اختار عملية واحدة على الأقل"
                )


            else:

                for transaction_id in selected_ids:

                    cursor.execute(

                        """
                        DELETE FROM transactions
                        WHERE id = ?
                        """,

                        (
                            int(
                                transaction_id
                            ),
                        )
                    )


                conn.commit()


                st.success(
                    f"تم مسح {len(selected_ids)} عملية"
                )


                st.rerun()


        # =================================================
        # TOTAL SAVED
        # =================================================

        saved_total = (
            saved_df["الإجمالي"].sum()
        )


        st.write(
            f"**إجمالي كل العمليات المحفوظة: {saved_total:.2f}**"
        )


    else:

        st.info(
            "لا توجد عمليات محفوظة حتى الآن"
        )


    # =====================================================
    # SAVED PDF
    # =====================================================

    st.divider()

    st.subheader(
        "PDF العمليات المحفوظة"
    )


    # =====================================================
    # GET MONTHS
    # =====================================================

    months_df = pd.read_sql_query(

        """
        SELECT DISTINCT

            substr(
                transaction_date,
                1,
                7
            ) AS month

        FROM transactions

        WHERE material = ?

        ORDER BY month DESC
        """,

        conn,

        params=(
            material_name,
        )
    )


    available_months = (

        months_df["month"]
        .dropna()
        .tolist()
    )


    # =====================================================
    # MONTH SELECTION
    # =====================================================

    if available_months:


        def format_month(month):

            year = month[:4]

            month_number = month[5:7]

            arabic_month = (
                month_names.get(
                    month_number,
                    month_number
                )
            )

            return (
                f"{arabic_month} {year}"
            )


        selected_month = st.selectbox(

            "اختار الشهر",

            available_months,

            format_func=format_month,

            key=f"month_{material_name}"
        )


        # =================================================
        # CREATE SAVED PDF
        # =================================================

        if st.button(

            "توليد PDF للمحفوظات",

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

                AND substr(
                    transaction_date,
                    1,
                    7
                ) = ?

                ORDER BY
                    transaction_date ASC,
                    id ASC
                """,

                conn,

                params=(

                    material_name,

                    selected_month
                )
            )


            if month_data.empty:

                st.warning(
                    "مفيش عمليات في الشهر ده"
                )


            else:

                month_text = format_month(
                    selected_month
                )


                saved_pdf = create_pdf(

                    material_name,

                    month_data,

                    "تقرير العمليات المحفوظة",

                    month_text
                )


                if saved_pdf is not None:

                    st.success(
                        "تم إنشاء PDF للمحفوظات"
                    )


                    st.download_button(

                        "تحميل PDF للمحفوظات",

                        data=saved_pdf,

                        file_name=(
                            f"{material_name}_"
                            f"{selected_month}.pdf"
                        ),

                        mime="application/pdf",

                        key=(
                            f"download_saved_"
                            f"{material_name}"
                        )
                    )


    else:

        st.info(
            "مفيش بيانات محفوظة لعمل PDF"
        )


    # =====================================================
    # BACK
    # =====================================================

    st.divider()


    if st.button(
        "رجوع",
        key=f"back_{material_name}"
    ):

        st.session_state[
            "selected_material"
        ] = None


        st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

if "selected_material" not in st.session_state:

    st.session_state[
        "selected_material"
    ] = None


# =========================================================
# SHOW HOME
# =========================================================

if (
    st.session_state[
        "selected_material"
    ] is None
):


    st.title(
        "ETB REAL ESTATE DEVELOPMENT"
    )


    st.write(
        "اختار نوع الخامة"
    )


    materials = [

        "خشب",

        "حديد",

        "أسمنت",

        "دهانات",

        "كهرباء",

        "سباكة"
    ]


    for material in materials:


        if st.button(

            material,

            use_container_width=True,

            key=f"material_{material}"
        ):


            st.session_state[
                "selected_material"
            ] = material


            st.rerun()


# =========================================================
# MATERIAL PAGE
# =========================================================

else:

    material_page(

        st.session_state[
            "selected_material"
        ]
    )













