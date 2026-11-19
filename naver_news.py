# ============================================================
# 네이버 실시간 뉴스 인텔리전스 대시보드 (NCP API Gateway)
# naver_news.py — Modern Indigo/Slate Edition (Full-Featured)
# ============================================================
import os
import re
import json
import html
import urllib.request
import urllib.parse
import urllib.error
from collections import Counter
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# ── .env 로드 ──────────────────────────────────────────────
_ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=True)

# ── 페이지 설정 ────────────────────────────────────────────
st.set_page_config(
    page_title="NewsPulse · 뉴스 인텔리전스",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
#  GOOGLE MATERIAL DESIGN 3 CSS (Sky/Azure Blue + Tonal Surfaces)
# ═══════════════════════════════════════════════════════════
DARK_CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

html { color-scheme: dark !important; }
:root, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp, body {
    color-scheme: dark !important;
    --background-color: #0f172a !important;
    --secondary-background-color: #162033 !important;
    --primary-color: #0ea5e9 !important;
    --text-color: #f8fafc !important;
    --font: "Pretendard", "Noto Sans KR", "Malgun Gothic", system-ui, sans-serif !important;
    --secondary-text-color: #94a3b8 !important;
    --widget-background-color: #1e293b !important;
    --widget-border-color: rgba(148, 163, 184, 0.16) !important;
}
:root {
    --surface: #0f172a;
    --surface-sidebar: #131c31;
    --surface-container: #1e293b;
    --surface-container-high: #273549;
    --on-surface: #f8fafc;
    --on-surface-variant: #94a3b8;
    --on-surface-muted: #64748b;
    --primary: #38bdf8;
    --primary-strong: #0ea5e9;
    --primary-deep: #0284c7;
    --on-primary: #ffffff;
    --primary-container: rgba(56, 189, 248, 0.14);
    --primary-glow: rgba(14, 165, 233, 0.28);
    --outline-subtle: rgba(148, 163, 184, 0.12);
    --pos: #16a34a;
    --pos-text: #4ade80;
    --pos-soft: rgba(22, 163, 74, 0.16);
    --neg: #dc2626;
    --neg-text: #fb7185;
    --neg-soft: rgba(220, 38, 38, 0.16);
    --neu-soft: rgba(148, 163, 184, 0.14);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 20px;
    --radius-pill: 9999px;
    --elevation: 0 8px 24px rgba(2, 6, 23, 0.32);
    --elevation-sm: 0 4px 14px rgba(2, 6, 23, 0.22);
}
* { font-family: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', system-ui, sans-serif !important; }
[data-testid="stIconMaterial"], span[data-testid="stIconMaterial"],
.material-symbols-outlined, .material-symbols-rounded, .material-icons {
    font-family: "Material Symbols Outlined", "Material Symbols Rounded", "Material Icons", sans-serif !important;
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
    background: var(--surface) !important;
    color: var(--on-surface) !important;
}
[data-testid="stHeader"] {
    background: rgba(15, 23, 42, 0.85) !important;
    backdrop-filter: blur(12px) !important;
}
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stMainMenu"],
.stAppDeployButton,
.stDeployButton,
#MainMenu {
    display: none !important;
    visibility: hidden !important;
}
[data-testid="stDialog"] div[role="dialog"],
div[role="dialog"] {
    width: min(900px, 92vw) !important;
    max-width: 900px !important;
}
[data-testid="stSidebar"] {
    background: var(--surface-sidebar) !important;
    border-right: 1px solid var(--outline-subtle) !important;
}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p {
    color: var(--on-surface) !important;
}
[data-testid="stForm"] {
    background: var(--surface-container) !important;
    border: none !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px !important;
    box-shadow: var(--elevation-sm) !important;
}
[data-testid="stTextInput"] > div, [data-testid="stTextInput"] > div > div,
[data-testid="stDateInput"] > div, [data-testid="stDateInput"] > div > div {
    border: none !important; background: transparent !important; box-shadow: none !important;
}
[data-testid="stTextInput"] input, [data-testid="stDateInput"] input {
    background: var(--surface-container-high) !important;
    color: var(--on-surface) !important;
    border: 1px solid var(--outline-subtle) !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stDateInput"] input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary-glow) !important;
    outline: none !important;
}
div[data-baseweb="select"] > div {
    background: var(--surface-container-high) !important;
    border: 1px solid var(--outline-subtle) !important;
    border-radius: var(--radius-md) !important;
}
div[data-baseweb="select"] span { color: var(--on-surface) !important; }

.stButton > button, [data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    box-shadow: 0 4px 14px var(--primary-glow) !important;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4) !important;
}

/* MD3 Pill Tabs (완전 둥근 탭 + 기본 빨간 밑줄 제거) */
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
    background: transparent !important;
    height: 0 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface-container) !important;
    border-radius: var(--radius-pill) !important;
    gap: 6px !important;
    padding: 6px !important;
    border: none !important;
    box-shadow: var(--elevation-sm) !important;
    width: fit-content !important;
    margin-bottom: 16px !important;
}
.stTabs [data-baseweb="tab"],
.stTabs button[data-baseweb="tab"],
.stTabs [role="tab"] {
    background: transparent !important;
    color: var(--on-surface-variant) !important;
    border-radius: var(--radius-pill) !important;
    border: none !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: var(--surface-container-high) !important;
    color: var(--on-surface) !important;
}
.stTabs [aria-selected="true"],
.stTabs button[aria-selected="true"] {
    background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    color: #ffffff !important;
    border-radius: var(--radius-pill) !important;
    box-shadow: 0 4px 14px var(--primary-glow) !important;
}
.stTabs [aria-selected="true"] *,
.stTabs button[aria-selected="true"] * {
    color: #ffffff !important;
}

/* Hero Banner */
.hero {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.16) 0%, rgba(56, 189, 248, 0.06) 55%, var(--surface-container) 100%);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: var(--elevation);
}
.hero h1 {
    color: #f8fafc !important;
    font-size: clamp(1.4rem, 2.2vw, 1.85rem);
    font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.02em;
}
.hero p { color: var(--on-surface-variant) !important; margin: 0; font-size: 0.94rem; line-height: 1.5; }

