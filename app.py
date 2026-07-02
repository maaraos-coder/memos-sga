import os
import sqlite3
import hashlib
from datetime import datetime
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
.logo-wrap img {{max-width: 230px !important; height:auto !important; display:block; margin:auto;}}
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
.panel h3, .panel .stSubheader {
    color:#003B7A !important;
}


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
            oficina TEXT
        )
    """)
    conn.commit()
    cargar_usuarios_csv(conn)
    conn.close()


def cargar_usuarios_csv(conn):
    if USUARIOS_CSV.exists():
        df = pd.read_csv(USUARIOS_CSV).fillna("")
        for _, r in df.iterrows():
            conn.execute(
                "INSERT OR IGNORE INTO usuarios(usuario,nombre,rol,password_hash,oficina) VALUES(?,?,?,?,?)",
                (r["usuario"], r["nombre"], r["rol"], r["password_hash"], r.get("oficina", "")),
            )
        conn.commit()


def get_user(username: str):
    conn = connect()
    row = conn.execute("SELECT * FROM usuarios WHERE usuario=?", (username,)).fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate(username: str, password: str):
    user = get_user(username)
    if user and user["password_hash"] == hash_password(password):
        return user
    return None


def read_funcionarios():
    df = pd.read_csv(FUNCIONARIOS_CSV).fillna("")
    return df[df["activo"].astype(str).str.upper().eq("SI")].copy()


def read_destinatarios():
    df = pd.read_csv(DESTINATARIOS_CSV).fillna("")
    return df[df["activo"].astype(str).str.upper().eq("SI")].copy()


def ultimo_documento(tipo):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM registros WHERE tipo_documento=? AND estado!='Anulado' ORDER BY anio DESC, numero DESC LIMIT 1",
        (tipo,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def generar_documento(tipo, oficina, funcionario, dest_row, materia, usuario_login):
    anio = datetime.now().year
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = connect()
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT MAX(numero) AS max_num FROM registros WHERE tipo_documento=? AND anio=?",
            (tipo, anio),
        ).fetchone()
        nuevo = int(row["max_num"] or 0) + 1
        conn.execute("""
            INSERT INTO registros(
                tipo_documento, numero, anio, fecha_hora, seccion_origen, oficina_origen,
                funcionario, departamento_destino, jefatura_destino, destinatario_nombre,
                materia, usuario_login, estado
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            tipo, nuevo, anio, fecha, "Sección Gestión Ambiental", oficina, funcionario,
            dest_row["departamento"], dest_row["jefatura"], dest_row["nombre"],
            materia.strip(), usuario_login, "Emitido"
        ))
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
            st.image(str(LOGO_PATH), width=225)
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

    with st.form("generar_documento_form", clear_on_submit=False):
        tipo = st.radio("Tipo de documento", ["Memorándum", "Ordinario"], horizontal=True)
        c1, c2 = st.columns(2)
        with c1:
            oficinas = sorted(funcionarios["oficina"].unique().tolist())
            oficina = st.selectbox("Oficina de origen", oficinas)
        with c2:
            funcionarios_filtrados = funcionarios[funcionarios["oficina"] == oficina]
            funcionario = st.selectbox("Funcionario emisor", funcionarios_filtrados["funcionario"].tolist())

        dest_labels = [f"{r.departamento} — {r.jefatura} — {r.nombre}" for r in destinatarios.itertuples()]
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
            st.success(f"{tipo} N° {n:03d}/{anio} generado correctamente.")
            st.info(f"Fecha y hora: {fecha}")


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
        path = EXPORTS_DIR / f"registro_documentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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


def page_admin():
    st.header("Administración")
    st.info("Los catálogos iniciales se editan en CSV: funcionarios.csv, destinatarios.csv y usuarios.csv.")
    st.subheader("Usuarios cargados")
    conn = connect()
    dfu = pd.read_sql_query("SELECT usuario,nombre,rol,oficina FROM usuarios ORDER BY rol,nombre", conn)
    conn.close()
    st.dataframe(dfu, use_container_width=True, hide_index=True)

    st.subheader("Anular documento")
    df = registros_df()
    if not df.empty:
        df["etiqueta"] = df.apply(lambda r: f"{r['tipo_documento']} N° {int(r['numero']):03d}/{r['anio']} - {r['funcionario']} - {r['materia'][:50]}", axis=1)
        etiqueta = st.selectbox("Documento", df["etiqueta"].tolist())
        motivo = st.text_input("Motivo de anulación")
        if st.button("Anular registro"):
            row = df[df["etiqueta"] == etiqueta].iloc[0]
            conn = connect()
            conn.execute("UPDATE registros SET estado=? WHERE id=?", (f"Anulado - {motivo}" if motivo else "Anulado", int(row["id"])))
            conn.commit(); conn.close()
            st.success("Registro anulado.")
            st.rerun()


def main():
    init_db()
    mostrar_inicio()

    if "user" not in st.session_state:
        login_box()
        st.caption("Usuarios iniciales: admin/admin123, jefatura/jefatura123, marco/marco123. Cambiar antes de uso real.")
        return

    user = st.session_state["user"]
    st.sidebar.write(f"**{user['nombre']}**")
    st.sidebar.caption(f"Rol: {user['rol']}")
    opciones = ["Generar documento", "Mis documentos"]
    if user["rol"] in ["Administrador", "Jefatura"]:
        opciones += ["Registro general", "Estadísticas"]
    if user["rol"] == "Administrador":
        opciones += ["Administración"]
    pagina = st.sidebar.radio("Menú", opciones)
    if st.sidebar.button("Cerrar sesión"):
        del st.session_state["user"]
        st.rerun()

    if pagina == "Generar documento":
        page_generar()
    elif pagina == "Mis documentos":
        page_mis_documentos()
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
