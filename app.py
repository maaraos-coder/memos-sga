import os
import sqlite3
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
EXPORTS_DIR = BASE_DIR / "exports"
DB_PATH = DATA_DIR / "app.db"
LOGO_PATH = ASSETS_DIR / "logo_seremi_rm.png"
FUNCIONARIOS_CSV = DATA_DIR / "funcionarios.csv"
DESTINATARIOS_CSV = DATA_DIR / "destinatarios.csv"
USUARIOS_CSV = DATA_DIR / "usuarios.csv"

st.set_page_config(
    page_title="Gestión Documental SGA",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

AZUL = "#005EB8"
ROJO = "#EF3340"
GRIS_FONDO = "#F5F7FA"
GRIS_TEXTO = "#2C2C2C"

CHILE_TZ = ZoneInfo("America/Santiago")

def ahora_chile():
    return datetime.now(CHILE_TZ)


st.markdown(f"""
<style>
/* Base */
.stApp {{
    background: linear-gradient(180deg, #ffffff 0%, #f3f7fc 42%, #eef3f8 100%);
    color: #1f2937;
}}
header[data-testid="stHeader"] {{background: rgba(255,255,255,0.92);}}
.block-container {{
    padding-top: 1.6rem !important;
    padding-bottom: 2.2rem !important;
    max-width: 1100px !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #ffffff 0%, #edf4fb 100%);
    border-right: 1px solid #d8e4f0;
}}
section[data-testid="stSidebar"] * {{color: #17345d;}}
section[data-testid="stSidebar"] .stButton button {{width: 100%;}}

/* Header */
.hero-card {{
    background: #ffffff;
    border: 1px solid #d9e5f2;
    border-radius: 22px;
    box-shadow: 0 8px 26px rgba(0, 61, 122, 0.08);
    padding: 26px 30px 24px 30px;
    margin: 0 0 26px 0;
    position: relative;
    overflow: hidden;
}}
.hero-card:before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 7px;
    background: linear-gradient(90deg, {AZUL} 0%, {AZUL} 62%, {ROJO} 62%, {ROJO} 100%);
}}
.logo-wrap {{
    display:flex; align-items:center; justify-content:center;
    background:#fff; border-radius:14px; padding:8px;
    border: 1px solid #e6eef7;
}}
.logo-wrap img {{max-width: 310px !important; height:auto !important; display:block; margin:auto;}}
.main-title {{
    font-size: 2.25rem;
    line-height: 1.15;
    font-weight: 850;
    color: #003B7A;
    margin: 0 0 8px 0;
    letter-spacing: -0.02em;
}}
.sub-title {{font-size: 1.08rem; color: #536179; margin: 0; line-height: 1.55;}}
.badge {{
    display:inline-block; margin-top: 10px; padding: 6px 12px;
    border-radius: 999px; background:#eef5ff; color:#004a91;
    font-weight: 700; font-size: 0.90rem;
}}

/* Titles */
.section-title {{font-size: 1.55rem; font-weight: 850; color: #1f2937; margin: 10px 0 16px 0;}}
h1, h2, h3 {{color:#1f2937 !important; letter-spacing:-0.02em;}}

/* Cards */
.card {{
    background: white;
    border: 1px solid #d9e3f0;
    border-radius: 18px;
    padding: 24px 28px;
    box-shadow: 0 6px 18px rgba(0,61,122,0.06);
    min-height: 172px;
}}
.card-blue {{border-left: 8px solid {AZUL};}}
.card-red {{border-left: 8px solid {ROJO};}}
.card-label {{font-weight:800; color:#1f2937; font-size:1.02rem;}}
.big-number-blue {{font-size: 2.12rem; color: {AZUL}; font-weight: 900; line-height: 1.45;}}
.big-number-red {{font-size: 2.12rem; color: {ROJO}; font-weight: 900; line-height: 1.45;}}
.small-muted {{color:#60708a; font-size: 0.95rem;}}

.panel {{
    background:#ffffff;
    border: 1px solid #d9e3f0;
    border-radius: 18px;
    box-shadow: 0 6px 18px rgba(0,61,122,0.06);
    padding: 24px 28px 28px 28px;
    margin-top: 18px;
}}
.panel-top {{height: 6px; background: linear-gradient(90deg, {AZUL} 0%, {AZUL} 60%, {ROJO} 60%, {ROJO} 100%); border-radius:999px; margin: 22px 0 14px 0;}}
.footer-line {{height: 5px; background: linear-gradient(90deg, {AZUL} 0%, {AZUL} 50%, {ROJO} 50%, {ROJO} 100%); margin: 30px 0 0 0; border-radius:999px;}}

/* Inputs & Buttons */
div.stButton > button:first-child, div.stFormSubmitButton > button {{
    background: linear-gradient(90deg, {AZUL}, #004a91) !important;
    color: white !important;
    border-radius: 12px !important;
    border: none !important;
    font-weight: 800 !important;
    padding: 0.65rem 1.25rem !important;
    box-shadow: 0 6px 14px rgba(0,94,184,0.18);
}}
div.stButton > button:first-child:hover, div.stFormSubmitButton > button:hover {{
    background: linear-gradient(90deg, #004a91, #003B7A) !important;
    color:white !important;
}}
.stRadio [role="radiogroup"] label:first-child span:nth-child(2) {{font-weight:700; color:{AZUL};}}
.stRadio [role="radiogroup"] label:nth-child(2) span:nth-child(2) {{font-weight:700; color:{ROJO};}}
input, textarea, div[data-baseweb="select"] {{border-radius: 10px !important;}}

/* Login/form readability */
div[data-testid="stForm"] label, div[data-testid="stForm"] p, div[data-testid="stWidgetLabel"] p {{
    color:#1f2937 !important;
    font-size: 1.02rem !important;
    font-weight: 750 !important;
}}
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {{
    background:#ffffff !important;
    color:#111827 !important;
    border:1.8px solid #b9c8dc !important;
    min-height: 46px !important;
    font-size: 1.02rem !important;
    box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border:2px solid {AZUL} !important;
}}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{
    color:#6b7280 !important;
}}
.panel h3, .panel .stSubheader {{
    color:#003B7A !important;
}}


/* Generated document result */
.result-card {{
    background: linear-gradient(135deg, #ffffff 0%, #eef7ff 100%);
    border: 2px solid #b8d7f5;
    border-left: 10px solid #005EB8;
    border-radius: 20px;
    box-shadow: 0 10px 24px rgba(0, 94, 184, 0.12);
    padding: 26px 30px;
    margin: 18px 0 12px 0;
}}
.result-ok {{
    display:inline-block;
    background:#dcfce7;
    color:#166534;
    font-weight:900;
    padding:7px 13px;
    border-radius:999px;
    margin-bottom:10px;
}}
.result-number {{
    font-size: 2.7rem;
    line-height:1.15;
    font-weight:950;
    color:#003B7A;
    letter-spacing:-0.03em;
}}
.result-meta {{
    margin-top:10px;
    color:#334155;
    font-size:1.05rem;
    font-weight:650;
}}
.result-time {{
    margin-top:8px;
    color:#005EB8;
    font-size:1.03rem;
    font-weight:750;
}}


/* Admin */
.admin-card {{
    background:#ffffff;
    border:1px solid #d9e3f0;
    border-radius:16px;
    padding:18px 20px;
    box-shadow:0 5px 14px rgba(0,61,122,0.05);
    min-height:105px;
}}
.admin-card-title {{font-weight:900; color:#003B7A; font-size:1.05rem; margin-bottom:7px;}}
.admin-card-text {{color:#334155; font-size:0.98rem; line-height:1.45;}}
.admin-help {{
    background:#eef5ff;
    border-left:6px solid #005EB8;
    border-radius:14px;
    padding:14px 16px;
    color:#1f2937;
    margin:10px 0 18px 0;
}}
.credential-box {{
    background:#f8fafc;
    border:1.8px dashed #005EB8;
    border-radius:14px;
    padding:16px 18px;
    margin:12px 0;
    color:#0f172a;
    font-size:1rem;
}}

/* Metrics */
div[data-testid="stMetric"] {{
    background:#ffffff; border:1px solid #dbe6f3; border-radius:16px;
    padding:16px 18px; box-shadow: 0 4px 12px rgba(0,61,122,0.05);
}}

@media (max-width: 900px) {{
    .block-container {{padding-left: 1rem !important; padding-right: 1rem !important;}}
    .main-title {{font-size: 1.62rem; text-align:center;}}
    .sub-title {{text-align:center;}}
    .logo-wrap img {{max-width: 170px !important;}}
    .card {{min-height:auto;}}
}}
</style>
""", unsafe_allow_html=True)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    EXPORTS_DIR.mkdir(exist_ok=True)
    conn = connect()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_documento TEXT NOT NULL,
            numero INTEGER NOT NULL,
            anio INTEGER NOT NULL,
            fecha_hora TEXT NOT NULL,
            seccion_origen TEXT NOT NULL,
            oficina_origen TEXT NOT NULL,
            funcionario TEXT NOT NULL,
            departamento_destino TEXT NOT NULL,
            jefatura_destino TEXT NOT NULL,
            destinatario_nombre TEXT NOT NULL,
            materia TEXT NOT NULL,
            usuario_login TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Emitido',
            UNIQUE(tipo_documento, numero, anio)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            rol TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            oficina TEXT,
            debe_cambiar_password INTEGER NOT NULL DEFAULT 0,
            activo INTEGER NOT NULL DEFAULT 1,
            fecha_creacion TEXT,
            ultimo_acceso TEXT
        )
    """)
    # Migración segura para bases creadas por versiones anteriores
    cols = [r[1] for r in cur.execute("PRAGMA table_info(usuarios)").fetchall()]
    for col, ddl in {
        "debe_cambiar_password": "ALTER TABLE usuarios ADD COLUMN debe_cambiar_password INTEGER NOT NULL DEFAULT 0",
        "activo": "ALTER TABLE usuarios ADD COLUMN activo INTEGER NOT NULL DEFAULT 1",
        "fecha_creacion": "ALTER TABLE usuarios ADD COLUMN fecha_creacion TEXT",
        "ultimo_acceso": "ALTER TABLE usuarios ADD COLUMN ultimo_acceso TEXT",
    }.items():
        if col not in cols:
            cur.execute(ddl)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS correlativos (
            tipo_documento TEXT NOT NULL,
            anio INTEGER NOT NULL,
            ultimo_numero INTEGER NOT NULL DEFAULT 0,
            actualizado_por TEXT,
            fecha_actualizacion TEXT,
            PRIMARY KEY(tipo_documento, anio)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            usuario TEXT NOT NULL,
            accion TEXT NOT NULL,
            detalle TEXT NOT NULL
        )
    """)
    conn.commit()
    cargar_usuarios_csv(conn)
    asegurar_correlativos(conn)
    conn.close()