/* MD3 Uniform 5-Column KPI Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
@media (max-width: 1100px) {
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.kpi-card {
    background: var(--surface-container);
    border-radius: var(--radius-lg);
    padding: 18px 20px;
    min-height: 122px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--elevation-sm);
    transition: transform 0.18s ease, background 0.18s ease;
}
.kpi-card:hover {
    background: var(--surface-container-high);
    transform: translateY(-2px);
}
.kpi-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--on-surface-variant);
    letter-spacing: -0.01em;
}
.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--on-surface);
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin: 6px 0;
    white-space: nowrap;
}
.kpi-sub {
    display: inline-flex;
    align-items: center;
    width: fit-content;
    font-size: 0.74rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: var(--radius-sm);
    background: var(--primary-container);
    color: #7dd3fc;
}
.kpi-sub-pos { background: var(--pos-soft); color: var(--pos-text); }
.kpi-sub-neu { background: var(--neu-soft); color: var(--on-surface-variant); }

.sidebar-brand {
    text-align: center; padding: 8px 0 16px; margin-bottom: 12px;
    border-bottom: 1px solid var(--outline-subtle);
}
.sidebar-brand h2 {
    background: linear-gradient(135deg, #7dd3fc, #0ea5e9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 1.35rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;
}
.sidebar-brand p { color: var(--on-surface-muted) !important; font-size: 0.75rem; margin: 4px 0 0; }
.section-label {
    font-size: 0.78rem; font-weight: 700; color: var(--primary); letter-spacing: 0.04em;
    text-transform: uppercase; margin: 20px 0 10px; display: flex; align-items: center; gap: 8px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--outline-subtle); }

.news-card {
    background: var(--surface-container); border-radius: var(--radius-lg);
    padding: 20px 22px; margin-bottom: 14px; box-shadow: var(--elevation-sm);
    transition: transform 0.18s ease, background 0.18s ease;
}
.news-card:hover { background: var(--surface-container-high); transform: translateY(-1px); }
.news-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 8px; line-height: 1.45; }
.news-title a { color: var(--on-surface) !important; text-decoration: none; }
.news-title a:hover { color: var(--primary) !important; }
.news-desc { font-size: 0.89rem; color: var(--on-surface-variant); line-height: 1.6; margin-bottom: 12px; }
.news-meta {
    font-size: 0.76rem; color: var(--on-surface-muted); display: flex; flex-wrap: wrap;
    gap: 8px 12px; align-items: center;
}
.news-meta a { color: var(--primary) !important; text-decoration: none; font-weight: 600; }
.badge {
    display: inline-flex; align-items: center; border-radius: var(--radius-sm);
    padding: 3px 10px; font-size: 0.73rem; font-weight: 600;
}
.badge-accent { background: var(--primary-container); color: #7dd3fc; }
.badge-neutral { background: var(--neu-soft); color: var(--on-surface-variant); }
.badge-pos { background: var(--pos-soft); color: var(--pos-text); }
.badge-neg { background: var(--neg-soft); color: var(--neg-text); }
.badge-cluster { background: rgba(14, 165, 233, 0.2); color: #38bdf8; }
.chip {
    display: inline-block; background: var(--surface-container-high);
    color: var(--on-surface-variant); border-radius: var(--radius-sm); padding: 4px 12px;
    font-size: 0.78rem; margin: 3px 5px 3px 0; font-weight: 500;
}
.chip-hot { background: var(--primary-container); color: #7dd3fc; font-weight: 600; }
.insight-box {
    background: var(--surface-container); border-radius: var(--radius-lg);
    padding: 20px 22px; box-shadow: var(--elevation-sm);
}
.insight-box h4 { margin: 0 0 10px; font-size: 0.95rem; color: #7dd3fc; font-weight: 600; }
.brief-box {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), var(--surface-container));
    border-radius: var(--radius-lg); padding: 22px 26px; margin-bottom: 16px;
    line-height: 1.65; box-shadow: var(--elevation-sm);
}
.footer-note { font-size: 0.73rem; text-align: center; opacity: 0.55; margin-top: 16px; }
.empty-state { text-align: center; padding: 48px 16px; color: var(--on-surface-variant); }
.empty-state .icon { font-size: 2.5rem; margin-bottom: 8px; }

.data-table-wrap {
    width: 100%; max-height: 460px; overflow: auto;
    border-radius: var(--radius-lg); background: var(--surface-container);
    box-shadow: var(--elevation-sm);
}
.data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; color: var(--on-surface); }
.data-table thead th {
    position: sticky; top: 0; z-index: 1; background: var(--surface-container-high);
    color: var(--on-surface); font-weight: 600; text-align: left;
    padding: 12px 14px; border-bottom: 1px solid var(--outline-subtle); white-space: nowrap;
}
.data-table tbody td {
    padding: 12px 14px; border-bottom: 1px solid var(--outline-subtle);
    vertical-align: top; color: var(--on-surface); background: var(--surface-container);
}
.data-table tbody tr:hover td { background: var(--surface-container-high); }
.data-table a { color: var(--primary) !important; text-decoration: none; font-weight: 600; }

/* App Footer (object_eraser.py 스타일 + MD3 다크 톤) */
.app-footer-wrap {
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid var(--outline-subtle);
}
.footer-meta-text {
    font-size: 0.82rem;
    color: var(--on-surface-variant);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    height: 36px;
    white-space: nowrap;
}
.footer-blog-wrap {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    height: 36px;
}
.footer-blog-link {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    color: #7dd3fc !important;
    text-decoration: none !important;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 8px;
    background: var(--primary-container);
    border: 1px solid rgba(56, 189, 248, 0.25);
    transition: all 0.18s ease;
    white-space: nowrap;
}
.footer-blog-link:hover {
    background: rgba(56, 189, 248, 0.24);
    transform: translateY(-1px);
}
.terms-rule-box {
    background: var(--surface-container-high);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    font-size: 0.86rem;
    line-height: 1.55;
    color: var(--on-surface-variant);
}
.terms-rule-box b { color: var(--on-surface); }
.oss-table {
    width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 8px;
}
.oss-table th, .oss-table td {
    padding: 8px 10px; border-bottom: 1px solid var(--outline-subtle); text-align: left;
}
.oss-table th { color: var(--primary); font-weight: 700; }
.oss-table td { color: var(--on-surface-variant); }
</style>
"""

LIGHT_CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

html { color-scheme: light !important; }
:root, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp, body {
    color-scheme: light !important;
    --background-color: #f8fafc !important;
    --secondary-background-color: #ffffff !important;
    --primary-color: #0284c7 !important;
    --text-color: #0f172a !important;
    --font: "Pretendard", "Noto Sans KR", "Malgun Gothic", system-ui, sans-serif !important;
    --secondary-text-color: #475569 !important;
    --widget-background-color: #ffffff !important;
    --widget-border-color: rgba(15, 23, 42, 0.1) !important;
}
:root {
    --surface: #f8fafc;
    --surface-sidebar: #ffffff;
    --surface-container: #ffffff;
    --surface-container-high: #f1f5f9;
    --on-surface: #0f172a;
    --on-surface-variant: #475569;
    --on-surface-muted: #64748b;
    --primary: #0284c7;
    --primary-strong: #0ea5e9;
    --primary-deep: #0369a1;
    --on-primary: #ffffff;
    --primary-container: rgba(14, 165, 233, 0.12);
    --primary-glow: rgba(14, 165, 233, 0.22);
    --outline-subtle: rgba(15, 23, 42, 0.08);
    --pos: #16a34a;
    --pos-text: #15803d;
    --pos-soft: rgba(22, 163, 74, 0.12);
    --neg: #dc2626;
    --neg-text: #b91c1c;
    --neg-soft: rgba(220, 38, 38, 0.12);
    --neu-soft: rgba(100, 116, 139, 0.12);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 20px;
    --radius-pill: 9999px;
    --elevation: 0 8px 24px rgba(15, 23, 42, 0.08);
    --elevation-sm: 0 4px 14px rgba(15, 23, 42, 0.05);
}
* { font-family: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', system-ui, sans-serif !important; }
[data-testid="stIconMaterial"], span[data-testid="stIconMaterial"],
.material-symbols-outlined, .material-symbols-rounded, .material-icons {
    font-family: "Material Symbols Outlined", "Material Symbols Rounded", "Material Icons", sans-serif !important;
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
    background: var(--surface) !important;
    color: var(--on-surface) !important;
}
[data-testid="stHeader"] {
    background: rgba(248, 250, 252, 0.85) !important;
    backdrop-filter: blur(12px) !important;
}
[data-testid="stToolbar"],
[data-testid="stDeployButton"],
[data-testid="stMainMenu"],
.stAppDeployButton,
.stDeployButton,
#MainMenu {
    display: none !important;
    visibility: hidden !important;
}
[data-testid="stSidebar"] {
    background: var(--surface-sidebar) !important;
    border-right: 1px solid var(--outline-subtle) !important;
}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p {
    color: #0f172a !important;
}
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span,
[data-testid="stCheckbox"] label,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] h5 {
    color: #0f172a !important;
}
[data-testid="stForm"] {
    background: var(--surface-container-high) !important;
    border: none !important;
    border-radius: var(--radius-lg) !important;
    padding: 16px !important;
}
[data-testid="stTextInput"] > div, [data-testid="stTextInput"] > div > div,
[data-testid="stDateInput"] > div, [data-testid="stDateInput"] > div > div {
    border: none !important; background: transparent !important; box-shadow: none !important;
}
[data-testid="stTextInput"] input, [data-testid="stDateInput"] input {
    background: #ffffff !important;
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stDateInput"] input::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stDateInput"] input:focus {
    border-color: var(--primary-strong) !important;
    box-shadow: 0 0 0 3px var(--primary-glow) !important;
    outline: none !important;
}
div[data-baseweb="select"] > div,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: var(--radius-md) !important;
    color: #0f172a !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div,
[data-testid="stSelectbox"] div[data-baseweb="select"] span,
[data-testid="stSelectbox"] div[data-baseweb="select"] div {
    color: #0f172a !important;
    -webkit-text-fill-color: #0f172a !important;
}
div[data-baseweb="select"] svg {
    fill: #475569 !important;
    color: #475569 !important;
}
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
ul[role="listbox"],
li[role="option"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
}
li[role="option"]:hover {
    background: #f1f5f9 !important;
    color: #0284c7 !important;
}

.stButton > button, [data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    box-shadow: 0 4px 12px var(--primary-glow) !important;
}
.stButton > button p, [data-testid="stFormSubmitButton"] > button p {
    color: #ffffff !important;
}

/* MD3 Pill Tabs */
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
    background: transparent !important;
    height: 0 !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface-container) !important;
    border-radius: var(--radius-pill) !important;
    gap: 6px !important;
    padding: 6px !important;
    border: none !important;
    box-shadow: var(--elevation-sm) !important;
    width: fit-content !important;
    margin-bottom: 16px !important;
}
.stTabs [data-baseweb="tab"],
.stTabs button[data-baseweb="tab"],
.stTabs [role="tab"] {
    background: transparent !important;
    color: #334155 !important;
    border-radius: var(--radius-pill) !important;
    border: none !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"] p,
.stTabs button[data-baseweb="tab"] p {
    color: #334155 !important;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background: var(--surface-container-high) !important;
    color: #0f172a !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"],
.stTabs button[data-baseweb="tab"][aria-selected="true"],
.stTabs button[role="tab"][aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"]:hover {
    background-color: #0284c7 !important;
    background-image: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
    color: #ffffff !important;
    border-radius: var(--radius-pill) !important;
    box-shadow: 0 4px 12px var(--primary-glow) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] *,
.stTabs button[data-baseweb="tab"][aria-selected="true"] *,
.stTabs button[role="tab"][aria-selected="true"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.hero {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(56, 189, 248, 0.04) 55%, #ffffff 100%);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: var(--elevation);
}
.hero h1 { color: #0f172a !important; font-size: clamp(1.4rem, 2.2vw, 1.85rem); font-weight: 700; margin: 0 0 6px 0; }
.hero p { color: var(--on-surface-variant) !important; margin: 0; font-size: 0.94rem; }

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}
@media (max-width: 1100px) {
    .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.kpi-card {
    background: var(--surface-container);
    border-radius: var(--radius-lg);
    padding: 18px 20px;
    min-height: 122px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--elevation-sm);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: var(--elevation); }
.kpi-label { font-size: 0.8rem; font-weight: 600; color: var(--on-surface-variant); }
.kpi-value {
    font-size: 1.65rem; font-weight: 700; color: var(--on-surface);
    font-variant-numeric: tabular-nums; letter-spacing: -0.02em; line-height: 1.2;
    margin: 6px 0; white-space: nowrap;
}
.kpi-sub {
    display: inline-flex; align-items: center; width: fit-content;
    font-size: 0.74rem; font-weight: 600; padding: 3px 10px;
    border-radius: var(--radius-sm); background: var(--primary-container); color: #0284c7;
}
.kpi-sub-pos { background: var(--pos-soft); color: var(--pos-text); }
.kpi-sub-neu { background: var(--neu-soft); color: var(--on-surface-variant); }

.sidebar-brand {
    text-align: center; padding: 8px 0 16px; margin-bottom: 12px;
    border-bottom: 1px solid var(--outline-subtle);
}
.sidebar-brand h2 { color: #0284c7 !important; font-size: 1.35rem; font-weight: 800; margin: 0; }
.sidebar-brand p { color: var(--on-surface-muted) !important; font-size: 0.75rem; margin: 4px 0 0; }
.section-label {
    font-size: 0.78rem; font-weight: 700; color: #0284c7; letter-spacing: 0.04em;
    text-transform: uppercase; margin: 20px 0 10px; display: flex; align-items: center; gap: 8px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: var(--outline-subtle); }

.news-card {
    background: var(--surface-container); border-radius: var(--radius-lg);
    padding: 20px 22px; margin-bottom: 14px; box-shadow: var(--elevation-sm);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.news-card:hover { transform: translateY(-1px); box-shadow: var(--elevation); }
.news-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 8px; line-height: 1.45; }
.news-title a { color: var(--on-surface) !important; text-decoration: none; }
.news-title a:hover { color: var(--primary) !important; }
.news-desc { font-size: 0.89rem; color: var(--on-surface-variant); line-height: 1.6; margin-bottom: 12px; }
.news-meta {
    font-size: 0.76rem; color: var(--on-surface-muted); display: flex; flex-wrap: wrap;
    gap: 8px 12px; align-items: center;
}
.news-meta a { color: #0284c7 !important; text-decoration: none; font-weight: 600; }
.badge {
    display: inline-flex; align-items: center; border-radius: var(--radius-sm);
    padding: 3px 10px; font-size: 0.73rem; font-weight: 600;
}
.badge-accent { background: var(--primary-container); color: #0284c7; }
.badge-neutral { background: var(--neu-soft); color: #475569; }
.badge-pos { background: var(--pos-soft); color: var(--pos-text); }
.badge-neg { background: var(--neg-soft); color: var(--neg-text); }
.badge-cluster { background: rgba(14, 165, 233, 0.16); color: #0369a1; }
.chip {
    display: inline-block; background: var(--surface-container-high);
    color: var(--on-surface-variant); border-radius: var(--radius-sm); padding: 4px 12px;
    font-size: 0.78rem; margin: 3px 5px 3px 0; font-weight: 500;
}
.chip-hot { background: var(--primary-container); color: #0284c7; font-weight: 600; }
.insight-box {
    background: var(--surface-container); border-radius: var(--radius-lg);
    padding: 20px 22px; box-shadow: var(--elevation-sm);
}
.insight-box h4 { margin: 0 0 10px; font-size: 0.95rem; color: #0284c7; font-weight: 600; }
.brief-box {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.08), #ffffff);
    border-radius: var(--radius-lg); padding: 22px 26px; margin-bottom: 16px;
    line-height: 1.65; box-shadow: var(--elevation-sm);
}
.footer-note { font-size: 0.73rem; text-align: center; opacity: 0.55; margin-top: 16px; }
.empty-state { text-align: center; padding: 48px 16px; color: var(--on-surface-variant); }
.empty-state .icon { font-size: 2.5rem; margin-bottom: 8px; }

.data-table-wrap {
    width: 100%; max-height: 460px; overflow: auto;
    border-radius: var(--radius-lg); background: #ffffff;
    box-shadow: var(--elevation-sm);
}
.data-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; color: #0f172a; }
.data-table thead th {
    position: sticky; top: 0; z-index: 1; background: #f1f5f9;
    color: #0f172a; font-weight: 600; text-align: left;
    padding: 12px 14px; border-bottom: 1px solid #e2e8f0; white-space: nowrap;
}
.data-table tbody td {
    padding: 12px 14px; border-bottom: 1px solid #f1f5f9;
    vertical-align: top; color: #0f172a; background: #ffffff;
}
.data-table tbody tr:hover td { background: #f8fafc; }
.data-table a { color: #0284c7 !important; text-decoration: none; font-weight: 600; }

/* App Footer (object_eraser.py 스타일 + MD3 라이트 톤) */
.app-footer-wrap {
    margin-top: 32px;
    padding-top: 16px;
    border-top: 1px solid #e2e8f0;
}
.footer-meta-text {
    font-size: 0.82rem;
    color: #64748b;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    height: 36px;
    white-space: nowrap;
}
.footer-blog-wrap {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    height: 36px;
}
.footer-blog-link {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    color: #0284c7 !important;
    text-decoration: none !important;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 8px;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    transition: all 0.18s ease;
    white-space: nowrap;
}
.footer-blog-link:hover {
    background: #e0f2fe;
    color: #0369a1 !important;
    transform: translateY(-1px);
}
[data-testid="stDialog"] div[role="dialog"],
div[role="dialog"] {
    background: #ffffff !important;
    color: #0f172a !important;
    width: min(900px, 92vw) !important;
    max-width: 900px !important;
}
div[role="dialog"] h1, div[role="dialog"] h2, div[role="dialog"] h3, div[role="dialog"] p {
    color: #0f172a !important;
}
.terms-rule-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    font-size: 0.86rem;
    line-height: 1.55;
    color: #475569;
}
.terms-rule-box b { color: #0f172a; }
.oss-table {
    width: 100%; border-collapse: collapse; font-size: 0.82rem; margin-top: 8px;
}
.oss-table th, .oss-table td {
    padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: left;
}
.oss-table th { color: #0284c7; font-weight: 700; }
.oss-table td { color: #334155; }
</style>
"""

