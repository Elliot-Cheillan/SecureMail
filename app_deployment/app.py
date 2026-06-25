import html
import streamlit as st
from pipeline import full_pipeline
from report import full_report


def safe(text: str) -> str:
    return html.escape(str(text))


st.set_page_config(
    page_title="SecureMail",
    page_icon="🛡️",
    layout="centered",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] { background-color: #0D0F14; color: #E8EAF0; }
.stApp { background-color: #0D0F14; }
h1, h2, h3 { font-family: 'Space Mono', monospace !important; }
p, li, span, label { font-family: 'Inter', sans-serif !important; }

.hero-badge { font-family: 'Space Mono', monospace; font-size: 11px; letter-spacing: 3px; color: #E8FF47; text-transform: uppercase; margin-bottom: 16px; display: block; }
.hero-title { font-family: 'Space Mono', monospace; font-size: clamp(36px, 6vw, 64px); font-weight: 700; line-height: 1.1; color: #E8EAF0; margin: 0 0 20px 0; }
.hero-title span { color: #E8FF47; font-family: 'Space Mono', monospace; }
.hero-sub { font-family: 'Inter', sans-serif; font-size: 16px; color: #7A8099; font-weight: 300; line-height: 1.6; max-width: 480px; margin-bottom: 48px; }
.section-label { font-family: 'Space Mono', monospace; font-size: 10px; letter-spacing: 4px; color: #4A4F5E; text-transform: uppercase; margin-bottom: 24px; }
.steps-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 48px; }
.step-card { background: #161920; border: 1px solid #1E2330; border-radius: 8px; padding: 20px; }
.step-num { font-family: 'Space Mono', monospace; font-size: 11px; color: #E8FF47; margin-bottom: 8px; }
.step-title { font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500; color: #E8EAF0; margin-bottom: 6px; }
.step-desc { font-family: 'Inter', sans-serif; font-size: 13px; color: #4A4F5E; line-height: 1.5; }
[data-testid="stFileUploader"] { background: #161920 !important; border: 1px dashed #2A2F3E !important; border-radius: 8px !important; padding: 20px 24px 20px 24px !important; }
[data-testid="stFileUploader"]::before { content: ">_ drop your file below"; font-family: 'Space Mono', monospace; font-size: 12px; color: #E8FF47; display: block; margin-bottom: 16px; }
[data-testid="stFileUploader"] section { background: #0D0F14 !important; border: 1px solid #2A2F3E !important; border-radius: 6px !important; }
[data-testid="stFileUploader"] section:hover { border-color: #E8FF47 !important; }
[data-testid="stFileDropzoneInstructions"] { color: #4A4F5E !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important; }
[data-testid="stFileUploaderDeleteBtn"] button { background: transparent !important; border: 1px solid #2A2F3E !important; color: #7A8099 !important; padding: 2px 8px !important; width: auto !important; margin-top: 0 !important; font-size: 12px !important; }
[data-testid="stFileUploaderDeleteBtn"] button:hover { border-color: #FF4F4F !important; color: #FF4F4F !important; background: transparent !important; }
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInput"] + div button { background: #1E2330 !important; color: #E8EAF0 !important; font-family: 'Space Mono', monospace !important; font-size: 12px !important; font-weight: 400 !important; border: 1px solid #2A2F3E !important; border-radius: 4px !important; padding: 6px 16px !important; width: auto !important; margin-top: 0 !important; letter-spacing: 0 !important; }
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInput"] + div button:hover { border-color: #E8FF47 !important; color: #E8FF47 !important; background: #1E2330 !important; }

[data-testid="stButton"] button { background-color: #E8FF47 !important; color: #0D0F14 !important; font-family: 'Space Mono', monospace !important; font-size: 13px !important; font-weight: 700 !important; border: none !important; border-radius: 6px !important; padding: 12px 32px !important; letter-spacing: 1px !important; width: 100% !important; cursor: pointer !important; margin-top: 8px !important; }
[data-testid="stButton"] button:hover { background-color: #d4e83d !important; }

.disclaimer { background: #0F1117; border-left: 2px solid #2A2F3E; padding: 14px 18px; border-radius: 0 6px 6px 0; margin-top: 32px; margin-bottom: 8px; }
.disclaimer p { font-family: 'Inter', sans-serif; font-size: 12px; color: #4A4F5E; margin: 0; line-height: 1.6; }
.disclaimer a { color: #E8FF47 !important; text-decoration: none; }
.custom-divider { border: none; border-top: 1px solid #1E2330; margin: 40px 0; }

.verdict-spam { font-family: 'Space Mono', monospace; font-size: 48px; font-weight: 700; color: #FF4F4F; }
.verdict-ham { font-family: 'Space Mono', monospace; font-size: 48px; font-weight: 700; color: #E8FF47; }
.confidence-label { font-family: 'Space Mono', monospace; font-size: 12px; letter-spacing: 3px; color: #4A4F5E; text-transform: uppercase; }
.info-card { background: #161920; border: 1px solid #1E2330; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; }
.info-card-label { font-family: 'Space Mono', monospace; font-size: 10px; letter-spacing: 3px; color: #4A4F5E; text-transform: uppercase; margin-bottom: 8px; }
.info-card-value { font-family: 'Inter', sans-serif; font-size: 14px; color: #E8EAF0; }
.shap-bar-pos { background: #FF4F4F; height: 6px; border-radius: 3px; }
.shap-bar-neg { background: #E8FF47; height: 6px; border-radius: 3px; }
.tag-safe { background: #1a2e1a; color: #4CAF50; font-family: 'Space Mono', monospace; font-size: 11px; padding: 2px 8px; border-radius: 4px; border: 1px solid #4CAF50; }
.tag-suspect { background: #2e1a1a; color: #FF4F4F; font-family: 'Space Mono', monospace; font-size: 11px; padding: 2px 8px; border-radius: 4px; border: 1px solid #FF4F4F; }
.tag-unknown { background: #1e1e24; color: #4A4F5E; font-family: 'Space Mono', monospace; font-size: 11px; padding: 2px 8px; border-radius: 4px; border: 1px solid #4A4F5E; }
</style>
""",
    unsafe_allow_html=True,
)


if "report" not in st.session_state:
    st.session_state.report = None


if st.session_state.report is None:

    st.markdown(
        '<span class="hero-badge">&#9632; Student project — ML / NLP</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h1 class="hero-title">Secure<span>Mail</span></h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-sub">Drop a <code>.eml</code> file and the model will tell you whether it\'s spam or not — with an explanation of what triggered the decision.</p>',
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-label">How it works</p>', unsafe_allow_html=True)
    st.markdown(
        """
    <div class="steps-grid">
        <div class="step-card">
            <div class="step-num">01</div>
            <div class="step-title">Parse</div>
            <div class="step-desc">Headers, links, attachments, and raw content are extracted from your file.</div>
        </div>
        <div class="step-card">
            <div class="step-num">02</div>
            <div class="step-title">Predict</div>
            <div class="step-desc">A neural network trained on labelled emails classifies the message as spam or legitimate.</div>
        </div>
        <div class="step-card">
            <div class="step-num">03</div>
            <div class="step-title">Explain</div>
            <div class="step-desc">SHAP values surface which features drove the decision, so you understand why — not just what.</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    file = st.file_uploader(
        "Upload a .eml file",
        type=["eml"],
        label_visibility="hidden",
    )

    if file:
        if st.button("RUN ANALYSIS"):
            with st.spinner("Analysing the email, please wait..."):
                json_mail_infos, final_df, results, explanation, content = (
                    full_pipeline(file_bytes=file.getvalue(), filename=file.name)
                )
                st.session_state.report = full_report(
                    explanation, content, results, json_mail_infos
                )
            st.rerun()

    st.markdown(
        """
    <div class="disclaimer">
        <p>This is a student project built for learning purposes. The model is <strong style="color:#E8EAF0">not production-ready</strong> and will make mistakes — do not rely on it for anything critical. Source code and training details on <a href="https://github.com/Elliot-Cheillan/SecureMail" target="_blank">GitHub ↗</a></p>
    </div>
    """,
        unsafe_allow_html=True,
    )


else:
    report = st.session_state.report

    verdict_class = "verdict-spam" if report["result"] == "SPAM" else "verdict-ham"
    verdict_icon = "⚠️" if report["result"] == "SPAM" else "✅"
    st.markdown(
        f'<div class="{verdict_class}">{verdict_icon} {safe(report["result"])}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="confidence-label">Confidence — {safe(report["confidence_level"])} ({round(report["confidence"] * 100, 1)}%)</p>',
        unsafe_allow_html=True,
    )
    st.progress(float(report["confidence"]))

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Mail info</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
        <div class="info-card">
            <div class="info-card-label">From</div>
            <div class="info-card-value">
                {safe(report["sender_display"] or "—")}<br>
                <span style="color:#4A4F5E;font-size:12px">{safe(report["sender"] or "")}</span>
            </div>
        </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
        <div class="info-card">
            <div class="info-card-label">Subject</div>
            <div class="info-card-value">{safe(report["subject"]) if report["subject"] else "—"}</div>
        </div>""",
            unsafe_allow_html=True,
        )

    col3, col4 = st.columns(2)
    spf_tag = (
        "tag-safe"
        if report["spf"] == "pass"
        else ("tag-suspect" if report["spf"] == "fail" else "tag-unknown")
    )
    dkim_tag = (
        "tag-safe"
        if report["dkim"] == "pass"
        else ("tag-suspect" if report["dkim"] == "fail" else "tag-unknown")
    )
    with col3:
        st.markdown(
            f"""
        <div class="info-card">
            <div class="info-card-label">SPF</div>
            <div class="info-card-value">
                <span class="{spf_tag}">{safe(report["spf"]) if report["spf"] else "unavailable"}</span>
            </div>
        </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
        <div class="info-card">
            <div class="info-card-label">DKIM</div>
            <div class="info-card-value">
                <span class="{dkim_tag}">{safe(report["dkim"]) if report["dkim"] else "unavailable"}</span>
            </div>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Top indicators</p>', unsafe_allow_html=True)

    indicators = report["top_5_indicators"]
    if indicators:
        float_values = {
            k: float(v.item()) if hasattr(v, "item") else float(v)
            for k, v in indicators.items()
        }
        max_shap = max(abs(v) for v in float_values.values()) or 1
        for feature, value in float_values.items():
            direction = "→ spam" if value > 0 else "→ legitimate"
            bar_class = "shap-bar-pos" if value > 0 else "shap-bar-neg"
            bar_width = int(abs(value) / max_shap * 100)
            st.markdown(
                f"""
            <div class="info-card" style="margin-bottom:8px">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                    <span style="font-family:'Inter',sans-serif;font-size:13px;color:#E8EAF0">{safe(feature)}</span>
                    <span style="font-family:'Space Mono',monospace;font-size:11px;color:#4A4F5E">{direction}</span>
                </div>
                <div style="background:#1E2330;border-radius:3px;height:6px">
                    <div class="{bar_class}" style="width:{bar_width}%"></div>
                </div>
            </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No indicators found pushing toward this decision.")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    st.markdown('<p class="section-label">Mail content</p>', unsafe_allow_html=True)

    if report["spamwords"]:
        words = report["content"].strip().split()
        highlighted = []
        for i, word in enumerate(words):
            safe_word = safe(word)
            if i in report["spamwords"]:
                highlighted.append(
                    f'<mark style="background:#FF4F4F22;color:#FF4F4F;border-radius:3px;padding:0 2px">{safe_word}</mark>'
                )
            else:
                highlighted.append(safe_word)
        content_html = " ".join(highlighted)
        st.markdown(
            f"""
        <div class="info-card" style="font-family:'Inter',sans-serif;font-size:13px;line-height:1.8;color:#7A8099;max-height:300px;overflow-y:auto">
            {content_html}
        </div>""",
            unsafe_allow_html=True,
        )
        st.caption(
            f"⚠️ {len(report['spamwords'])} spam word(s) detected — highlighted in red"
        )
    else:
        st.markdown(
            f"""
        <div class="info-card" style="font-family:'Inter',sans-serif;font-size:13px;line-height:1.8;color:#7A8099;max-height:300px;overflow-y:auto">
            {safe(report["content"])}
        </div>""",
            unsafe_allow_html=True,
        )
        st.caption("✅ No spam words detected in content")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    if report["links"]:
        st.markdown('<p class="section-label">Links</p>', unsafe_allow_html=True)
        for link in report["links"]:
            is_http = link["url"].startswith("http://")
            has_redirect = link["redirect"] and link["redirect"] != link["url"]
            tag = (
                '<span class="tag-suspect">suspect</span>'
                if (is_http or has_redirect)
                else '<span class="tag-safe">safe</span>'
            )
            redirect_line = (
                f'<div style="font-size:11px;color:#4A4F5E;margin-top:4px">↳ redirects to {safe(link["redirect"])}</div>'
                if has_redirect
                else ""
            )
            st.markdown(
                f"""
            <div class="info-card" style="margin-bottom:8px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-family:'Space Mono',monospace;font-size:12px;color:#E8EAF0">{safe(link["domain"])}</span>
                    {tag}
                </div>
                <div style="font-size:11px;color:#4A4F5E;margin-top:4px">{safe(link["url"])}</div>
                {redirect_line}
            </div>""",
                unsafe_allow_html=True,
            )
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    if report["attachments"]:
        st.markdown('<p class="section-label">Attachments</p>', unsafe_allow_html=True)
        suspect_extensions = {
            ".exe",
            ".bat",
            ".cmd",
            ".scr",
            ".vbs",
            ".js",
            ".jar",
            ".msi",
            ".ps1",
        }
        for att in report["attachments"]:
            is_suspect = att["extension"].lower() in suspect_extensions
            tag = (
                '<span class="tag-suspect">suspect</span>'
                if is_suspect
                else '<span class="tag-safe">safe</span>'
            )
            st.markdown(
                f"""
            <div class="info-card" style="margin-bottom:8px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-family:'Space Mono',monospace;font-size:12px;color:#E8EAF0">{safe(att["filename"])}</span>
                    {tag}
                </div>
                <div style="font-size:11px;color:#4A4F5E;margin-top:4px">{safe(att["extension"])}</div>
            </div>""",
                unsafe_allow_html=True,
            )
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    if st.button("← Analyse another email"):
        st.session_state.report = None
        st.rerun()
