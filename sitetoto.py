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
# ARABIC PDF
# =========================================================

def pdf_arabic(text):

    if text is None:
        text = ""

    text = str(text)

    reshaped = arabic_reshaper.reshape(text)

    return get_display(reshaped)


# =========================================================
# GET FONT
# =========================================================

def get_pdf_font():

    fonts = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/arial.ttf"
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
    report_title
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

    font_path = get_pdf_font()

    # -----------------------------------------------------
    # FONT
    # -----------------------------------------------------

    if font_path:

        pdf.add_font(
            "Arabic",
            "",
            font_path
        )

        pdf.set_font(
            "Arabic",
            "",
            11
        )

    else:

        pdf.set_font(
            "Helvetica",
            "",
            10
        )

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    if os.path.exists(LOGO_PATH):

        pdf.image(
            LOGO_PATH,
            x=10,
            y=7,
            w=25
        )

    # -----------------------------------------------------
    # COMPANY NAME
    # -----------------------------------------------------

    if font_path:

        pdf.set_font(
            "Arabic",
            "",
            14
        )

        pdf.cell(
            0,
            8,
            "ETB REAL ESTATE DEVELOPMENT",
            align="C"
        )

    else:

        pdf.set_font(
            "Helvetica",
            "",
            14
        )

        pdf.cell(
            0,
            8,
            "ETB REAL ESTATE DEVELOPMENT",
            align="C"
        )

    pdf.ln(12)

    # -----------------------------------------------------
    # REPORT TITLE
    # -----------------------------------------------------

    if font_path:

        pdf.set_font(
            "Arabic",
            "",
            13
        )

        title = pdf_arabic(
            f"{report_title} - {material_name}"
        )

        pdf.cell(
            0,
            8,
            title,
            align="C"
        )

    else:

        pdf.set_font(
            "Helvetica",
            "",
            13
        )

        pdf.cell(
            0,
            8,
            f"{report_title} - {material_name}",
            align="C"
        )

    pdf.ln(10)

    # -----------------------------------------------------
    # TABLE SETTINGS
    # -----------------------------------------------------

    if font_path:

        pdf.set_font(
            "Arabic",
            "",
            9
        )

    else:

        pdf.set_font(
            "Helvetica",
            "",
            9
        )

    col_widths = [
        32,
        55,
        25,
        35,
        43
    ]

    headers = [
        "التاريخ",
        "الصنف",
        "الكمية",
        "السعر",
        "الإجمالي"
    ]

    # -----------------------------------------------------
    # TABLE HEADER
    # -----------------------------------------------------

    pdf.set_fill_color(
        230,
        230,
        230
    )

    for header, width in zip(
        headers,
        col_widths
    ):

        if font_path:

            header_text = pdf_arabic(
                header
            )

        else:

            header_text = header

        pdf.cell(
            width,
            9,
            header_text,
            border=1,
            align="C",
            fill=True
        )

    pdf.ln()

    # -----------------------------------------------------
    # TABLE DATA
    # -----------------------------------------------------

    total_all = 0

    for _, row in data.iterrows():

        # DATE
        transaction_date = row.get(
            "التاريخ",
            ""
        )

        if pd.isna(transaction_date):

            transaction_date = ""

        else:

            transaction_date = str(
                transaction_date
            )

        # ITEM
        item = row.get(
            "الصنف",
            ""
        )

        if pd.isna(item):

            item = ""

        else:

            item = str(item)

        # QUANTITY
        try:

            quantity = float(
                row.get(
                    "الكمية",
                    0
                )
            )

        except:

            quantity = 0

        # PRICE
        try:

            price = float(
                row.get(
                    "السعر",
                    0
                )
            )

        except:

            price = 0

        # TOTAL
        total = quantity * price

        total_all += total

        # -------------------------------------------------
        # DATE CELL
        # -------------------------------------------------

        if font_path:

            date_text = pdf_arabic(
                transaction_date
            )

        else:

            date_text = transaction_date

        pdf.cell(
            col_widths[0],
            8,
            date_text,
            border=1,
            align="C"
        )

        # -------------------------------------------------
        # ITEM CELL
        # -------------------------------------------------

        if font_path:

            item_text = pdf_arabic(
                item
            )

        else:

            item_text = item

        pdf.cell(
            col_widths[1],
            8,
            item_text,
            border=1,
            align="C"
        )

        # -------------------------------------------------
        # QUANTITY CELL
        # -----------------------------------------------------

        pdf.cell(
            col_widths[2],
            8,
            f"{quantity:g}",
            border=1,
            align="C"
        )

        # -------------------------------------------------
        # PRICE CELL
        # -----------------------------------------------------

        pdf.cell(
            col_widths[3],
            8,
            f"{price:.2f}",
            border=1,
            align="C"
        )

        # -------------------------------------------------
        # TOTAL CELL
        # -----------------------------------------------------

        pdf.cell(
            col_widths[4],
            8,
            f"{total:.2f}",
            border=1,
            align="C"
        )

        pdf.ln()

    # -----------------------------------------------------
    # TOTAL
    # -----------------------------------------------------

    pdf.ln(5)

    if font_path:

        pdf.set_font(
            "Arabic",
            "",
            12
        )

        total_text = pdf_arabic(
            f"إجمالي العمليات: {total_all:.2f}"
        )

        pdf.cell(
            0,
            8,
            total_text,
            align="R"
        )

        pdf.ln(7)

        count_text = pdf_arabic(
            f"عدد العمليات: {len(data)}"
        )

        pdf.cell(
            0,
            7,
            count_text,
            align="R"
        )

    else:

        pdf.set_font(
            "Helvetica",
            "",
            12
        )

        pdf.cell(
            0,
            8,
            f"Total: {total_all:.2f}",
            align="R"
        )

        pdf.ln(7)

        pdf.cell(
            0,
            7,
            f"Operations: {len(data)}",
            align="R"
        )

    # -----------------------------------------------------
    # RETURN PDF
    # -----------------------------------------------------

    return bytes(
        pdf.output()
    )


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

        hide_index=True,

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
    # CALCULATE CURRENT TOTAL
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

    current_total = edited_df[
        "الإجمالي"
    ].sum()

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

            # ITEM

            item = str(
                row["الصنف"]
            ).strip()

            # QUANTITY

            try:

                quantity = float(
                    row["الكمية"]
                )

            except:

                quantity = 0

            # PRICE

            try:

                price = float(
                    row["السعر"]
                )

            except:

                price = 0

            # Skip empty rows

            if item == "":
                continue

            if quantity <= 0:
                continue

            # DATE

            transaction_date = row[
                "التاريخ"
            ]

            if pd.isna(
                transaction_date
            ):

                transaction_date = (
                    date.today()
                )

            transaction_date = pd.Timestamp(
                transaction_date
            ).strftime(
                "%Y-%m-%d"
            )

            # TOTAL

            total = (
                quantity *
                price
            )

            # INSERT

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

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        if rows_saved > 0:

            st.success(
                f"تم حفظ {rows_saved} عملية بنجاح"
            )

            # Reset table

            st.session_state[input_key] = (
                pd.DataFrame({

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
            )

            st.rerun()

        else:

            st.warning(
                "مفيش عمليات صحيحة للحفظ"
            )

    # =====================================================
    # CURRENT PDF
    # =====================================================

    st.divider()

    st.subheader(
        "PDF العمليات الحالية"
    )

    if st.button(
        "توليد PDF للعمليات الحالية",
        key=f"current_pdf_{material_name}"
    ):

        current_data = edited_df.copy()

        # Clean item

        current_data["الصنف"] = (
            current_data["الصنف"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Remove empty rows

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

            # Recalculate

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

            st.session_state[
                f"current_pdf_{material_name}"
            ] = current_pdf

            st.success(
                "تم إنشاء PDF للعمليات الحالية"
            )

    # -----------------------------------------------------
    # DOWNLOAD CURRENT PDF
    # -----------------------------------------------------

    current_pdf_key = (
        f"current_pdf_{material_name}"
    )

    if current_pdf_key in st.session_state:

        st.download_button(

            "تحميل PDF للعمليات الحالية",

            data=st.session_state[
                current_pdf_key
            ],

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
    # SAVED OPERATIONS
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
                            int(transaction_id),
                        )
                    )

                conn.commit()

                st.success(
                    f"تم مسح {len(selected_ids)} عملية"
                )

                st.rerun()

        # =================================================
        # SAVED TOTAL
        # =================================================

        saved_total = saved_df[
            "الإجمالي"
        ].sum()

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

    if not saved_df.empty:

        if st.button(
            "توليد PDF للمحفوظات",
            key=f"saved_pdf_{material_name}"
        ):

            # Take only needed columns

            pdf_saved_data = saved_df[
                [
                    "التاريخ",
                    "الصنف",
                    "الكمية",
                    "السعر",
                    "الإجمالي"
                ]
            ].copy()

            # Convert numbers

            pdf_saved_data["الكمية"] = (
                pd.to_numeric(
                    pdf_saved_data["الكمية"],
                    errors="coerce"
                )
                .fillna(0)
            )

            pdf_saved_data["السعر"] = (
                pd.to_numeric(
                    pdf_saved_data["السعر"],
                    errors="coerce"
                )
                .fillna(0)
            )

            # Recalculate total

            pdf_saved_data["الإجمالي"] = (
                pdf_saved_data["الكمية"]
                *
                pdf_saved_data["السعر"]
            )

            # Create PDF

            saved_pdf = create_pdf(
                material_name,
                pdf_saved_data,
                "تقرير العمليات المحفوظة"
            )

            st.session_state[
                f"saved_pdf_{material_name}"
            ] = saved_pdf

            st.success(
                "تم إنشاء PDF للمحفوظات"
            )

        # -------------------------------------------------
        # DOWNLOAD SAVED PDF
        # -------------------------------------------------

        saved_pdf_key = (
            f"saved_pdf_{material_name}"
        )

        if saved_pdf_key in st.session_state:

            st.download_button(

                "تحميل PDF للمحفوظات",

                data=st.session_state[
                    saved_pdf_key
                ],

                file_name=(
                    f"{material_name}_"
                    "العمليات_المحفوظة.pdf"
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
# HOME
# =========================================================

if "selected_material" not in st.session_state:

    st.session_state[
        "selected_material"
    ] = None


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