# ═══════════════════════════════════════════════════════════
#  PRESS DOMAIN MAP (originallink 기반 실제 언론사 매핑)
# ═══════════════════════════════════════════════════════════
PRESS_MAP = {
    "yna.co.kr": "연합뉴스", "yonhapnewstv.co.kr": "연합뉴스TV",
    "newsis.com": "뉴시스", "news1.kr": "뉴스1",
    "chosun.com": "조선일보", "biz.chosun.com": "조선비즈",
    "joongang.co.kr": "중앙일보", "donga.com": "동아일보",
    "hani.co.kr": "한겨레", "khan.co.kr": "경향신문",
    "hankookilbo.com": "한국일보", "seoul.co.kr": "서울신문",
    "kmib.co.kr": "국민일보", "munhwa.com": "문화일보",
    "segye.com": "세계일보", "hankyung.com": "한국경제",
    "mk.co.kr": "매일경제", "sedaily.com": "서울경제",
    "mt.co.kr": "머니투데이", "edaily.co.kr": "이데일리",
    "fnnews.com": "파이낸셜뉴스", "heraldcorp.com": "헤럴드경제",
    "asiae.co.kr": "아시아경제", "ajunews.com": "아주경제",
    "etnews.com": "전자신문", "zdnet.co.kr": "ZDNet",
    "dt.co.kr": "디지털타임스", "inews24.com": "아이뉴스24",
    "bloter.net": "블로터", "aitimes.com": "AI타임스",
    "kbs.co.kr": "KBS", "imbc.com": "MBC", "sbs.co.kr": "SBS",
    "jtbc.co.kr": "JTBC", "ytn.co.kr": "YTN", "mbn.co.kr": "MBN",
    "tvchosun.com": "TV조선", "ichannela.com": "채널A",
    "nocutnews.co.kr": "노컷뉴스", "ohmynews.com": "오마이뉴스",
    "pressian.com": "프레시안", "mediatoday.co.kr": "미디어오늘",
    "sportschosun.com": "스포츠조선", "osen.co.kr": "OSEN",
    "xportsnews.com": "엑스포츠뉴스", "starnewskorea.com": "스타뉴스",
    "tenasia.hankyung.com": "텐아시아", "mydaily.co.kr": "마이데일리",
    "dispatch.co.kr": "디스패치", "newsen.com": "뉴스엔",
}

