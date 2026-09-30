from __future__ import annotations

import os
import sys
from datetime import date


# ---------------------------------------------------------
# Make project root available to Python
# ---------------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

if PROJECT_ROOT not in sys.path:

    sys.path.insert(
        0,
        PROJECT_ROOT,
    )


import requests
import streamlit as st

from dotenv import load_dotenv

from backend.utils.text_utils import (
    format_html_preview,
)


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()

BACKEND_URL = (
    os.getenv(
        "BACKEND_URL",
        "http://127.0.0.1:8000",
    )
    .rstrip("/")
)


# ---------------------------------------------------------
# Streamlit configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        margin-bottom: 0;
        font-weight: 700;
    }

    .subtitle {
        text-align: center;
        color: #9aa4b2;
        margin-top: 0;
    }

    .legal-preview {
        background: #111827;
        color: #e5e7eb;
        padding: 28px;
        border-radius: 14px;
        line-height: 1.75;
        max-height: 700px;
        overflow-y: auto;
        border: 1px solid #374151;
    }

    .legal-preview h3 {
        color: #f9fafb;
        margin-top: 20px;
        margin-bottom: 8px;
    }

    .legal-preview p {
        margin-bottom: 12px;
    }

    .notice {
        padding: 14px 18px;
        border-radius: 10px;
        background: #fff7ed;
        color: #7c2d12;
        border: 1px solid #fed7aa;
    }

    .feature-box {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

logo_path = os.path.join(
    PROJECT_ROOT,
    "static",
    "logo.svg",
)


header_left, header_center, header_right = (
    st.columns([1, 2, 1])
)


with header_center:

    if os.path.exists(logo_path):

        st.image(
            logo_path,
            width=90,
        )

    st.markdown(
        "<h1 class='main-title'>LegalEase</h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <p class='subtitle'>
        AI-powered legal document drafting assistant
        </p>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# Disclaimer
# ---------------------------------------------------------

st.markdown(
    """
    <div class='notice'>
    <b>Important:</b>
    LegalEase creates AI-assisted legal drafts for
    general informational and drafting purposes.
    It is not legal advice and does not replace review
    by a qualified legal professional.
    </div>
    """,
    unsafe_allow_html=True,
)


st.write("")


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "last_request" not in st.session_state:

    st.session_state.last_request = None


# ---------------------------------------------------------
# Input form
# ---------------------------------------------------------

st.subheader(
    "Create Your Legal Document"
)


with st.form(
    "document_form"
):

    left, right = st.columns(2)

    with left:

        document_type = st.text_input(
            "Document Type",
            placeholder=(
                "e.g. Freelance Work Contract"
            ),
        )

        parties = st.text_area(
            "Parties Involved",
            placeholder=(
                "Jane Doe (Service Provider), "
                "TechNova Inc. (Client)"
            ),
            height=140,
        )

    with right:

        effective_date = st.text_input(
            "Effective Date",
            value=date.today().strftime(
                "%B %d, %Y"
            ),
        )

        terms = st.text_area(
            "Terms & Conditions",
            placeholder=(
                "Payment within 30 days; "
                "Confidentiality must be maintained; "
                "Either party may terminate with 15 days notice"
            ),
            height=140,
        )

    submitted = st.form_submit_button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )


# ---------------------------------------------------------
# Generate
# ---------------------------------------------------------

if submitted:

    if not document_type.strip():

        st.error(
            "Please enter the document type."
        )

    elif not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    else:

        payload = {
            "document_type":
                document_type,

            "parties":
                parties,

            "terms":
                terms,

            "effective_date":
                effective_date,
        }

        try:

            with st.spinner(
                "Generating your legal draft..."
            ):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=180,
                )

            if response.ok:

                data = response.json()

                st.session_state.document = (
                    data["document"]
                )

                st.session_state.last_request = (
                    payload
                )

                st.success(
                    "Document generated successfully."
                )

            else:

                try:

                    detail = response.json().get(
                        "detail",
                        response.text,
                    )

                except ValueError:

                    detail = response.text

                st.error(
                    f"Backend error: {detail}"
                )

        except requests.RequestException as exc:

            st.error(
                "Could not connect to the FastAPI "
                f"backend at {BACKEND_URL}. "
                "Start the backend first.\n\n"
                f"Details: {exc}"
            )


# ---------------------------------------------------------
# Preview and editing
# ---------------------------------------------------------

if st.session_state.document:

    st.divider()

    st.subheader(
        "Document Preview"
    )

    preview_html = format_html_preview(
        st.session_state.document
    )

    st.markdown(
        preview_html,
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader(
        "Edit Document"
    )

    edited_document = st.text_area(
        "Edit the generated document",
        value=st.session_state.document,
        height=500,
        label_visibility="collapsed",
    )

    if st.button(
        "Save Edits"
    ):

        st.session_state.document = (
            edited_document
        )

        st.success(
            "Your edits have been saved."
        )

    # -----------------------------------------------------
    # Downloads
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Download Document"
    )

    request_data = (
        st.session_state.last_request
        or {}
    )

    col1, col2, col3 = st.columns(3)

    download_options = [
        (
            col1,
            "txt",
            "Download TXT",
            "text/plain",
        ),
        (
            col2,
            "docx",
            "Download DOCX",
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document",
        ),
        (
            col3,
            "pdf",
            "Download PDF",
            "application/pdf",
        ),
    ]

    for (
        column,
        file_format,
        button_label,
        mime_type,
    ) in download_options:

        with column:

            try:

                export_payload = {
                    **request_data,
                    "text":
                        st.session_state.document,
                }

                response = requests.post(
                    f"{BACKEND_URL}/export/"
                    f"{file_format}",
                    json=export_payload,
                    timeout=60,
                )

                if response.ok:

                    st.download_button(
                        label=button_label,
                        data=response.content,
                        file_name=(
                            f"legalease_document."
                            f"{file_format}"
                        ),
                        mime=mime_type,
                        use_container_width=True,
                    )

                else:

                    st.error(
                        f"{file_format.upper()} "
                        "export failed."
                    )

            except requests.RequestException as exc:

                st.error(
                    f"{file_format.upper()} "
                    f"export unavailable: {exc}"
                )


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "LegalEase • AI-assisted document drafting • "
    "Always review important legal documents with "
    "a qualified legal professional."
)