def cargar_usuarios_csv(conn):
    if USUARIOS_CSV.exists():
        df = pd.read_csv(USUARIOS_CSV).fillna("")
        for _, r in df.iterrows():
            debe = int(r.get("debe_cambiar_password", 0) or 0) if str(r.get("debe_cambiar_password", "")).strip() else 0
            activo = int(r.get("activo", 1) or 1) if str(r.get("activo", "")).strip() else 1
            conn.execute(
                """INSERT OR IGNORE INTO usuarios(usuario,nombre,rol,password_hash,oficina,debe_cambiar_password,activo,fecha_creacion)
                   VALUES(?,?,?,?,?,?,?,?)""",
                (r["usuario"], r["nombre"], r["rol"], r["password_hash"], r.get("oficina", ""), debe, activo, ahora_chile().strftime("%Y-%m-%d %H:%M:%S")),
            )
        conn.commit()


def log_auditoria(conn, usuario, accion, detalle):
    conn.execute(
        "INSERT INTO auditoria(fecha_hora, usuario, accion, detalle) VALUES(?,?,?,?)",
        (ahora_chile().strftime("%Y-%m-%d %H:%M:%S"), usuario, accion, detalle),
    )


def asegurar_correlativos(conn):
    anio = ahora_chile().year
    for tipo in ["Memorándum", "Ordinario"]:
        row = conn.execute("SELECT MAX(numero) AS max_num FROM registros WHERE tipo_documento=? AND anio=?", (tipo, anio)).fetchone()
        max_num = int(row["max_num"] or 0)
        existe = conn.execute("SELECT ultimo_numero FROM correlativos WHERE tipo_documento=? AND anio=?", (tipo, anio)).fetchone()
        if existe is None:
            conn.execute(
                "INSERT INTO correlativos(tipo_documento, anio, ultimo_numero, actualizado_por, fecha_actualizacion) VALUES(?,?,?,?,?)",
                (tipo, anio, max_num, "sistema", ahora_chile().strftime("%Y-%m-%d %H:%M:%S")),
            )
        elif int(existe["ultimo_numero"] or 0) < max_num:
            conn.execute(
                "UPDATE correlativos SET ultimo_numero=?, actualizado_por=?, fecha_actualizacion=? WHERE tipo_documento=? AND anio=?",
                (max_num, "sistema", ahora_chile().strftime("%Y-%m-%d %H:%M:%S"), tipo, anio),
            )
    conn.commit()