def extract_press_name(orig_url: str, fallback_url: str = "") -> str:
    url = orig_url if isinstance(orig_url, str) and orig_url.strip() else fallback_url
    try:
        host = urllib.parse.urlparse(url).netloc.lower()
        host = re.sub(r"^(www\.|m\.|news\.|n\.news\.)", "", host)
        if not host:
            return "기타"
        for dom, name in PRESS_MAP.items():
            if host == dom or host.endswith("." + dom):
                return name
        return host
    except Exception:
        return "기타"

# ═══════════════════════════════════════════════════════════
#  NLP: KEYWORD EXTRACTION, SENTIMENT & CLUSTERING
# ═══════════════════════════════════════════════════════════
_STOPWORDS = {
    "있는", "있다", "하는", "하다", "위해", "통해", "대한", "관련", "이번", "지난",
    "오늘", "내일", "어제", "기자", "뉴스", "보도", "밝혔다", "전했다", "따르면",
    "것으로", "등", "및", "그", "이", "저", "것", "수", "등등", "에서", "으로",
    "이다", "합니다", "했습니다", "했다", "된다", "됐다", "같은", "다른", "모든",
    "가장", "더", "또", "또한", "그리고", "하지만", "그러나", "때문에", "대해",
    "이상", "이하", "이후", "이전", "현재", "최근", "올해", "지난해", "오전", "오후",
    "서울", "한국", "국내", "관계자", "예정", "계획", "가운데", "기준", "대비",
    "진행", "개최", "공개", "발표", "설명", "강조", "지적", "우려", "기대",
}

_KO_SUFFIX = re.compile(
    r"(에서는|으로는|에서도|으로도|부터는|까지는|이라고|이라는|에게는|한테는|"
    r"은|는|이|가|을|를|의|에|와|과|도|로|으로|에서|까지|부터|만|처럼|보다|라고|라며)$"
)

_POS_WORDS = {
    "상승", "급등", "호조", "성장", "최대", "최고", "신고가", "흑자", "돌파", "성공",
    "혁신", "호평", "수상", "확대", "개선", "회복", "강세", "기대", "긍정", "인기",
    "흥행", "호실적", "계약", "수주", "투자", "출시", "선도", "우승", "축하", "반등",
    "혜택", "지원", "협력", "달성", "신기록", "안정", "증가", "우수", "호황", "대박",
}
_NEG_WORDS = {
    "하락", "급락", "부진", "적자", "감소", "위기", "우려", "논란", "비판", "갈등",
    "충돌", "피해", "사고", "화재", "폭락", "약세", "손실", "파산", "부정", "반발",
    "중단", "지연", "철회", "취소", "해킹", "유출", "사기", "혐의", "구속", "기소",
    "조사", "압수수색", "제재", "파업", "리콜", "결함", "불만", "침체", "악화", "경고",
}

def clean_html_text(s: str) -> str:
    if not isinstance(s, str):
        return ""
    s = re.sub(r"</?b>", "", s)
    return html.unescape(s).strip()

def tokenize_text(text: str):
    if not isinstance(text, str):
        return []
    tokens = []
    # 한글 2자 이상 + 영문/숫자 조합 2자 이상 (AI, GPT, 5G 등)
    for w in re.findall(r"[가-힣]{2,}|[A-Za-z][A-Za-z0-9\+\-]{1,}", text):
        if re.match(r"^[A-Za-z]", w):
            w_norm = w.upper() if len(w) <= 4 else w
            if len(w_norm) >= 2 and w_norm.lower() not in {"the", "and", "for", "with", "from", "this", "that"}:
                tokens.append(w_norm)
        else:
            stem = _KO_SUFFIX.sub("", w)
            if len(stem) >= 2 and stem not in _STOPWORDS:
                tokens.append(stem)
    return tokens

def extract_keywords(texts, query: str = "", top_n: int = 18):
    q_tokens = set(tokenize_text(query))
    bag = []
    for t in texts:
        for tok in tokenize_text(t):
            if tok not in q_tokens:
                bag.append(tok)
    return Counter(bag).most_common(top_n)

def analyze_sentiment(text: str):
    if not isinstance(text, str):
        return "중립", 0
    pos_cnt = sum(1 for w in _POS_WORDS if w in text)
    neg_cnt = sum(1 for w in _NEG_WORDS if w in text)
    score = pos_cnt - neg_cnt
    if score > 0:
        return "긍정", score
    elif score < 0:
        return "부정", score
    return "중립", 0

def cluster_similar_articles(df: pd.DataFrame, threshold: float = 0.45) -> pd.DataFrame:
    """제목 토큰 Jaccard 유사도 기반으로 중복/유사 기사를 대표 기사 아래 묶음"""
    if df.empty:
        return df
    token_sets = [set(tokenize_text(t)) for t in df["clean_title"].fillna("")]
    n = len(df)
    visited = [False] * n
    cluster_id = [-1] * n
    is_rep = [False] * n
    cluster_sizes = {}
    cid = 0

    for i in range(n):
        if visited[i]:
            continue
        visited[i] = True
        cluster_id[i] = cid
        is_rep[i] = True
        members = [i]
        si = token_sets[i]
        if si:
            for j in range(i + 1, n):
                if visited[j]:
                    continue
                sj = token_sets[j]
                if not sj:
                    continue
                inter = len(si & sj)
                union = len(si | sj)
                if union > 0 and (inter / union) >= threshold:
                    visited[j] = True
                    cluster_id[j] = cid
                    members.append(j)
        cluster_sizes[cid] = len(members)
        cid += 1

    out = df.copy()
    out["cluster_id"] = cluster_id
    out["is_cluster_rep"] = is_rep
    out["cluster_size"] = [cluster_sizes[c] for c in cluster_id]
    return out

# ═══════════════════════════════════════════════════════════
#  API CLIENT (Pagination up to 500+, originallink support)
# ═══════════════════════════════════════════════════════════
class NaverNewsAPIClient:
    def __init__(self):
        self.client_id = os.environ.get("CLIENT_ID", "")
        self.client_secret = os.environ.get("CLIENT_SECRET", "")

    def _headers(self):
        return {
            "X-NCP-APIGW-API-KEY-ID": self.client_id,
            "X-NCP-APIGW-API-KEY": self.client_secret,
        }

    def _fetch_page(self, query: str, display: int, start: int, sort: str):
        url = (
            "https://naverapihub.apigw.ntruss.com/search/v1/news?"
            + urllib.parse.urlencode(
                {"query": query, "display": display, "start": start, "sort": sort}
            )
        )
        req = urllib.request.Request(url, headers=self._headers())
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.getcode() == 200:
                return json.loads(resp.read().decode("utf-8"))
        return {}

    def search_news(self, query: str, count: int = 100, sort: str = "sim"):
        all_items = []
        total = 0
        remaining = min(max(count, 10), 1000)
        start = 1

        try:
            while remaining > 0 and start <= 1000:
                batch = min(remaining, 100)
                data = self._fetch_page(query, batch, start, sort)
                if not data:
                    break
                total = data.get("total", total)
                items = data.get("items", [])
                if not items:
                    break
                all_items.extend(items)
                if len(items) < batch:
                    break
                remaining -= len(items)
                start += batch
        except urllib.error.HTTPError as e:
            msgs = {
                401: "인증 실패 (401): .env의 CLIENT_ID / CLIENT_SECRET을 확인하세요.",
                403: "권한 오류 (403): NCP API Gateway 권한을 확인하세요.",
                404: "엔드포인트 오류 (404): 요청 URL을 확인하세요.",
                429: "호출 한도 초과 (429): 잠시 후 다시 시도하세요.",
            }
            st.error(f"❌ {msgs.get(e.code, f'API 오류: HTTP {e.code}')}")
            return pd.DataFrame(), 0
        except Exception as e:
            st.error(f"❌ 검색 실패: {e}")
            return pd.DataFrame(), 0

        if not all_items:
            return pd.DataFrame(), total

        df = pd.DataFrame(all_items)
        df["clean_title"] = df["title"].apply(clean_html_text)
        df["clean_desc"] = df["description"].apply(clean_html_text)
        if "originallink" not in df.columns:
            df["originallink"] = df["link"]
        df["press"] = [
            extract_press_name(o, l)
            for o, l in zip(df["originallink"], df["link"])
        ]
        df["date_parsed"] = pd.to_datetime(df["pubDate"], errors="coerce")
        df["hour"] = df["date_parsed"].dt.hour
        df["day"] = df["date_parsed"].dt.date

        sent_res = [
            analyze_sentiment(f"{t} {d}")
            for t, d in zip(df["clean_title"], df["clean_desc"])
        ]
        df["sentiment"] = [r[0] for r in sent_res]
        df["sentiment_score"] = [r[1] for r in sent_res]

        df = cluster_similar_articles(df, threshold=0.45)
        return df, total

def _env_mtime():
    try:
        return str(_ENV_PATH.stat().st_mtime)
    except Exception:
        return "0"

@st.cache_data(ttl=300, show_spinner=False)
def run_news_search(query: str, count: int, sort: str, _env_ts: str = ""):
    return NaverNewsAPIClient().search_news(query, count, sort)

def relative_time(dt) -> str:
    if pd.isna(dt):
        return ""
    now = datetime.now()
    try:
        dt_naive = dt.to_pydatetime().replace(tzinfo=None) if hasattr(dt, "to_pydatetime") else dt
        secs = (now - dt_naive).total_seconds()
    except Exception:
        return str(dt)[:16]
    if secs < 60:
        return "방금 전"
    if secs < 3600:
        return f"{int(secs // 60)}분 전"
    if secs < 86400:
        return f"{int(secs // 3600)}시간 전"
    if secs < 86400 * 7:
        return f"{int(secs // 86400)}일 전"
    return dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt)[:10]

def _esc(s) -> str:
    return html.escape(str(s), quote=True)

# ═══════════════════════════════════════════════════════════
#  AI BRIEFING & Q&A (Gemini API + Heuristic Fallback)
# ═══════════════════════════════════════════════════════════
def generate_heuristic_briefing(df: pd.DataFrame, query: str, total: int, keywords):
    n = len(df)
    pos_pct = (df["sentiment"] == "긍정").mean() * 100 if n else 0
    neg_pct = (df["sentiment"] == "부정").mean() * 100 if n else 0
    top_press = df["press"].value_counts().head(3).index.tolist() if "press" in df.columns else []
    top_kws = [w for w, _ in keywords[:6]]
    reps = df[df["is_cluster_rep"]].head(3) if "is_cluster_rep" in df.columns else df.head(3)

    tone = "긍정 우세" if pos_pct > neg_pct + 8 else ("부정 우세" if neg_pct > pos_pct + 8 else "중립/혼조")
    lines = [
        f"### 📌 «{query}» 자동 요약 브리핑",
        f"- **보도 규모**: 전체 {total:,}건 중 상위 **{n}건** 분석 (중복 제거 후 고유 이슈 **{int(df['is_cluster_rep'].sum())}건**)",
        f"- **여론 톤**: **{tone}** (긍정 {pos_pct:.1f}% · 부정 {neg_pct:.1f}% · 중립 {100 - pos_pct - neg_pct:.1f}%)",
        f"- **핵심 키워드**: {', '.join(f'`{k}`' for k in top_kws) if top_kws else '—'}",
        f"- **주요 보도 매체**: {', '.join(top_press) if top_press else '—'}",
        "",
        "#### 🗞️ 대표 헤드라인 TOP 3",
    ]
    for idx, (_, r) in enumerate(reps.iterrows(), 1):
        extra = f" *(유사 기사 +{int(r['cluster_size']) - 1}건)*" if r.get("cluster_size", 1) > 1 else ""
        lines.append(f"{idx}. **[{r['press']}]** {r['clean_title']}{extra}")
    return "\n".join(lines)

def generate_heuristic_briefing_html(df: pd.DataFrame, query: str, total: int, keywords) -> str:
    n = len(df)
    pos_pct = (df["sentiment"] == "긍정").mean() * 100 if n else 0
    neg_pct = (df["sentiment"] == "부정").mean() * 100 if n else 0
    neu_pct = max(0.0, 100 - pos_pct - neg_pct)
    top_press = df["press"].value_counts().head(3).index.tolist() if "press" in df.columns else []
    top_kws = [w for w, _ in keywords[:6]]
    reps = df[df["is_cluster_rep"]].head(3) if "is_cluster_rep" in df.columns else df.head(3)
    unique_cnt = int(df["is_cluster_rep"].sum()) if "is_cluster_rep" in df.columns else n

    tone = "긍정 우세" if pos_pct > neg_pct + 8 else ("부정 우세" if neg_pct > pos_pct + 8 else "중립/혼조")
    kw_html = " ".join(f'<span class="chip chip-hot">{_esc(k)}</span>' for k in top_kws) if top_kws else "—"
    press_str = ", ".join(_esc(p) for p in top_press) if top_press else "—"

    headline_items = []
    for idx, (_, r) in enumerate(reps.iterrows(), 1):
        extra = f' <span class="badge badge-cluster">유사 기사 +{int(r["cluster_size"]) - 1}건</span>' if r.get("cluster_size", 1) > 1 else ""
        headline_items.append(
            f'<li style="margin-bottom:8px;"><strong>[{_esc(r["press"])}]</strong> {_esc(r["clean_title"])}{extra}</li>'
        )

    return (
        f'<div class="brief-box">'
        f'<h3 style="margin:0 0 12px 0; font-size:1.15rem; font-weight:700;">{_esc(query)} 자동 요약 브리핑</h3>'
        f'<ul style="margin:0 0 16px 0; padding-left:20px; line-height:1.8;">'
        f'<li><strong>보도 규모:</strong> 전체 <strong>{total:,}건</strong> 중 상위 <strong>{n}건</strong> 분석 (중복 제거 후 고유 이슈 <strong>{unique_cnt}건</strong>)</li>'
        f'<li><strong>여론 톤:</strong> <strong>{tone}</strong> (긍정 {pos_pct:.1f}% · 부정 {neg_pct:.1f}% · 중립 {neu_pct:.1f}%)</li>'
        f'<li><strong>핵심 키워드:</strong> {kw_html}</li>'
        f'<li><strong>주요 보도 매체:</strong> <strong>{press_str}</strong></li>'
        f'</ul>'
        f'<h4 style="margin:0 0 10px 0; font-size:1rem; font-weight:700;">대표 헤드라인 TOP 3</h4>'
        f'<ol style="margin:0; padding-left:20px; line-height:1.7;">{"".join(headline_items)}</ol>'
        f'</div>'
    )

def build_markdown_report(df: pd.DataFrame, query: str, total: int, keywords, ai_brief: str = "") -> str:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    md = [
        f"# 뉴스 인텔리전스 리포트: {query}",
        f"- 생성 시각: {now_str}",
        f"- 전체 검색 결과: {total:,}건 / 분석 기사: {len(df)}건",
        "",
    ]
    if ai_brief:
        md.extend(["## AI 브리핑", ai_brief, ""])
    else:
        md.append(generate_heuristic_briefing(df, query, total, keywords))
        md.append("")
    md.append("## 주요 기사 목록")
    for i, (_, r) in enumerate(df.head(30).iterrows(), 1):
        md.append(f"{i}. [{r['clean_title']}]({r['originallink'] or r['link']}) — {r['press']} ({r['sentiment']}, {r['pubDate']})")
    return "\n".join(md)