def get_user(username: str):
    conn = connect()
    row = conn.execute("SELECT * FROM usuarios WHERE usuario=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate(username: str, password: str):
    user = get_user(username)
    if user and int(user.get("activo", 1)) == 1 and user["password_hash"] == hash_password(password):
        conn = connect()
        conn.execute("UPDATE usuarios SET ultimo_acceso=? WHERE usuario=?", (ahora_chile().strftime("%Y-%m-%d %H:%M:%S"), username))
        conn.commit(); conn.close()
        user["ultimo_acceso"] = ahora_chile().strftime("%Y-%m-%d %H:%M:%S")
        return user
    return None


def cambiar_password(usuario, nueva_password, debe_cambiar=0):
    conn = connect()
    conn.execute("UPDATE usuarios SET password_hash=?, debe_cambiar_password=? WHERE usuario=?", (hash_password(nueva_password), int(debe_cambiar), usuario))
    log_auditoria(conn, usuario, "Cambio de contraseña", "El usuario cambió o recibió una nueva contraseña.")
    conn.commit(); conn.close()


def password_valida(pw: str):
    if len(pw) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not any(c.isupper() for c in pw):
        return False, "La contraseña debe incluir al menos una mayúscula."
    if not any(c.islower() for c in pw):
        return False, "La contraseña debe incluir al menos una minúscula."
    if not any(c.isdigit() for c in pw):
        return False, "La contraseña debe incluir al menos un número."
    return True, "OK"


def read_funcionarios():
    df = pd.read_csv(FUNCIONARIOS_CSV).fillna("")
    return df[df["activo"].astype(str).str.upper().eq("SI")].copy()


def read_destinatarios():
    df = pd.read_csv(DESTINATARIOS_CSV).fillna("")
    # Compatibilidad: versiones antiguas usaban "departamento".
    # En la versión actual, el destinatario corresponde a jefaturas de secciones del DAS.
    if "seccion" not in df.columns and "departamento" in df.columns:
        df = df.rename(columns={"departamento": "seccion"})
    if "nombre" not in df.columns:
        df["nombre"] = ""
    if "correo" not in df.columns:
        df["correo"] = ""
    if "activo" not in df.columns:
        df["activo"] = "SI"
    df = df[df["activo"].astype(str).str.upper().eq("SI")].copy()
    # No debe aparecer Gestión Ambiental como destinatario, porque la emisión sale desde esa sección.
    df = df[~df["seccion"].astype(str).str.lower().str.contains("gestión ambiental|gestion ambiental", na=False)]
    return df.copy()


def ultimo_documento(tipo):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM registros WHERE tipo_documento=? AND estado!='Anulado' ORDER BY anio DESC, numero DESC LIMIT 1",
        (tipo,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def generar_documento(tipo, oficina, funcionario, dest_row, materia, usuario_login):
    anio = ahora_chile().year
    fecha = ahora_chile().strftime("%Y-%m-%d %H:%M:%S")
    conn = connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT OR IGNORE INTO correlativos(tipo_documento, anio, ultimo_numero, actualizado_por, fecha_actualizacion) VALUES(?,?,?,?,?)",
            (tipo, anio, 0, "sistema", fecha),
        )
        row = conn.execute(
            "SELECT ultimo_numero FROM correlativos WHERE tipo_documento=? AND anio=?",
            (tipo, anio),
        ).fetchone()
        nuevo = int(row["ultimo_numero"] or 0) + 1
        conn.execute("""
            INSERT INTO registros(
                tipo_documento, numero, anio, fecha_hora, seccion_origen, oficina_origen,
                funcionario, departamento_destino, jefatura_destino, destinatario_nombre,
                materia, usuario_login, estado
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            tipo, nuevo, anio, fecha, "Sección Gestión Ambiental", oficina, funcionario,
            dest_row["seccion"], dest_row["jefatura"], dest_row["nombre"],
            materia.strip(), usuario_login, "Emitido"
        ))
        conn.execute(
            "UPDATE correlativos SET ultimo_numero=?, actualizado_por=?, fecha_actualizacion=? WHERE tipo_documento=? AND anio=?",
            (nuevo, usuario_login, fecha, tipo, anio),
        )
        log_auditoria(conn, usuario_login, "Genera documento", f"{tipo} N° {nuevo:03d}/{anio}")
        conn.commit()
        return nuevo, anio, fecha
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def registros_df():
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM registros ORDER BY fecha_hora DESC", conn)
    conn.close()
    return df


def format_doc(row, tipo):
    if not row:
        return "Sin registros", "—", "—"
    return f"N° {int(row['numero']):03d}/{row['anio']}", row["funcionario"], row["fecha_hora"]


def mostrar_inicio():
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    col_logo, col_title = st.columns([1.35, 3.2], vertical_alignment="center")
    with col_logo:
        if LOGO_PATH.exists():
            st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
            st.image(str(LOGO_PATH), width=300)
            st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.markdown('<div class="main-title">Sistema de Gestión Documental</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Memorándums y Ordinarios<br>Sección de Gestión Ambiental · Departamento de Acción Sanitaria</div>', unsafe_allow_html=True)
        st.markdown('<span class="badge">SEREMI de Salud Región Metropolitana</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    memo = ultimo_documento("Memorándum")
    ordn = ultimo_documento("Ordinario")
    memo_num, memo_func, memo_fecha = format_doc(memo, "Memorándum")
    ord_num, ord_func, ord_fecha = format_doc(ordn, "Ordinario")

    st.markdown('<div class="section-title">Últimos documentos emitidos</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(f"""
        <div class="card card-blue">
            <div class="card-label">Último Memorándum emitido</div>
            <div class="big-number-blue">{memo_num}</div>
            <div>Emitido por: <b>{memo_func}</b></div>
            <div class="small-muted" style="margin-top:8px;">{memo_fecha}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="card card-red">
            <div class="card-label">Último Ordinario emitido</div>
            <div class="big-number-red">{ord_num}</div>
            <div>Emitido por: <b>{ord_func}</b></div>
            <div class="small-muted" style="margin-top:8px;">{ord_fecha}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="panel-top"></div>', unsafe_allow_html=True)


def login_box():
    with st.container():
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<h2 style='color:#003B7A;margin-bottom:18px;'>Iniciar sesión</h2>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                usuario = st.text_input("Usuario")
            with c2:
                password = st.text_input("Contraseña", type="password")
            ok = st.form_submit_button("Ingresar")
            if ok:
                user = authenticate(usuario.strip(), password)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
        st.markdown('</div>', unsafe_allow_html=True)


def page_generar():
    st.markdown('<div class="section-title">Generar documento</div>', unsafe_allow_html=True)
    funcionarios = read_funcionarios()
    destinatarios = read_destinatarios()

    st.markdown("""
    <div class="panel" style="margin-top:0;">
        <div style="font-weight:850;color:#003B7A;font-size:1.05rem;margin-bottom:6px;">Emisor institucional fijo</div>
        <div style="font-size:1.04rem;color:#1f2937;">
            Jefe(a) de la Sección Gestión Ambiental<br>
            Departamento de Acción Sanitaria · SEREMI de Salud Región Metropolitana
        </div>
        <div class="small-muted" style="margin-top:8px;">
            La oficina y el funcionario se registran solo para trazabilidad interna de quién toma el número.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("generar_documento_form", clear_on_submit=False):
        tipo = st.radio("Tipo de documento", ["Memorándum", "Ordinario"], horizontal=True)
        c1, c2 = st.columns(2)
        with c1:
            oficinas = sorted(funcionarios["oficina"].unique().tolist())
            oficina = st.selectbox("Oficina de la Sección Gestión Ambiental que solicita/toma el número", oficinas)
        with c2:
            funcionarios_filtrados = funcionarios[funcionarios["oficina"] == oficina]
            funcionario = st.selectbox("Funcionario que toma el número", funcionarios_filtrados["funcionario"].tolist())

        def etiqueta_destinatario(r):
            nombre = str(r.nombre).strip()
            base = f"{r.jefatura} — {r.seccion}"
            return f"{base} — {nombre}" if nombre else base

        dest_labels = [etiqueta_destinatario(r) for r in destinatarios.itertuples()]
        dest_label = st.selectbox("Destinatario", dest_labels)
        dest_index = dest_labels.index(dest_label)
        dest_row = destinatarios.iloc[dest_index]

        materia = st.text_area("Materia", placeholder="Ej.: Remite antecedentes técnicos...", height=120)
        generar = st.form_submit_button("Generar número")

    if generar:
        if not materia.strip():
            st.warning("Debe ingresar la materia del documento.")
        else:
            n, anio, fecha = generar_documento(tipo, oficina, funcionario, dest_row, materia, st.session_state["user"]["usuario"])
            st.markdown(f"""
            <div class="result-card">
                <div class="result-ok">Número generado correctamente</div>
                <div class="result-number">{tipo} N° {n:03d}/{anio}</div>
                <div class="result-meta">Funcionario: {funcionario} · Oficina: {oficina}</div>
                <div class="result-time">Fecha y hora de Santiago de Chile: {fecha} hrs.</div>
            </div>
            """, unsafe_allow_html=True)

def page_mis_documentos():
    st.header("Mis documentos")
    df = registros_df()
    nombre = st.session_state["user"]["nombre"]
    df = df[df["funcionario"].eq(nombre) | df["usuario_login"].eq(st.session_state["user"]["usuario"])]
    st.dataframe(df, use_container_width=True, hide_index=True)


def page_documentos():
    st.header("Registro general")
    df = registros_df()
    if df.empty:
        st.info("No existen registros.")
        return
    c1, c2, c3 = st.columns(3)
    with c1:
        tipo = st.selectbox("Filtrar tipo", ["Todos"] + sorted(df["tipo_documento"].unique().tolist()))
    with c2:
        oficina = st.selectbox("Filtrar oficina", ["Todas"] + sorted(df["oficina_origen"].unique().tolist()))
    with c3:
        texto = st.text_input("Buscar materia / funcionario / destinatario")
    if tipo != "Todos":
        df = df[df["tipo_documento"] == tipo]
    if oficina != "Todas":
        df = df[df["oficina_origen"] == oficina]
    if texto:
        t = texto.lower()
        df = df[df.apply(lambda r: t in " ".join(map(str, r.values)).lower(), axis=1)]
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("Exportar a Excel"):
        EXPORTS_DIR.mkdir(exist_ok=True)
        path = EXPORTS_DIR / f"registro_documentos_{ahora_chile().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(path, index=False)
        st.success("Archivo generado.")
        with open(path, "rb") as f:
            st.download_button("Descargar Excel", f, file_name=path.name)


def page_estadisticas():
    st.header("Estadísticas")
    df = registros_df()
    if df.empty:
        st.info("No existen datos para estadísticas.")
        return
    df["fecha"] = pd.to_datetime(df["fecha_hora"])
    df["mes"] = df["fecha"].dt.strftime("%Y-%m")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Memorándums", int((df["tipo_documento"] == "Memorándum").sum()))
    c2.metric("Ordinarios", int((df["tipo_documento"] == "Ordinario").sum()))
    c3.metric("Total documentos", len(df))
    c4.metric("Anulados", int((df["estado"] == "Anulado").sum()))

    fig1 = px.histogram(df, x="mes", color="tipo_documento", barmode="group", title="Documentos por mes")
    st.plotly_chart(fig1, use_container_width=True)
    fig2 = px.histogram(df, y="oficina_origen", color="tipo_documento", title="Documentos por oficina")
    st.plotly_chart(fig2, use_container_width=True)
    fig3 = px.histogram(df, y="funcionario", color="tipo_documento", title="Documentos por funcionario")
    st.plotly_chart(fig3, use_container_width=True)
    fig4 = px.histogram(df, y="departamento_destino", color="tipo_documento", title="Documentos por sección destinataria")
    st.plotly_chart(fig4, use_container_width=True)



def page_cambiar_password(forzado=False):
    titulo = "Cambio obligatorio de contraseña" if forzado else "Cambiar contraseña"
    st.markdown(f'<div class="section-title">{titulo}</div>', unsafe_allow_html=True)
    st.info("La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula y un número.")
    with st.form("cambiar_password_form"):
        actual = st.text_input("Contraseña actual", type="password")
        nueva = st.text_input("Nueva contraseña", type="password")
        confirma = st.text_input("Confirmar nueva contraseña", type="password")
        ok = st.form_submit_button("Guardar nueva contraseña")
    if ok:
        user = get_user(st.session_state["user"]["usuario"])
        if user["password_hash"] != hash_password(actual):
            st.error("La contraseña actual no es correcta.")
            return
        if nueva != confirma:
            st.error("La nueva contraseña y la confirmación no coinciden.")
            return
        valido, msg = password_valida(nueva)
        if not valido:
            st.error(msg)
            return
        cambiar_password(user["usuario"], nueva, 0)
        st.session_state["user"] = get_user(user["usuario"])
        st.success("Contraseña actualizada correctamente.")
        st.rerun()


def page_correlativos():
    st.markdown('<div class="section-title">Administrar correlativos</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="admin-help">
        Esta opción sirve para iniciar el sistema con los números ya utilizados en el sistema antiguo.
        Debe ingresar el <b>último número usado</b>; el próximo documento se generará sumando 1.
    </div>
    """, unsafe_allow_html=True)

    anio = st.number_input("Año", min_value=2024, max_value=2100, value=ahora_chile().year, step=1)
    conn = connect()
    asegurar_correlativos(conn)
    rows = conn.execute("SELECT * FROM correlativos WHERE anio=? ORDER BY tipo_documento", (int(anio),)).fetchall()
    actual = {r["tipo_documento"]: int(r["ultimo_numero"]) for r in rows}
    conn.close()

    memo_actual = int(actual.get("Memorándum", 0))
    ord_actual = int(actual.get("Ordinario", 0))
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Último Memorándum registrado", f"N° {memo_actual:03d}/{int(anio)}", f"Próximo: N° {memo_actual + 1:03d}/{int(anio)}")
    with c2:
        st.metric("Último Ordinario registrado", f"N° {ord_actual:03d}/{int(anio)}", f"Próximo: N° {ord_actual + 1:03d}/{int(anio)}")

    with st.form("correlativos_form"):
        c1, c2 = st.columns(2)
        with c1:
            memo = st.number_input("Último número utilizado de Memorándum", min_value=0, value=memo_actual, step=1)
        with c2:
            ordn = st.number_input("Último número utilizado de Ordinario", min_value=0, value=ord_actual, step=1)
        st.caption("Ejemplo: si el último Memorándum antiguo fue 458, ingrese 458. El sistema entregará 459/2026.")
        ok = st.form_submit_button("Guardar correlativos")

    if ok:
        conn = connect()
        for tipo, valor in [("Memorándum", int(memo)), ("Ordinario", int(ordn))]:
            anterior = conn.execute("SELECT ultimo_numero FROM correlativos WHERE tipo_documento=? AND anio=?", (tipo, int(anio))).fetchone()
            ant = int(anterior["ultimo_numero"]) if anterior else 0
            conn.execute(
                "INSERT OR REPLACE INTO correlativos(tipo_documento, anio, ultimo_numero, actualizado_por, fecha_actualizacion) VALUES(?,?,?,?,?)",
                (tipo, int(anio), valor, st.session_state["user"]["usuario"], ahora_chile().strftime("%Y-%m-%d %H:%M:%S")),
            )
            if ant != valor:
                log_auditoria(conn, st.session_state["user"]["usuario"], "Actualiza correlativo", f"{tipo} {anio}: {ant} → {valor}")
        conn.commit(); conn.close()
        st.success("Correlativos actualizados correctamente.")
        st.rerun()

def page_usuarios_admin():
    st.markdown('<div class="section-title">Administrar usuarios</div>', unsafe_allow_html=True)
    st.subheader("Crear nuevo usuario")
    funcionarios = read_funcionarios()
    oficinas = [""] + sorted(funcionarios["oficina"].unique().tolist())
    with st.form("crear_usuario_form"):
        c1, c2 = st.columns(2)
        with c1:
            usuario = st.text_input("Usuario de acceso", placeholder="Ej.: jperez")
            nombre = st.text_input("Nombre completo")
            oficina = st.selectbox("Oficina", oficinas)
        with c2:
            rol = st.selectbox("Rol", ["Funcionario", "Jefatura", "Administrador"])
            temp = st.text_input("Contraseña temporal", type="password", placeholder="Ej.: SGA2026Jp")
            st.caption("El usuario deberá cambiarla en su primer ingreso.")
            temp2 = st.text_input("Confirmar contraseña temporal", type="password")
        ok = st.form_submit_button("Crear usuario")
    if ok:
        if not usuario.strip() or not nombre.strip() or not temp:
            st.error("Debe completar usuario, nombre y contraseña temporal.")
        elif temp != temp2:
            st.error("Las contraseñas temporales no coinciden.")
        else:
            valido, msg = password_valida(temp)
            if not valido:
                st.error(msg)
            else:
                conn = connect()
                existe = conn.execute("SELECT usuario FROM usuarios WHERE usuario=?", (usuario.strip(),)).fetchone()
                if existe:
                    st.error("Ese usuario ya existe.")
                else:
                    conn.execute("""INSERT INTO usuarios(usuario,nombre,rol,password_hash,oficina,debe_cambiar_password,activo,fecha_creacion)
                                    VALUES(?,?,?,?,?,?,?,?)""", (usuario.strip(), nombre.strip(), rol, hash_password(temp), oficina, 1, 1, ahora_chile().strftime("%Y-%m-%d %H:%M:%S")))
                    log_auditoria(conn, st.session_state["user"]["usuario"], "Crea usuario", f"Usuario creado: {usuario.strip()} ({rol})")
                    conn.commit(); conn.close()
                    st.success("Usuario creado correctamente.")
                    st.markdown(f"""
                    <div class="credential-box">
                    <b>Credenciales para entregar:</b><br>
                    Usuario: <b>{usuario.strip()}</b><br>
                    Contraseña temporal: <b>{temp}</b><br><br>
                    Al ingresar por primera vez, el sistema obligará a cambiar la contraseña.
                    </div>
                    """, unsafe_allow_html=True)
    st.subheader("Usuarios existentes")
    conn = connect()
    dfu = pd.read_sql_query("SELECT usuario,nombre,rol,oficina,debe_cambiar_password,activo,ultimo_acceso FROM usuarios ORDER BY rol,nombre", conn)
    conn.close()
    st.dataframe(dfu, use_container_width=True, hide_index=True)

    st.subheader("Restablecer contraseña / activar o desactivar")
    if not dfu.empty:
        sel = st.selectbox("Usuario", dfu["usuario"].tolist())
        c1, c2 = st.columns(2)
        with c1:
            nueva = st.text_input("Nueva contraseña temporal", type="password")
            if st.button("Restablecer contraseña"):
                valido, msg = password_valida(nueva)
                if not valido:
                    st.error(msg)
                else:
                    conn = connect()
                    conn.execute("UPDATE usuarios SET password_hash=?, debe_cambiar_password=1 WHERE usuario=?", (hash_password(nueva), sel))
                    log_auditoria(conn, st.session_state["user"]["usuario"], "Restablece contraseña", f"Usuario: {sel}")
                    conn.commit(); conn.close()
                    st.success("Contraseña temporal asignada. El usuario deberá cambiarla al ingresar.")
        with c2:
            activo = st.selectbox("Estado", ["Activo", "Inactivo"])
            if st.button("Guardar estado"):
                conn = connect()
                conn.execute("UPDATE usuarios SET activo=? WHERE usuario=?", (1 if activo == "Activo" else 0, sel))
                log_auditoria(conn, st.session_state["user"]["usuario"], "Cambia estado usuario", f"{sel}: {activo}")
                conn.commit(); conn.close()
                st.success("Estado actualizado.")
                st.rerun()


def _read_catalogo_raw(path, columnas):
    if path.exists():
        df = pd.read_csv(path, dtype=str).fillna("")
    else:
        df = pd.DataFrame(columns=columnas)
    for col in columnas:
        if col not in df.columns:
            df[col] = ""
    df = df[columnas].copy()
    return df.fillna("")


def _guardar_catalogo(path, df, columnas, usuario, nombre_catalogo):
    df = df.copy().fillna("")
    for col in columnas:
        if col not in df.columns:
            df[col] = ""
    df = df[columnas]

    # Limpieza básica
    if "id" in df.columns:
        df["id"] = df["id"].astype(str).str.strip()
    if "activo" in df.columns:
        df["activo"] = df["activo"].astype(str).str.strip().str.upper().replace({"": "SI", "S": "SI", "TRUE": "SI", "1": "SI", "NO": "NO", "0": "NO", "FALSE": "NO"})
        df.loc[~df["activo"].isin(["SI", "NO"]), "activo"] = "SI"

    # Eliminar filas completamente vacías, excepto id
    cols_sin_id = [c for c in columnas if c != "id"]
    df = df[df[cols_sin_id].astype(str).apply(lambda r: any(x.strip() for x in r), axis=1)].copy()

    # Completar id faltante y corregir duplicados con números correlativos
    if "id" in df.columns:
        used = set()
        next_id = 1
        nuevos = []
        for val in df["id"].tolist():
            val = str(val).strip()
            if val.isdigit() and val not in used:
                nuevos.append(val)
                used.add(val)
                next_id = max(next_id, int(val) + 1)
            else:
                while str(next_id) in used:
                    next_id += 1
                nuevos.append(str(next_id))
                used.add(str(next_id))
                next_id += 1
        df["id"] = nuevos

    path.parent.mkdir(exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    conn = connect()
    log_auditoria(conn, usuario, "Actualiza catálogo", f"Se actualizó {nombre_catalogo}. Filas: {len(df)}")
    conn.commit(); conn.close()
    return df


def page_catalogos_admin():
    st.markdown('<div class="section-title">Catálogos del sistema</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="admin-help">
        Desde esta pantalla puede agregar, editar o desactivar funcionarios y destinatarios.
        Para ocultar un registro sin borrarlo, cambie el campo <b>activo</b> a <b>NO</b>.
    </div>
    """, unsafe_allow_html=True)

    st.warning("Los cambios se guardan en los archivos CSV de la app. En Streamlit Cloud pueden perderse si la aplicación se reinicia o se redepliega desde GitHub. Para dejarlos permanentes, después también conviene actualizar los CSV en GitHub.")

    t1, t2 = st.tabs(["Funcionarios por oficina", "Destinatarios"])

    with t1:
        st.subheader("Funcionarios por oficina")
        st.caption("Agregue una fila nueva al final de la tabla. Campos mínimos recomendados: oficina, sección, funcionario y activo=SI.")
        cols_func = ["id", "oficina", "seccion", "funcionario", "cargo", "correo", "activo"]
        try:
            df_func = _read_catalogo_raw(FUNCIONARIOS_CSV, cols_func)
            edit_func = st.data_editor(
                df_func,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="editor_funcionarios",
                column_config={
                    "activo": st.column_config.SelectboxColumn("activo", options=["SI", "NO"], required=True),
                    "correo": st.column_config.TextColumn("correo", help="Correo institucional, opcional"),
                },
            )
            if st.button("Guardar funcionarios", key="guardar_funcionarios"):
                _guardar_catalogo(FUNCIONARIOS_CSV, edit_func, cols_func, st.session_state["user"]["usuario"], "funcionarios.csv")
                st.success("Funcionarios actualizados correctamente.")
                st.rerun()
        except Exception as e:
            st.error(f"No se pudo editar funcionarios.csv: {e}")

    with t2:
        st.subheader("Destinatarios")
        st.caption("Corresponden a jefaturas de secciones del Departamento de Acción Sanitaria. No agregue Gestión Ambiental como destinatario.")
        cols_dest = ["id", "seccion", "jefatura", "nombre", "correo", "activo"]
        try:
            df_dest = _read_catalogo_raw(DESTINATARIOS_CSV, cols_dest)
            # Regla de seguridad visual: ocultar Gestión Ambiental si alguien la agregó antes
            df_dest = df_dest[~df_dest["seccion"].astype(str).str.lower().str.contains("gestión ambiental|gestion ambiental", na=False)].copy()
            edit_dest = st.data_editor(
                df_dest,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="editor_destinatarios",
                column_config={
                    "activo": st.column_config.SelectboxColumn("activo", options=["SI", "NO"], required=True),
                    "correo": st.column_config.TextColumn("correo", help="Correo institucional, opcional"),
                },
            )
            if st.button("Guardar destinatarios", key="guardar_destinatarios"):
                # Regla fija: no guardar Gestión Ambiental como destinatario
                edit_dest = edit_dest[~edit_dest["seccion"].astype(str).str.lower().str.contains("gestión ambiental|gestion ambiental", na=False)].copy()
                _guardar_catalogo(DESTINATARIOS_CSV, edit_dest, cols_dest, st.session_state["user"]["usuario"], "destinatarios.csv")
                st.success("Destinatarios actualizados correctamente.")
                st.rerun()
        except Exception as e:
            st.error(f"No se pudo editar destinatarios.csv: {e}")


def page_auditoria_admin():
    st.markdown('<div class="section-title">Auditoría del sistema</div>', unsafe_allow_html=True)
    conn = connect()
    aud = pd.read_sql_query("SELECT fecha_hora, usuario, accion, detalle FROM auditoria ORDER BY id DESC LIMIT 200", conn)
    conn.close()
    if aud.empty:
        st.info("No existen movimientos de auditoría.")
    else:
        st.dataframe(aud, use_container_width=True, hide_index=True)


def page_admin():
    st.markdown('<div class="section-title">Administración</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="admin-help">
        Panel reservado para Administrador y Jefatura. Permite ajustar correlativos, revisar catálogos,
        anular documentos y consultar auditoría. La creación y restablecimiento de usuarios queda solo para Administrador.
    </div>
    """, unsafe_allow_html=True)

    df = registros_df()
    conn = connect()
    users_count = conn.execute("SELECT COUNT(*) AS n FROM usuarios WHERE activo=1").fetchone()["n"]
    aud_count = conn.execute("SELECT COUNT(*) AS n FROM auditoria").fetchone()["n"]
    conn.close()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="admin-card"><div class="admin-card-title">Documentos registrados</div><div class="admin-card-text"><b>{len(df)}</b> documentos en el sistema.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="admin-card"><div class="admin-card-title">Usuarios activos</div><div class="admin-card-text"><b>{users_count}</b> usuarios habilitados.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="admin-card"><div class="admin-card-title">Auditoría</div><div class="admin-card-text"><b>{aud_count}</b> movimientos registrados.</div></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Correlativos", "Usuarios", "Catálogos", "Anular documento", "Auditoría"])
    with tab1:
        page_correlativos()
    with tab2:
        if st.session_state["user"]["rol"] == "Administrador":
            page_usuarios_admin()
        else:
            st.info("La administración de usuarios está disponible solo para el Administrador.")
    with tab3:
        page_catalogos_admin()
    with tab4:
        st.subheader("Anular documento")
        df = registros_df()
        if not df.empty:
            df["etiqueta"] = df.apply(lambda r: f"{r['tipo_documento']} N° {int(r['numero']):03d}/{r['anio']} - {r['funcionario']} - {str(r['materia'])[:50]}", axis=1)
            etiqueta = st.selectbox("Documento", df["etiqueta"].tolist())
            motivo = st.text_input("Motivo de anulación")
            st.warning("La anulación no elimina el registro ni libera el número. Solo cambia el estado para mantener trazabilidad.")
            if st.button("Anular registro"):
                row = df[df["etiqueta"] == etiqueta].iloc[0]
                conn = connect()
                conn.execute("UPDATE registros SET estado=? WHERE id=?", (f"Anulado - {motivo}" if motivo else "Anulado", int(row["id"])))
                log_auditoria(conn, st.session_state["user"]["usuario"], "Anula documento", etiqueta)
                conn.commit(); conn.close()
                st.success("Registro anulado.")
                st.rerun()
        else:
            st.info("No existen documentos para anular.")
    with tab5:
        page_auditoria_admin()

def main():
    init_db()
    mostrar_inicio()

    if "user" not in st.session_state:
        login_box()
        st.caption("Usuarios iniciales: admin/admin123, jefatura/jefatura123, marco/marco123. Cambiar antes de uso real.")
        return

    user = st.session_state["user"]
    if int(user.get("debe_cambiar_password", 0)) == 1:
        page_cambiar_password(forzado=True)
        return
    st.sidebar.write(f"**{user['nombre']}**")
    st.sidebar.caption(f"Rol: {user['rol']}")
    opciones = ["Generar documento", "Mis documentos", "Cambiar contraseña"]
    if user["rol"] in ["Administrador", "Jefatura"]:
        opciones += ["Registro general", "Estadísticas", "Administración"]
    pagina = st.sidebar.radio("Menú", opciones)
    if st.sidebar.button("Cerrar sesión"):
        del st.session_state["user"]
        st.rerun()

    if pagina == "Generar documento":
        page_generar()
    elif pagina == "Mis documentos":
        page_mis_documentos()
    elif pagina == "Cambiar contraseña":
        page_cambiar_password()
    elif pagina == "Registro general":
        page_documentos()
    elif pagina == "Estadísticas":
        page_estadisticas()
    elif pagina == "Administración":
        page_admin()

    st.markdown('<div class="footer-line"></div>', unsafe_allow_html=True)
    st.caption("Versión 1.0 · SEREMI de Salud Región Metropolitana · Departamento de Acción Sanitaria · Sección Gestión Ambiental")


if __name__ == "__main__":
    main()