# ═══════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════
def init_session():
    defaults = {
        "theme": "light",
        "news_df": pd.DataFrame(),
        "last_searched": "",
        "total_count": 0,
        "search_query_val": "AI 반도체",
        "search_history": [],
        "watchlist": ["AI 반도체", "삼성전자", "환율", "코스피"],
        "bookmarks": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()
st.markdown(DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        "<div class='sidebar-brand'><h2>⚡ NewsPulse</h2>"
        "<p>Naver News Intelligence Dashboard</p></div>",
        unsafe_allow_html=True,
    )

    toggle_text = "☀️ 라이트 모드" if st.session_state.theme == "dark" else "🌙 다크 모드"
    if st.button(toggle_text, key="theme_toggle", width="stretch"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.markdown("<div class='section-label'>검색 설정</div>", unsafe_allow_html=True)
    with st.form(key="search_form"):
        search_input = st.text_input(
            "검색어",
            value=st.session_state.search_query_val,
            placeholder="예) AI 반도체, 삼성전자, 금리 …",
            label_visibility="collapsed",
        )
        display_count = st.select_slider(
            "수집 기사 수 (페이징 자동 수집)",
            options=[20, 50, 100, 200, 300, 500],
            value=100,
        )
        sort_map = {"정확도순": "sim", "최신순": "date"}
        sort_label = st.selectbox("정렬 기준", list(sort_map.keys()))
        search_btn = st.form_submit_button("🔍 검색 및 분석 실행", width="stretch")

    # ── 워치리스트 (관심 키워드 모니터링) ────────────────────
    st.markdown("<div class='section-label'>워치리스트</div>", unsafe_allow_html=True)
    wl_cols = st.columns(2)
    for idx, kw in enumerate(st.session_state.watchlist):
        with wl_cols[idx % 2]:
            if st.button(f"📌 {kw}", key=f"wl_{kw}", width="stretch"):
                st.session_state.search_query_val = kw
                with st.spinner(f"'{kw}' 수집 중…"):
                    df_new, tot_new = run_news_search(kw, display_count, sort_map[sort_label], _env_mtime())
                    st.session_state.news_df = df_new
                    st.session_state.total_count = tot_new
                    st.session_state.last_searched = kw
                    st.session_state.ai_briefing = ""
                st.rerun()

    with st.expander("➕ 워치리스트 편집"):
        new_wl = st.text_input("추가할 키워드", key="new_wl_input", placeholder="키워드 입력")
        c_add, c_del = st.columns(2)
        if c_add.button("추가", key="wl_add_btn", width="stretch") and new_wl.strip():
            if new_wl.strip() not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_wl.strip())
                st.rerun()
        if st.session_state.watchlist:
            del_target = st.selectbox("삭제할 키워드", st.session_state.watchlist, key="wl_del_sel")
            if c_del.button("삭제", key="wl_del_btn", width="stretch"):
                st.session_state.watchlist.remove(del_target)
                st.rerun()

    # ── 최근 검색 ───────────────────────────────────────────
    if st.session_state.search_history:
        st.markdown("<div class='section-label'>최근 검색</div>", unsafe_allow_html=True)
        for h in st.session_state.search_history[-3:][::-1]:
            if st.button(f"↺ {h}", key=f"hist_{h}", width="stretch"):
                st.session_state.search_query_val = h
                with st.spinner(f"'{h}' 검색 중…"):
                    df_new, tot_new = run_news_search(h, display_count, sort_map[sort_label], _env_mtime())
                    st.session_state.news_df = df_new
                    st.session_state.total_count = tot_new
                    st.session_state.last_searched = h
                st.rerun()

    st.markdown(
        "<p class='footer-note'>NewsPulse · Naver Open API + Analytics<br>© 2026 PyLab</p>",
        unsafe_allow_html=True,
    )

# ── 검색 실행 ───────────────────────────────────────────────
if search_btn:
    q = search_input.strip()
    if not q:
        st.sidebar.warning("검색어를 입력하세요.")
    else:
        st.session_state.search_query_val = q
        with st.spinner(f"🔍 '{q}' 뉴스 {display_count}건 수집 및 분석 중…"):
            df_new, tot_new = run_news_search(q, display_count, sort_map[sort_label], _env_mtime())
            st.session_state.news_df = df_new
            st.session_state.total_count = tot_new
            st.session_state.last_searched = q
            st.session_state.ai_briefing = ""
            st.session_state.qa_history = []
            hist = st.session_state.search_history
            if q not in hist:
                hist.append(q)
                st.session_state.search_history = hist[-10:]

if st.session_state.news_df.empty and not st.session_state.last_searched:
    with st.spinner("초기 뉴스 데이터를 불러오는 중…"):
        df_init, tot_init = run_news_search(st.session_state.search_query_val, 100, "sim", _env_mtime())
        st.session_state.news_df = df_init
        st.session_state.total_count = tot_init
        st.session_state.last_searched = st.session_state.search_query_val

# ═══════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════
df = st.session_state.news_df
last_q = st.session_state.last_searched
total = st.session_state.total_count
is_dark = st.session_state.theme == "dark"

PLOT_BG = "#1e293b" if is_dark else "#ffffff"
PAPER_BG = "#0f172a" if is_dark else "#f8fafc"
FONT_CLR = "#f8fafc" if is_dark else "#0f172a"
GRID_CLR = "rgba(148,163,184,0.16)" if is_dark else "#e2e8f0"
ACCENT = "#38bdf8" if is_dark else "#0ea5e9"
ACCENT_2 = "#0ea5e9" if is_dark else "#0284c7"
POS_CLR = "#16a34a"
NEG_CLR = "#dc2626"
NEU_CLR = "#64748b"

st.markdown(
    f"<div class='hero'>"
    f"<h1>⚡ NewsPulse 뉴스 인텔리전스</h1>"
    f"<p>키워드 <b style='color:{ACCENT}'>« {_esc(last_q or '—')} »</b> 실시간 수집 · "
    f"언론사 정밀 매핑 · 감성 분석 · 중복 클러스터링 · AI 브리핑</p>"
    f"</div>",
    unsafe_allow_html=True,
)

if df.empty:
    st.markdown(
        "<div class='empty-state'><div class='icon'>📭</div>"
        f"<p><b>'{_esc(last_q)}'</b> 검색 결과가 없습니다.<br>다른 검색어를 시도해 보세요.</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()

# ── 상단 KPI 5개 (MD3 Uniform Grid — 5개 박스 크기 완전 동일) ──
n_articles = len(df)
n_unique = int(df["is_cluster_rep"].sum()) if "is_cluster_rep" in df.columns else n_articles
n_press = df["press"].nunique() if "press" in df.columns else 0
top_press_name = df["press"].value_counts().index[0] if "press" in df.columns and not df.empty else "—"
pos_ratio = (df["sentiment"] == "긍정").mean() * 100
neg_ratio = (df["sentiment"] == "부정").mean() * 100
latest_dt = df["date_parsed"].max() if "date_parsed" in df.columns else None
latest_label = relative_time(latest_dt) if latest_dt is not None else "—"
latest_time_str = latest_dt.strftime("%m/%d %H:%M") if pd.notna(latest_dt) and hasattr(latest_dt, "strftime") else "실시간"

kpi_html = (
    '<div class="kpi-grid">'
    f'<div class="kpi-card"><div class="kpi-label">수집 / 전체 결과</div><div class="kpi-value">{n_articles:,}건</div><div class="kpi-sub">전체 {total:,}건</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">고유 이슈 (중복 제거)</div><div class="kpi-value">{n_unique:,}건</div><div class="kpi-sub kpi-sub-pos">중복 {n_articles - n_unique}건 묶음</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">보도 언론사</div><div class="kpi-value">{n_press}개사</div><div class="kpi-sub">최다 {_esc(top_press_name)}</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">여론 감성 (긍정/부정)</div><div class="kpi-value">{pos_ratio:.0f}% / {neg_ratio:.0f}%</div><div class="kpi-sub kpi-sub-pos">중립 {max(0.0, 100 - pos_ratio - neg_ratio):.0f}%</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">최신 기사</div><div class="kpi-value">{_esc(latest_label)}</div><div class="kpi-sub kpi-sub-neu">{_esc(latest_time_str)} 기준</div></div>'
    '</div>'
)
st.markdown(kpi_html, unsafe_allow_html=True)

# 키워드 사전 추출 (여러 탭에서 공유)
all_texts = df["clean_title"].fillna("").tolist() + df["clean_desc"].fillna("").tolist()
keywords = extract_keywords(all_texts, query=last_q, top_n=18)

tabs = st.tabs([
    "📰 뉴스 피드",
    "📊 심층 인사이트",
    "📌 이슈 브리핑",
    "⚖️ 키워드 비교",
    "⭐ 스크랩 & 리포트",
])

# ═══════════════════════════════════════════════════════════
#  TAB 1: 뉴스 피드 (날짜/감성/언론사 필터 + 중복 제거 + 스크랩)
# ═══════════════════════════════════════════════════════════
with tabs[0]:
    f1, f2, f3, f4 = st.columns([1.4, 1.1, 1.3, 1.0])
    with f1:
        press_list = ["전체"] + sorted(df["press"].dropna().unique().tolist())
        press_filter = st.selectbox("언론사", press_list, key="press_filter")
    with f2:
        sent_filter = st.selectbox("감성", ["전체", "긍정", "중립", "부정"], key="sent_filter")
    with f3:
        kw_filter = st.text_input("피드 내 검색", placeholder="제목/요약 키워드…", key="kw_filter")
    with f4:
        dedup_on = st.toggle("유사 기사 묶기", value=True, key="dedup_toggle")

    valid_dates = df["day"].dropna()
    date_range = None
    if not valid_dates.empty and valid_dates.min() < valid_dates.max():
        date_range = st.date_input(
            "발행일 범위 필터",
            value=(valid_dates.min(), valid_dates.max()),
            min_value=valid_dates.min(),
            max_value=valid_dates.max(),
            key="date_range_filter",
        )

    view = df.copy()
    if dedup_on and "is_cluster_rep" in view.columns:
        view = view[view["is_cluster_rep"]]
    if press_filter != "전체":
        view = view[view["press"] == press_filter]
    if sent_filter != "전체":
        view = view[view["sentiment"] == sent_filter]
    if kw_filter.strip():
        kw = kw_filter.strip()
        mask = view["clean_title"].str.contains(kw, case=False, na=False) | view["clean_desc"].str.contains(kw, case=False, na=False)
        view = view[mask]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        d_start, d_end = date_range
        view = view[view["day"].notna() & (view["day"] >= d_start) & (view["day"] <= d_end)]

    st.markdown(f"<div class='section-label'>실시간 뉴스 피드 · {len(view)}건</div>", unsafe_allow_html=True)

    if view.empty:
        st.info("필터 조건에 맞는 기사가 없습니다.")
    else:
        bm_links = {b["link"] for b in st.session_state.bookmarks}
        for idx, row in view.head(60).iterrows():
            title = _esc(row.get("clean_title", ""))
            desc = _esc(row.get("clean_desc", ""))
            link = row.get("link", "#")
            orig_link = row.get("originallink") or link
            press = _esc(row.get("press", "기타"))
            rel = relative_time(row.get("date_parsed"))
            sent = row.get("sentiment", "중립")
            c_size = int(row.get("cluster_size", 1))

            sent_cls = "badge-pos" if sent == "긍정" else ("badge-neg" if sent == "부정" else "badge-neutral")
            cluster_html = f"<span class='badge badge-cluster'>유사 기사 +{c_size - 1}</span>" if (dedup_on and c_size > 1) else ""

            c_card, c_bm = st.columns([11, 1.3])
            with c_card:
                card_html = (
                    f'<div class="news-card">'
                    f'<div class="news-title"><a href="{_esc(orig_link)}" target="_blank" rel="noopener">{title}</a></div>'
                    f'<div class="news-desc">{desc}</div>'
                    f'<div class="news-meta">'
                    f'<span class="badge badge-accent">{press}</span>'
                    f'<span class="badge {sent_cls}">{sent}</span>'
                    f'{cluster_html}'
                    f'<span>🕒 {_esc(rel or row.get("pubDate", ""))}</span>'
                    f'<a href="{_esc(orig_link)}" target="_blank" rel="noopener">언론사 원문 ↗</a>'
                    f'<a href="{_esc(link)}" target="_blank" rel="noopener">네이버 뉴스 ↗</a>'
                    f'</div></div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
            with c_bm:
                is_saved = link in bm_links
                btn_lbl = "★ 저장됨" if is_saved else "☆ 스크랩"
                if st.button(btn_lbl, key=f"bm_{idx}_{hash(link) % 100000}", width="stretch"):
                    if is_saved:
                        st.session_state.bookmarks = [b for b in st.session_state.bookmarks if b["link"] != link]
                    else:
                        st.session_state.bookmarks.append({
                            "title": row.get("clean_title", ""),
                            "desc": row.get("clean_desc", ""),
                            "press": row.get("press", ""),
                            "sentiment": sent,
                            "pubDate": row.get("pubDate", ""),
                            "link": link,
                            "originallink": orig_link,
                        })
                    st.rerun()

# ═══════════════════════════════════════════════════════════
#  TAB 2: 심층 인사이트 (키워드 + 언론사 + 감성 + 시간대 히트맵)
# ═══════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("<div class='section-label'>핵심 키워드 & 여론 감성</div>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1.25, 1])

    with col_l:
        st.markdown("##### 🔥 핵심 키워드 (한글 + 영문 통합)")
        if keywords:
            kw_df = pd.DataFrame(keywords[:15], columns=["키워드", "빈도"])
            fig_kw = px.bar(
                kw_df, x="빈도", y="키워드", orientation="h",
                color="빈도", color_continuous_scale=["#0c4a6e", ACCENT_2, ACCENT],
            )
            fig_kw.update_layout(
                plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR),
                height=370, margin=dict(l=10, r=10, t=15, b=10),
                yaxis=dict(categoryorder="total ascending", gridcolor=GRID_CLR),
                xaxis=dict(gridcolor=GRID_CLR),
                coloraxis_showscale=False, showlegend=False,
            )
            st.plotly_chart(fig_kw, width="stretch")

            chips = "".join(
                f'<span class="chip {"chip-hot" if i < 4 else ""}">{w} ({c})</span>'
                for i, (w, c) in enumerate(keywords[:14])
            )
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.caption("키워드를 추출할 수 없습니다.")

    with col_r:
        st.markdown("##### 🎭 여론 감성 분포")
        sent_counts = df["sentiment"].value_counts().reindex(["긍정", "중립", "부정"], fill_value=0).reset_index()
        sent_counts.columns = ["감성", "기사수"]
        fig_sent = px.pie(
            sent_counts, values="기사수", names="감성", hole=0.52,
            color="감성", color_discrete_map={"긍정": POS_CLR, "중립": NEU_CLR, "부정": NEG_CLR},
        )
        fig_sent.update_layout(
            plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR),
            height=250, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=-0.1),
        )
        fig_sent.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_sent, width="stretch")

        st.markdown("##### 🏛 주요 보도 언론사 TOP 8")
        press_df = df["press"].value_counts().head(8).reset_index()
        press_df.columns = ["언론사", "기사수"]
        fig_p = px.bar(press_df, x="기사수", y="언론사", orientation="h", color_discrete_sequence=[ACCENT_2])
        fig_p.update_layout(
            plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR),
            height=220, margin=dict(l=10, r=10, t=10, b=10),
            yaxis=dict(categoryorder="total ascending", gridcolor=GRID_CLR),
            xaxis=dict(gridcolor=GRID_CLR),
        )
        st.plotly_chart(fig_p, width="stretch")

    st.markdown("<div class='section-label'>시계열 보도량 & 시간대별 집중도</div>", unsafe_allow_html=True)
    t_col1, t_col2 = st.columns([1.3, 1])

    with t_col1:
        st.markdown("##### 📈 일별 보도량 추이 (스파이크 감지)")
        daily = (
            df.dropna(subset=["day"])
            .groupby("day").size().reset_index(name="기사수")
            .sort_values("day")
        )
        if not daily.empty:
            mean_v = daily["기사수"].mean()
            std_v = daily["기사수"].std() if len(daily) > 1 else 0
            spike_th = mean_v + std_v
            colors = [NEG_CLR if (v > spike_th and std_v > 0) else ACCENT for v in daily["기사수"]]

            fig_d = go.Figure()
            fig_d.add_trace(go.Scatter(
                x=daily["day"], y=daily["기사수"], mode="lines+markers",
                line=dict(color=ACCENT, width=2.5),
                marker=dict(size=9, color=colors),
                fill="tozeroy", fillcolor="rgba(56,189,248,0.14)",
                name="일별 기사 수",
            ))
            fig_d.update_layout(
                plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR),
                height=280, margin=dict(l=10, r=10, t=15, b=10),
                xaxis=dict(gridcolor=GRID_CLR, title=""),
                yaxis=dict(gridcolor=GRID_CLR, title="기사 수"),
            )
            st.plotly_chart(fig_d, width="stretch")
        else:
            st.caption("날짜 데이터가 부족합니다.")

    with t_col2:
        st.markdown("##### ⏰ 시간대별 보도 집중도 (0~23시)")
        hourly = df.dropna(subset=["hour"]).groupby("hour").size().reindex(range(24), fill_value=0).reset_index()
        hourly.columns = ["시간", "기사수"]
        fig_h = px.bar(
            hourly, x="시간", y="기사수",
            color="기사수", color_continuous_scale=["#1e293b", ACCENT, ACCENT_2],
        )
        fig_h.update_layout(
            plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR),
            height=280, margin=dict(l=10, r=10, t=15, b=10),
            xaxis=dict(tickmode="linear", dtick=3, gridcolor=GRID_CLR, title="시(Hour)"),
            yaxis=dict(gridcolor=GRID_CLR, title="기사 수"),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_h, width="stretch")

# ═══════════════════════════════════════════════════════════
#  TAB 3: 이슈 브리핑
# ═══════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("<div class='section-label'>실시간 이슈 브리핑</div>", unsafe_allow_html=True)

    auto_brief_html = generate_heuristic_briefing_html(df, last_q, total, keywords)
    st.markdown(auto_brief_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  TAB 4: 멀티 키워드 비교
# ═══════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("<div class='section-label'>멀티 키워드 보도량 · 여론 비교</div>", unsafe_allow_html=True)
    top_related_kw = next((w for w, _ in keywords if w.lower() != last_q.lower()), "")
    default_comp_val = f"{last_q}, {top_related_kw}" if top_related_kw else last_q
    comp_input = st.text_input(
        "비교할 키워드를 쉼표(,)로 구분해 입력하세요 (최대 4개)",
        value=default_comp_val,
        key=f"comp_input_{last_q}",
        help="현재 검색어와 수집된 기사에서 가장 많이 언급된 핵심 키워드 1개가 자동으로 입력됩니다.",
    )
    if st.button("⚖️ 비교 분석 실행", key="comp_run"):
        kws = [k.strip() for k in comp_input.split(",") if k.strip()][:4]
        if len(kws) < 2:
            st.warning("최소 2개 이상의 키워드를 입력하세요.")
        else:
            comp_rows = []
            trend_frames = []
            with st.spinner("키워드별 뉴스 수집 및 비교 분석 중…"):
                for kw in kws:
                    cdf, ctot = run_news_search(kw, 100, "date", _env_mtime())
                    if not cdf.empty:
                        pos_p = (cdf["sentiment"] == "긍정").mean() * 100
                        neg_p = (cdf["sentiment"] == "부정").mean() * 100
                        neu_p = 100 - pos_p - neg_p
                        comp_rows.append({
                            "키워드": kw, "전체 검색량": ctot, "수집 건수": len(cdf),
                            "긍정(%)": round(pos_p, 1), "중립(%)": round(neu_p, 1), "부정(%)": round(neg_p, 1),
                            "최다 매체": cdf["press"].value_counts().index[0],
                        })
                        d_cnt = cdf.dropna(subset=["day"]).groupby("day").size().reset_index(name="기사수")
                        d_cnt["키워드"] = kw
                        trend_frames.append(d_cnt)

            if comp_rows:
                comp_df = pd.DataFrame(comp_rows)
                st.dataframe(comp_df, width="stretch", hide_index=True)

                cc1, cc2 = st.columns(2)
                with cc1:
                    fig_tot = px.bar(
                        comp_df, x="키워드", y="전체 검색량", color="키워드",
                        title="전체 뉴스 검색량 비교",
                        color_discrete_sequence=[ACCENT, ACCENT_2, POS_CLR, "#f59e0b"],
                    )
                    fig_tot.update_layout(
                        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR),
                        height=300, showlegend=False,
                    )
                    st.plotly_chart(fig_tot, width="stretch")

                with cc2:
                    sent_melt = comp_df.melt(
                        id_vars="키워드", value_vars=["긍정(%)", "중립(%)", "부정(%)"],
                        var_name="감성", value_name="비율",
                    )
                    fig_sm = px.bar(
                        sent_melt, x="키워드", y="비율", color="감성", barmode="stack",
                        title="키워드별 여론 감성 비교",
                        color_discrete_map={"긍정(%)": POS_CLR, "중립(%)": NEU_CLR, "부정(%)": NEG_CLR},
                    )
                    fig_sm.update_layout(
                        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR),
                        height=300,
                    )
                    st.plotly_chart(fig_sm, width="stretch")

                if trend_frames:
                    tr_all = pd.concat(trend_frames, ignore_index=True)
                    fig_tr = px.line(
                        tr_all, x="day", y="기사수", color="키워드", markers=True,
                        title="최근 일별 보도량 추이 비교",
                        color_discrete_sequence=[ACCENT, ACCENT_2, POS_CLR, "#f59e0b"],
                    )
                    fig_tr.update_layout(
                        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG, font=dict(color=FONT_CLR),
                        height=280, xaxis_title="", yaxis_title="기사 수",
                    )
                    st.plotly_chart(fig_tr, width="stretch")

# ═══════════════════════════════════════════════════════════
#  TAB 5: 스크랩 & 데이터 리포트
# ═══════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown(f"<div class='section-label'>스크랩한 기사 · {len(st.session_state.bookmarks)}건</div>", unsafe_allow_html=True)
    if st.session_state.bookmarks:
        for i, bm in enumerate(st.session_state.bookmarks):
            c1, c2 = st.columns([10, 1.2])
            c1.markdown(
                f"**{i+1}. [{bm['press']}]** [{_esc(bm['title'])}]({bm['originallink'] or bm['link']}) "
                f"· `{bm['sentiment']}` · {bm['pubDate']}"
            )
            if c2.button("삭제", key=f"del_bm_{i}", width="stretch"):
                st.session_state.bookmarks.pop(i)
                st.rerun()
    else:
        st.caption("뉴스 피드에서 ☆ 스크랩 버튼을 눌러 관심 기사를 저장할 수 있습니다.")

    st.markdown("<div class='section-label'>전체 수집 데이터 & 내보내기</div>", unsafe_allow_html=True)
    disp = df[["clean_title", "clean_desc", "press", "sentiment", "pubDate", "originallink"]].copy()
    disp.columns = ["제목", "요약", "언론사", "감성", "발행일", "원문링크"]

    rows_html = []
    for i, (_, row) in enumerate(disp.iterrows(), 1):
        rows_html.append(
            f"<tr>"
            f"<td>{i}</td>"
            f"<td><b>{_esc(row['제목'])}</b></td>"
            f"<td>{_esc(row['요약'])}</td>"
            f"<td>{_esc(row['언론사'])}</td>"
            f"<td>{_esc(row['감성'])}</td>"
            f"<td style='white-space:nowrap'>{_esc(row['발행일'])}</td>"
            f"<td style='white-space:nowrap'><a href='{_esc(row['원문링크'])}' target='_blank' rel='noopener'>열기 ↗</a></td>"
            f"</tr>"
        )
    st.markdown(
        f"<div class='data-table-wrap'><table class='data-table'>"
        f"<thead><tr><th>#</th><th>제목</th><th>요약</th><th>언론사</th><th>감성</th><th>발행일</th><th>링크</th></tr></thead>"
        f"<tbody>{''.join(rows_html)}</tbody></table></div>",
        unsafe_allow_html=True,
    )

    dl1, dl2 = st.columns([1, 1])
    csv_bytes = disp.to_csv(index=False).encode("utf-8-sig")
    md_report = build_markdown_report(df, last_q, total, keywords)
    ts_str = datetime.now().strftime("%Y%m%d_%H%M")
    dl1.download_button(
        "⬇️ CSV 데이터 다운로드", data=csv_bytes,
        file_name=f"newspulse_{last_q}_{ts_str}.csv", mime="text/csv", width="stretch",
    )
    dl2.download_button(
        "📝 Markdown 리포트 다운로드", data=md_report.encode("utf-8"),
        file_name=f"newspulse_report_{last_q}_{ts_str}.md", mime="text/markdown", width="stretch",
    )


# ═══════════════════════════════════════════════════════════
#  TERMS & OPEN SOURCE LICENSES DIALOG + FOOTER
# ═══════════════════════════════════════════════════════════
@st.dialog("📜 사용약관 및 오픈소스 라이선스", width="large")
def show_terms_dialog():
    terms_html = (
        '<div class="terms-rule-box"><b>제1조 (목적)</b><br>'
        '본 약관은 NewsPulse 뉴스 인텔리전스 대시보드(이하 "서비스")의 이용 조건 및 절차, 운영자와 이용자 간의 권리·의무 및 책임사항을 규정함을 목적으로 합니다.</div>'
        '<div class="terms-rule-box"><b>제2조 (서비스 내용 및 데이터 출처)</b><br>'
        '본 서비스는 네이버 검색 오픈 API(NCP API Gateway)를 통해 실시간 뉴스 메타데이터(제목, 요약, 링크, 발행일)를 수집·시각화합니다. 개별 기사의 저작권 및 내용에 대한 권리는 각 언론사 및 원저작권자에게 귀속됩니다.</div>'
        '<div class="terms-rule-box"><b>제3조 (이용자의 의무 및 저작권 준수)</b><br>'
        '이용자는 본 서비스를 통해 조회하거나 다운로드(CSV/Markdown)한 뉴스 데이터를 대한민국 저작권법 및 관련 법령이 허용하는 범위 내에서만 이용해야 하며, 무단 전재·재배포·상업적 도용으로 발생하는 민·형사상 책임은 전적으로 이용자 본인에게 있습니다.</div>'
        '<div class="terms-rule-box"><b>제4조 (자동 분석 결과 및 기술적 면책)</b><br>'
        '본 서비스가 제공하는 키워드 추출, 감성 분석, 유사 기사 클러스터링 및 요약 브리핑은 자동화된 참고 정보일 뿐이며, 정확성·완전성·투자 판단 등에 대해 보증하지 않습니다. 외부 API 장애 또는 호출 한도 초과로 인한 서비스 중단에 대해 운영자는 책임을 지지 않습니다.</div>'
        '<div class="terms-rule-box"><b>제5조 (개인정보 및 세션 데이터)</b><br>'
        '이용자의 검색 기록·스크랩 목록은 현재 브라우저 세션 메모리에만 임시 보관되며, 운영자의 외부 서버에 영구 저장되거나 제3자에게 제공되지 않습니다.</div>'
        '<div class="terms-rule-box"><b>📦 오픈소스 라이선스 고지 (Open Source Licenses)</b><br>'
        '본 서비스는 아래 오픈소스 소프트웨어 및 폰트를 기반으로 제작되었습니다.'
        '<table class="oss-table"><thead><tr><th>라이브러리 / 리소스</th><th>용도</th><th>라이선스</th></tr></thead><tbody>'
        '<tr><td><b>Python</b></td><td>런타임 환경</td><td>PSF License</td></tr>'
        '<tr><td><b>Streamlit</b></td><td>웹 대시보드 프레임워크</td><td>Apache License 2.0</td></tr>'
        '<tr><td><b>Pandas</b></td><td>데이터 정제 및 통계 분석</td><td>BSD 3-Clause License</td></tr>'
        '<tr><td><b>Plotly</b></td><td>인터랙티브 데이터 시각화</td><td>MIT License</td></tr>'
        '<tr><td><b>python-dotenv</b></td><td>환경 변수(.env) 관리</td><td>BSD 3-Clause License</td></tr>'
        '<tr><td><b>Pretendard / Noto Sans KR</b></td><td>다국어 웹 타이포그래피</td><td>SIL Open Font License 1.1</td></tr>'
        '</tbody></table></div>'
    )
    st.markdown(terms_html, unsafe_allow_html=True)
    if st.button("확인 (닫기)", key="close_terms_btn", width="stretch"):
        st.rerun()


st.markdown('<div class="app-footer-wrap"></div>', unsafe_allow_html=True)
ft_l, ft_c, ft_r = st.columns([4.6, 1.35, 3.2], vertical_alignment="center")
with ft_l:
    st.markdown(
        '<div class="footer-meta-text">Copyright © 2026 Kim Jeongman. All rights reserved. &nbsp;|&nbsp;</div>',
        unsafe_allow_html=True,
    )
with ft_c:
    if st.button("📜 사용약관", key="open_terms_footer_btn", width="stretch"):
        show_terms_dialog()
with ft_r:
    st.markdown(
        '<div class="footer-blog-wrap">&nbsp;|&nbsp;&nbsp;'
        '<a href="https://blog.naver.com/jungman3" target="_blank" rel="noopener noreferrer" class="footer-blog-link">'
        '📗 Naver Blog</a></div>',
        unsafe_allow_html=True,
    )
