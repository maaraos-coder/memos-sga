import os
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"
EXPORTS_DIR = BASE_DIR / "exports"
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
CHILE_TZ = ZoneInfo("America/Santiago")


def ahora_chile():
    return datetime.now(CHILE_TZ)


def fecha_str(dt=None):
    return (dt or ahora_chile()).strftime("%Y-%m-%d %H:%M:%S")


st.markdown(f"""
<style>
.stApp {{ background: linear-gradient(180deg, #ffffff 0%, #f3f7fc 42%, #eef3f8 100%); color: #1f2937; }}
header[data-testid="stHeader"] {{ background: rgba(255,255,255,0.92); }}
.block-container {{ padding-top: 1.6rem !important; padding-bottom: 2.2rem !important; max-width: 1100px !important; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #ffffff 0%, #edf4fb 100%); border-right: 1px solid #d8e4f0; }}
section[data-testid="stSidebar"] * {{ color: #17345d; }}
section[data-testid="stSidebar"] .stButton button {{ width: 100%; }}
.hero-card {{ background: #ffffff; border: 1px solid #d9e5f2; border-radius: 22px; box-shadow: 0 8px 26px rgba(0, 61, 122, 0.08); padding: 24px 28px; margin: 0 0 26px 0; position: relative; overflow: hidden; }}
.hero-card:before {{ content: ""; position: absolute; top: 0; left: 0; right: 0; height: 7px; background: linear-gradient(90deg, {AZUL} 0%, {AZUL} 62%, {ROJO} 62%, {ROJO} 100%); }}
.logo-wrap {{ display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; padding:8px; border: 1px solid #e6eef7; }}
.logo-wrap img {{ max-width: 240px !important; height:auto !important; display:block; margin:auto; }}
.main-title {{ font-size: 2.05rem; line-height: 1.15; font-weight: 850; color: #003B7A; margin: 0 0 8px 0; letter-spacing: -0.02em; }}
.sub-title {{ font-size: 1.04rem; color: #536179; margin: 0; line-height: 1.55; }}
.badge {{ display:inline-block; margin-top: 10px; padding: 6px 12px; border-radius: 999px; background:#eef5ff; color:#004a91; font-weight: 700; font-size: 0.90rem; }}
.section-title {{ font-size: 1.55rem; font-weight: 850; color: #1f2937; margin: 10px 0 16px 0; }}
h1, h2, h3 {{ color:#1f2937 !important; letter-spacing:-0.02em; }}
.card {{ background: white; border: 1px solid #d9e3f0; border-radius: 18px; padding: 24px 28px; box-shadow: 0 6px 18px rgba(0,61,122,0.06); min-height: 172px; }}
.card-blue {{ border-left: 8px solid {AZUL}; }}
.card-red {{ border-left: 8px solid {ROJO}; }}
.card-label {{ font-weight:800; color:#1f2937; font-size:1.02rem; }}
.big-number-blue {{ font-size: 2.12rem; color: {AZUL}; font-weight: 900; line-height: 1.45; }}
.big-number-red {{ font-size: 2.12rem; color: {ROJO}; font-weight: 900; line-height: 1.45; }}
.small-muted {{ color:#60708a; font-size: 0.95rem; }}
.panel {{ background:#ffffff; border: 1px solid #d9e3f0; border-radius: 18px; box-shadow: 0 6px 18px rgba(0,61,122,0.06); padding: 24px 28px 28px 28px; margin-top: 18px; }}
.panel-top {{ height: 6px; background: linear-gradient(90deg, {AZUL} 0%, {AZUL} 60%, {ROJO} 60%, {ROJO} 100%); border-radius:999px; margin: 22px 0 14px 0; }}
.footer-line {{ height: 5px; background: linear-gradient(90deg, {AZUL} 0%, {AZUL} 50%, {ROJO} 50%, {ROJO} 100%); margin: 30px 0 0 0; border-radius:999px; }}
div.stButton > button:first-child, div.stFormSubmitButton > button {{ background: linear-gradient(90deg, {AZUL}, #004a91) !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 800 !important; padding: 0.65rem 1.25rem !important; box-shadow: 0 6px 14px rgba(0,94,184,0.18); }}
div.stButton > button:first-child:hover, div.stFormSubmitButton > button:hover {{ background: linear-gradient(90deg, #004a91, #003B7A) !important; color:white !important; }}
.stRadio [role="radiogroup"] label:first-child span:nth-child(2) {{ font-weight:700; color:{AZUL}; }}
.stRadio [role="radiogroup"] label:nth-child(2) span:nth-child(2) {{ font-weight:700; color:{ROJO}; }}
input, textarea, div[data-baseweb="select"] {{ border-radius: 10px !important; }}
div[data-testid="stForm"] label, div[data-testid="stForm"] p, div[data-testid="stWidgetLabel"] p {{ color:#1f2937 !important; font-size: 1.02rem !important; font-weight: 750 !important; }}
.stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div {{ background:#ffffff !important; color:#111827 !important; border:1.8px solid #b9c8dc !important; min-height: 46px !important; font-size: 1.02rem !important; box-shadow: inset 0 1px 2px rgba(0,0,0,0.03); }}
.stTextInput input:focus, .stTextArea textarea:focus {{ border:2px solid {AZUL} !important; }}
.panel h3, .panel .stSubheader {{ color:#003B7A !important; }}
.result-card {{ background: linear-gradient(135deg, #ffffff 0%, #eef7ff 100%); border: 2px solid #b8d7f5; border-left: 10px solid #005EB8; border-radius: 20px; box-shadow: 0 10px 24px rgba(0, 94, 184, 0.12); padding: 26px 30px; margin: 18px 0 12px 0; }}
.result-ok {{ display:inline-block; background:#dcfce7; color:#166534; font-weight:900; padding:7px 13px; border-radius:999px; margin-bottom:10px; }}
.result-number {{ font-size: 2.7rem; line-height:1.15; font-weight:950; color:#003B7A; letter-spacing:-0.03em; }}
.result-meta {{ margin-top:10px; color:#334155; font-size:1.05rem; font-weight:650; }}
.result-time {{ margin-top:8px; color:#005EB8; font-size:1.03rem; font-weight:750; }}
.admin-card {{ background:#ffffff; border:1px solid #d9e3f0; border-radius:16px; padding:18px 20px; box-shadow:0 5px 14px rgba(0,61,122,0.05); min-height:105px; }}
.admin-card-title {{ font-weight:900; color:#003B7A; font-size:1.05rem; margin-bottom:7px; }}
.admin-card-text {{ color:#334155; font-size:0.98rem; line-height:1.45; }}
.admin-help {{ background:#eef5ff; border-left:6px solid #005EB8; border-radius:14px; padding:14px 16px; color:#1f2937; margin:10px 0 18px 0; }}
.credential-box {{ background:#f8fafc; border:1.8px dashed #005EB8; border-radius:14px; padding:16px 18px; margin:12px 0; color:#0f172a; font-size:1rem; }}
div[data-testid="stMetric"] {{ background:#ffffff; border:1px solid #dbe6f3; border-radius:16px; padding:16px 18px; box-shadow: 0 4px 12px rgba(0,61,122,0.05); }}
@media (max-width: 900px) {{ .block-container {{ padding-left: 1rem !important; padding-right: 1rem !important; }} .main-title {{ font-size: 1.55rem; text-align:center; }} .sub-title {{ text-align:center; }} .logo-wrap img {{ max-width: 170px !important; }} .card {{ min-height:auto; }} }}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Supabase / PostgreSQL
# -------------------------

@st.cache_resource(show_spinner=False)
def get_engine():
    db_url = st.secrets.get("DATABASE_URL", "")
    if not db_url:
        st.error("No está configurado DATABASE_URL en Streamlit Secrets.")
        st.stop()
    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
        connect_args={"connect_timeout": 5},
    )


def db_execute(sql, params=None):
    engine = get_engine()
    with engine.begin() as conn:
        return conn.execute(text(sql), params or {})


def db_query_df(sql, params=None):
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn, params=params or {})


def db_query_one(sql, params=None):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text(sql), params or {}).mappings().fetchone()
        return dict(row) if row else None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def tipo_key(tipo: str) -> str:
    return "MEMORANDUM" if tipo == "Memorándum" else "ORDINARIO"


def tipo_display(key: str) -> str:
    return "Memorándum" if str(key).upper() == "MEMORANDUM" else "Ordinario"


def init_db():
    DATA_DIR.mkdir(exist_ok=True)
    EXPORTS_DIR.mkdir(exist_ok=True)
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            create table if not exists documentos (
              id bigint generated always as identity primary key,
              tipo text not null,
              numero integer not null,
              anio integer not null,
              fecha_hora timestamptz not null,
              seccion_origen text default 'Sección Gestión Ambiental',
              oficina_origen text not null,
              funcionario text not null,
              seccion_destino text,
              jefatura_destino text,
              destinatario_nombre text,
              destinatario text,
              materia text not null,
              estado text default 'Emitido',
              usuario_creador text not null
            )
        """))
        # Migraciones seguras por si la tabla ya existía con la versión inicial.
        for col, ddl in {
            "seccion_origen": "alter table documentos add column if not exists seccion_origen text default 'Sección Gestión Ambiental'",
            "seccion_destino": "alter table documentos add column if not exists seccion_destino text",
            "jefatura_destino": "alter table documentos add column if not exists jefatura_destino text",
            "destinatario_nombre": "alter table documentos add column if not exists destinatario_nombre text",
            "destinatario": "alter table documentos add column if not exists destinatario text",
        }.items():
            conn.execute(text(ddl))
        conn.execute(text("create unique index if not exists idx_documentos_numero on documentos(tipo, numero, anio)"))

        conn.execute(text("""
            create table if not exists correlativos (
              tipo text not null,
              anio integer not null,
              ultimo_numero integer not null default 0,
              actualizado_por text,
              actualizado_en timestamptz default now(),
              primary key (tipo, anio)
            )
        """))
        conn.execute(text("""
            create table if not exists usuarios (
              id bigint generated always as identity primary key,
              usuario text unique not null,
              nombre text not null,
              rol text not null,
              oficina text,
              password_hash text not null,
              debe_cambiar_password boolean default true,
              activo boolean default true,
              fecha_creacion timestamptz default now(),
              ultimo_acceso timestamptz
            )
        """))
        conn.execute(text("""
            create table if not exists funcionarios (
              id bigint generated always as identity primary key,
              oficina text not null,
              seccion text default 'Sección Gestión Ambiental',
              funcionario text not null,
              cargo text,
              correo text,
              activo text default 'SI'
            )
        """))
        conn.execute(text("alter table funcionarios add column if not exists seccion text default 'Sección Gestión Ambiental'"))
        conn.execute(text("""
            create table if not exists destinatarios (
              id bigint generated always as identity primary key,
              seccion text not null,
              jefatura text not null,
              nombre text,
              correo text,
              activo text default 'SI'
            )
        """))
        conn.execute(text("""
            create table if not exists auditoria (
              id bigint generated always as identity primary key,
              fecha_hora timestamptz default now(),
              usuario text,
              accion text,
              detalle text
            )
        """))
    seed_data()
    asegurar_correlativos()


@st.cache_resource(show_spinner=False)
def init_once():
    init_db()
    return True


def limpiar_cache_datos():
    read_funcionarios.clear()
    read_destinatarios.clear()
    registros_df.clear()
    ultimos_documentos.clear()


def seed_data():
    engine = get_engine()
    with engine.begin() as conn:
        n_users = conn.execute(text("select count(*) from usuarios")).scalar() or 0
        if n_users == 0:
            rows = []
            if USUARIOS_CSV.exists():
                dfu = pd.read_csv(USUARIOS_CSV).fillna("")
                for _, r in dfu.iterrows():
                    rows.append({
                        "usuario": str(r.get("usuario", "")).strip(),
                        "nombre": str(r.get("nombre", "")).strip(),
                        "rol": str(r.get("rol", "Funcionario")).strip() or "Funcionario",
                        "oficina": str(r.get("oficina", "")).strip(),
                        "password_hash": str(r.get("password_hash", "")).strip() or hash_password("Temp1234"),
                        "debe": str(r.get("debe_cambiar_password", "0")).strip() in ["1", "SI", "TRUE", "True", "true"],
                        "activo": str(r.get("activo", "1")).strip() not in ["0", "NO", "FALSE", "False", "false"],
                    })
            if not rows:
                rows = [
                    {"usuario": "admin", "nombre": "Administrador", "rol": "Administrador", "oficina": "", "password_hash": hash_password("admin123"), "debe": False, "activo": True},
                    {"usuario": "jefatura", "nombre": "Jefatura Gestión Ambiental", "rol": "Jefatura", "oficina": "Sección Gestión Ambiental", "password_hash": hash_password("jefatura123"), "debe": False, "activo": True},
                    {"usuario": "marco", "nombre": "Marco Araos Barría", "rol": "Administrador", "oficina": "Oficina de Acústica y Vibraciones", "password_hash": hash_password("marco123"), "debe": False, "activo": True},
                ]
            for r in rows:
                if r["usuario"]:
                    conn.execute(text("""
                        insert into usuarios(usuario,nombre,rol,oficina,password_hash,debe_cambiar_password,activo,fecha_creacion)
                        values(:usuario,:nombre,:rol,:oficina,:password_hash,:debe,:activo,now())
                        on conflict(usuario) do nothing
                    """), r)

        n_func = conn.execute(text("select count(*) from funcionarios")).scalar() or 0
        if n_func == 0:
            if FUNCIONARIOS_CSV.exists():
                dff = pd.read_csv(FUNCIONARIOS_CSV).fillna("")
            else:
                dff = pd.DataFrame([
                    {"oficina": "Oficina de Acústica y Vibraciones", "seccion": "Sección Gestión Ambiental", "funcionario": "Marco Araos Barría", "cargo": "Profesional", "correo": "marco.araos@redsalud.gov.cl", "activo": "SI"},
                    {"oficina": "Oficina de SEIA", "seccion": "Sección Gestión Ambiental", "funcionario": "Nombre Funcionario SEIA", "cargo": "Profesional", "correo": "", "activo": "SI"},
                    {"oficina": "Oficina de Calificación Industrial", "seccion": "Sección Gestión Ambiental", "funcionario": "Nombre Funcionario Calificación", "cargo": "Profesional", "correo": "", "activo": "SI"},
                ])
            for _, r in dff.iterrows():
                conn.execute(text("""
                    insert into funcionarios(oficina,seccion,funcionario,cargo,correo,activo)
                    values(:oficina,:seccion,:funcionario,:cargo,:correo,:activo)
                """), {
                    "oficina": str(r.get("oficina", "")).strip(),
                    "seccion": str(r.get("seccion", "Sección Gestión Ambiental")).strip() or "Sección Gestión Ambiental",
                    "funcionario": str(r.get("funcionario", "")).strip(),
                    "cargo": str(r.get("cargo", "")).strip(),
                    "correo": str(r.get("correo", "")).strip(),
                    "activo": str(r.get("activo", "SI")).strip().upper() or "SI",
                })

        n_dest = conn.execute(text("select count(*) from destinatarios")).scalar() or 0
        if n_dest == 0:
            if DESTINATARIOS_CSV.exists():
                dfd = pd.read_csv(DESTINATARIOS_CSV).fillna("")
                if "seccion" not in dfd.columns and "departamento" in dfd.columns:
                    dfd = dfd.rename(columns={"departamento": "seccion"})
            else:
                dfd = pd.DataFrame([
                    {"seccion": "Sección Control Sanitario de los Alimentos", "jefatura": "Jefe(a) Sección Control Sanitario de los Alimentos", "nombre": "", "correo": "", "activo": "SI"},
                    {"seccion": "Sección Salud Ocupacional y Prevención de Riesgos", "jefatura": "Jefe(a) Sección Salud Ocupacional y Prevención de Riesgos", "nombre": "", "correo": "", "activo": "SI"},
                    {"seccion": "Sección Estrategias Sanitarias Transversales y Emergentes", "jefatura": "Jefe(a) Sección Estrategias Sanitarias Transversales y Emergentes", "nombre": "", "correo": "", "activo": "SI"},
                    {"seccion": "Sección Control Sanitario Ambiental", "jefatura": "Jefe(a) Sección Control Sanitario Ambiental", "nombre": "", "correo": "", "activo": "SI"},
                    {"seccion": "Sección Prestadores de Salud y Medicinas Complementarias", "jefatura": "Jefe(a) Sección Prestadores de Salud y Medicinas Complementarias", "nombre": "", "correo": "", "activo": "SI"},
                ])
            for _, r in dfd.iterrows():
                seccion = str(r.get("seccion", "")).strip()
                if "gestión ambiental" in seccion.lower() or "gestion ambiental" in seccion.lower():
                    continue
                conn.execute(text("""
                    insert into destinatarios(seccion,jefatura,nombre,correo,activo)
                    values(:seccion,:jefatura,:nombre,:correo,:activo)
                """), {
                    "seccion": seccion,
                    "jefatura": str(r.get("jefatura", "")).strip(),
                    "nombre": str(r.get("nombre", "")).strip(),
                    "correo": str(r.get("correo", "")).strip(),
                    "activo": str(r.get("activo", "SI")).strip().upper() or "SI",
                })


def log_auditoria_db(conn, usuario, accion, detalle):
    conn.execute(text("""
        insert into auditoria(fecha_hora, usuario, accion, detalle)
        values(now() at time zone 'America/Santiago', :usuario, :accion, :detalle)
    """), {"usuario": usuario, "accion": accion, "detalle": detalle})


def log_auditoria(usuario, accion, detalle):
    engine = get_engine()
    with engine.begin() as conn:
        log_auditoria_db(conn, usuario, accion, detalle)


def asegurar_correlativos():
    anio = ahora_chile().year
    engine = get_engine()
    with engine.begin() as conn:
        for tipo in ["Memorándum", "Ordinario"]:
            key = tipo_key(tipo)
            max_num = conn.execute(text("select coalesce(max(numero),0) from documentos where tipo=:tipo and anio=:anio"), {"tipo": tipo, "anio": anio}).scalar() or 0
            conn.execute(text("""
                insert into correlativos(tipo, anio, ultimo_numero, actualizado_por, actualizado_en)
                values(:key, :anio, :max_num, 'sistema', now())
                on conflict(tipo, anio) do update
                set ultimo_numero = greatest(correlativos.ultimo_numero, excluded.ultimo_numero)
            """), {"key": key, "anio": anio, "max_num": int(max_num)})


def get_user(username: str):
    return db_query_one("select * from usuarios where usuario=:u", {"u": username})


def authenticate(username: str, password: str):
    user = get_user(username)
    if user and bool(user.get("activo", True)) and user["password_hash"] == hash_password(password):
        db_execute("update usuarios set ultimo_acceso=now() where usuario=:u", {"u": username})
        user["ultimo_acceso"] = fecha_str()
        return user
    return None


def cambiar_password(usuario, nueva_password, debe_cambiar=False):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("update usuarios set password_hash=:ph, debe_cambiar_password=:d where usuario=:u"), {"ph": hash_password(nueva_password), "d": bool(debe_cambiar), "u": usuario})
        log_auditoria_db(conn, usuario, "Cambio de contraseña", "El usuario cambió o recibió una nueva contraseña.")


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


@st.cache_data(ttl=300, show_spinner=False)
def read_funcionarios(include_inactivos=False):
    df = db_query_df("select id, oficina, seccion, funcionario, cargo, correo, activo from funcionarios order by oficina, funcionario")
    df = df.fillna("")
    if not include_inactivos:
        df = df[df["activo"].astype(str).str.upper().eq("SI")]
    return df.copy()


@st.cache_data(ttl=300, show_spinner=False)
def read_destinatarios(include_inactivos=False):
    df = db_query_df("select id, seccion, jefatura, nombre, correo, activo from destinatarios order by seccion, jefatura")
    df = df.fillna("")
    df = df[~df["seccion"].astype(str).str.lower().str.contains("gestión ambiental|gestion ambiental", na=False)]
    if not include_inactivos:
        df = df[df["activo"].astype(str).str.upper().eq("SI")]
    return df.copy()


def ultimo_documento(tipo):
    return db_query_one("""
        select * from documentos
        where tipo=:tipo and coalesce(estado,'Emitido') not like 'Anulado%'
        order by anio desc, numero desc limit 1
    """, {"tipo": tipo})


@st.cache_data(ttl=30, show_spinner=False)
def ultimos_documentos():
    df = db_query_df("""
        select distinct on (tipo) *
        from documentos
        where tipo in ('Memorándum','Ordinario')
          and coalesce(estado,'Emitido') not like 'Anulado%'
        order by tipo, anio desc, numero desc, id desc
    """)
    out = {}
    for _, r in df.fillna("").iterrows():
        out[str(r.get("tipo", ""))] = r.to_dict()
    return out


def generar_documento(tipo, oficina, funcionario, dest_row, materia, usuario_login):
    anio = ahora_chile().year
    key = tipo_key(tipo)
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("""
            insert into correlativos(tipo, anio, ultimo_numero, actualizado_por, actualizado_en)
            values(:key, :anio, 0, 'sistema', now())
            on conflict(tipo, anio) do nothing
        """), {"key": key, "anio": anio})
        row = conn.execute(text("select ultimo_numero from correlativos where tipo=:key and anio=:anio for update"), {"key": key, "anio": anio}).mappings().fetchone()
        nuevo = int(row["ultimo_numero"] or 0) + 1
        seccion = str(dest_row.get("seccion", "")).strip()
        jefatura = str(dest_row.get("jefatura", "")).strip()
        nombre = str(dest_row.get("nombre", "")).strip()
        destinatario = f"{jefatura} — {seccion}" + (f" — {nombre}" if nombre else "")
        conn.execute(text("""
            insert into documentos(
                tipo, numero, anio, fecha_hora, seccion_origen, oficina_origen,
                funcionario, seccion_destino, jefatura_destino, destinatario_nombre,
                destinatario, materia, usuario_creador, estado
            ) values(
                :tipo, :numero, :anio, now() at time zone 'America/Santiago', 'Sección Gestión Ambiental', :oficina,
                :funcionario, :seccion, :jefatura, :nombre,
                :destinatario, :materia, :usuario, 'Emitido'
            )
        """), {
            "tipo": tipo, "numero": nuevo, "anio": anio, "oficina": oficina,
            "funcionario": funcionario, "seccion": seccion, "jefatura": jefatura,
            "nombre": nombre, "destinatario": destinatario, "materia": materia.strip(),
            "usuario": usuario_login,
        })
        conn.execute(text("""
            update correlativos set ultimo_numero=:n, actualizado_por=:u, actualizado_en=now()
            where tipo=:key and anio=:anio
        """), {"n": nuevo, "u": usuario_login, "key": key, "anio": anio})
        log_auditoria_db(conn, usuario_login, "Genera documento", f"{tipo} N° {nuevo:03d}/{anio}")
    registros_df.clear()
    ultimos_documentos.clear()
    return nuevo, anio, fecha_str()


@st.cache_data(ttl=30, show_spinner=False)
def registros_df():
    df = db_query_df("""
        select
          id,
          tipo as tipo_documento,
          numero,
          anio,
          to_char(fecha_hora at time zone 'America/Santiago', 'YYYY-MM-DD HH24:MI:SS') as fecha_hora,
          coalesce(seccion_origen, 'Sección Gestión Ambiental') as seccion_origen,
          oficina_origen,
          funcionario,
          coalesce(seccion_destino, '') as departamento_destino,
          coalesce(jefatura_destino, '') as jefatura_destino,
          coalesce(destinatario_nombre, '') as destinatario_nombre,
          coalesce(destinatario, '') as destinatario,
          materia,
          usuario_creador as usuario_login,
          coalesce(estado, 'Emitido') as estado
        from documentos
        order by fecha_hora desc, id desc
    """)
    return df.fillna("")


def format_doc(row, tipo):
    if not row:
        return "Sin registros", "—", "—"
    fecha = row.get("fecha_hora")
    if fecha and not isinstance(fecha, str):
        try:
            fecha = fecha.astimezone(CHILE_TZ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            fecha = str(fecha)
    return f"N° {int(row['numero']):03d}/{row['anio']}", row.get("funcionario", "—"), fecha or "—"


def mostrar_inicio():
    st.markdown('<div class="hero-card">', unsafe_allow_html=True)
    col_logo, col_title = st.columns([1.15, 3.4], vertical_alignment="center")
    with col_logo:
        if LOGO_PATH.exists():
            st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
            st.image(str(LOGO_PATH), width=235)
            st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.markdown('<div class="main-title">Sistema de Gestión Documental</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Memorándums y Ordinarios<br>Sección de Gestión Ambiental · Departamento de Acción Sanitaria</div>', unsafe_allow_html=True)
        st.markdown('<span class="badge">SEREMI de Salud Región Metropolitana</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    ultimos = ultimos_documentos()
    memo = ultimos.get("Memorándum")
    ordn = ultimos.get("Ordinario")
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
    if funcionarios.empty or destinatarios.empty:
        st.error("Debe existir al menos un funcionario activo y un destinatario activo en Administración → Catálogos.")
        return

    st.markdown("""
    <div class="panel" style="margin-top:0;">
        <div style="font-weight:850;color:#003B7A;font-size:1.05rem;margin-bottom:6px;">Emisor institucional fijo</div>
        <div style="font-size:1.04rem;color:#1f2937;">Jefe(a) de la Sección Gestión Ambiental<br>Departamento de Acción Sanitaria · SEREMI de Salud Región Metropolitana</div>
        <div class="small-muted" style="margin-top:8px;">La oficina y el funcionario se registran solo para trazabilidad interna de quién toma el número.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("generar_documento_form", clear_on_submit=False):
        tipo = st.radio("Tipo de documento", ["Memorándum", "Ordinario"], horizontal=True)
        c1, c2 = st.columns(2)
        with c1:
            oficinas = sorted(funcionarios["oficina"].dropna().unique().tolist())
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
    c4.metric("Anulados", int(df["estado"].astype(str).str.startswith("Anulado").sum()))
    st.plotly_chart(px.histogram(df, x="mes", color="tipo_documento", barmode="group", title="Documentos por mes"), use_container_width=True)
    st.plotly_chart(px.histogram(df, y="oficina_origen", color="tipo_documento", title="Documentos por oficina"), use_container_width=True)
    st.plotly_chart(px.histogram(df, y="funcionario", color="tipo_documento", title="Documentos por funcionario"), use_container_width=True)
    st.plotly_chart(px.histogram(df, y="departamento_destino", color="tipo_documento", title="Documentos por sección destinataria"), use_container_width=True)


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
        cambiar_password(user["usuario"], nueva, False)
        st.session_state["user"] = get_user(user["usuario"])
        st.success("Contraseña actualizada correctamente.")
        st.rerun()


def page_correlativos():
    st.markdown('<div class="section-title">Administrar correlativos</div>', unsafe_allow_html=True)
    st.markdown('<div class="admin-help">Ingrese el <b>último número usado</b>; el próximo documento se generará sumando 1. Los cambios quedan guardados en Supabase.</div>', unsafe_allow_html=True)
    anio = st.number_input("Año", min_value=2024, max_value=2100, value=ahora_chile().year, step=1)
    asegurar_correlativos()
    corr = db_query_df("select tipo, ultimo_numero from correlativos where anio=:anio", {"anio": int(anio)})
    actual = {r["tipo"]: int(r["ultimo_numero"]) for _, r in corr.iterrows()} if not corr.empty else {}
    memo_actual = int(actual.get("MEMORANDUM", 0))
    ord_actual = int(actual.get("ORDINARIO", 0))
    c1, c2 = st.columns(2)
    c1.metric("Último Memorándum registrado", f"N° {memo_actual:03d}/{int(anio)}", f"Próximo: N° {memo_actual + 1:03d}/{int(anio)}")
    c2.metric("Último Ordinario registrado", f"N° {ord_actual:03d}/{int(anio)}", f"Próximo: N° {ord_actual + 1:03d}/{int(anio)}")
    with st.form("correlativos_form"):
        c1, c2 = st.columns(2)
        memo = c1.number_input("Último número utilizado de Memorándum", min_value=0, value=memo_actual, step=1)
        ordn = c2.number_input("Último número utilizado de Ordinario", min_value=0, value=ord_actual, step=1)
        ok = st.form_submit_button("Guardar correlativos")
    if ok:
        engine = get_engine()
        with engine.begin() as conn:
            for key, valor, ant, label in [("MEMORANDUM", int(memo), memo_actual, "Memorándum"), ("ORDINARIO", int(ordn), ord_actual, "Ordinario")]:
                conn.execute(text("""
                    insert into correlativos(tipo, anio, ultimo_numero, actualizado_por, actualizado_en)
                    values(:key, :anio, :valor, :u, now())
                    on conflict(tipo, anio) do update set ultimo_numero=:valor, actualizado_por=:u, actualizado_en=now()
                """), {"key": key, "anio": int(anio), "valor": valor, "u": st.session_state["user"]["usuario"]})
                if ant != valor:
                    log_auditoria_db(conn, st.session_state["user"]["usuario"], "Actualiza correlativo", f"{label} {anio}: {ant} → {valor}")
        st.success("Correlativos actualizados correctamente.")
        st.rerun()


def page_usuarios_admin():
    st.markdown('<div class="section-title">Administrar usuarios</div>', unsafe_allow_html=True)
    st.subheader("Crear nuevo usuario")
    funcionarios = read_funcionarios()
    oficinas = [""] + sorted(funcionarios["oficina"].unique().tolist()) if not funcionarios.empty else [""]
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
            elif get_user(usuario.strip()):
                st.error("Ese usuario ya existe.")
            else:
                engine = get_engine()
                with engine.begin() as conn:
                    conn.execute(text("""
                        insert into usuarios(usuario,nombre,rol,oficina,password_hash,debe_cambiar_password,activo,fecha_creacion)
                        values(:usuario,:nombre,:rol,:oficina,:ph,true,true,now())
                    """), {"usuario": usuario.strip(), "nombre": nombre.strip(), "rol": rol, "oficina": oficina, "ph": hash_password(temp)})
                    log_auditoria_db(conn, st.session_state["user"]["usuario"], "Crea usuario", f"Usuario creado: {usuario.strip()} ({rol})")
                st.success("Usuario creado correctamente.")
                st.markdown(f'<div class="credential-box"><b>Credenciales para entregar:</b><br>Usuario: <b>{usuario.strip()}</b><br>Contraseña temporal: <b>{temp}</b><br><br>Al ingresar por primera vez, el sistema obligará a cambiar la contraseña.</div>', unsafe_allow_html=True)
    st.subheader("Usuarios existentes")
    dfu = db_query_df("select usuario,nombre,rol,oficina,debe_cambiar_password,activo,to_char(ultimo_acceso at time zone 'America/Santiago', 'YYYY-MM-DD HH24:MI:SS') as ultimo_acceso from usuarios order by rol,nombre")
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
                    engine = get_engine()
                    with engine.begin() as conn:
                        conn.execute(text("update usuarios set password_hash=:ph, debe_cambiar_password=true where usuario=:u"), {"ph": hash_password(nueva), "u": sel})
                        log_auditoria_db(conn, st.session_state["user"]["usuario"], "Restablece contraseña", f"Usuario: {sel}")
                    st.success("Contraseña temporal asignada. El usuario deberá cambiarla al ingresar.")
        with c2:
            activo = st.selectbox("Estado", ["Activo", "Inactivo"])
            if st.button("Guardar estado"):
                engine = get_engine()
                with engine.begin() as conn:
                    conn.execute(text("update usuarios set activo=:a where usuario=:u"), {"a": activo == "Activo", "u": sel})
                    log_auditoria_db(conn, st.session_state["user"]["usuario"], "Cambia estado usuario", f"{sel}: {activo}")
                st.success("Estado actualizado.")
                st.rerun()


def save_funcionarios(df):
    df = df.fillna("").copy()
    df = df[df[["oficina", "funcionario"]].astype(str).apply(lambda r: any(x.strip() for x in r), axis=1)]
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("delete from funcionarios"))
        for _, r in df.iterrows():
            conn.execute(text("""
                insert into funcionarios(oficina,seccion,funcionario,cargo,correo,activo)
                values(:oficina,:seccion,:funcionario,:cargo,:correo,:activo)
            """), {
                "oficina": str(r.get("oficina", "")).strip(), "seccion": str(r.get("seccion", "Sección Gestión Ambiental")).strip() or "Sección Gestión Ambiental",
                "funcionario": str(r.get("funcionario", "")).strip(), "cargo": str(r.get("cargo", "")).strip(),
                "correo": str(r.get("correo", "")).strip(), "activo": str(r.get("activo", "SI")).strip().upper() if str(r.get("activo", "SI")).strip().upper() in ["SI", "NO"] else "SI",
            })
        log_auditoria_db(conn, st.session_state["user"]["usuario"], "Actualiza catálogo", f"Funcionarios. Filas: {len(df)}")
    read_funcionarios.clear()


def save_destinatarios(df):
    df = df.fillna("").copy()
    df = df[~df["seccion"].astype(str).str.lower().str.contains("gestión ambiental|gestion ambiental", na=False)]
    df = df[df[["seccion", "jefatura"]].astype(str).apply(lambda r: any(x.strip() for x in r), axis=1)]
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("delete from destinatarios"))
        for _, r in df.iterrows():
            conn.execute(text("""
                insert into destinatarios(seccion,jefatura,nombre,correo,activo)
                values(:seccion,:jefatura,:nombre,:correo,:activo)
            """), {
                "seccion": str(r.get("seccion", "")).strip(), "jefatura": str(r.get("jefatura", "")).strip(),
                "nombre": str(r.get("nombre", "")).strip(), "correo": str(r.get("correo", "")).strip(),
                "activo": str(r.get("activo", "SI")).strip().upper() if str(r.get("activo", "SI")).strip().upper() in ["SI", "NO"] else "SI",
            })
        log_auditoria_db(conn, st.session_state["user"]["usuario"], "Actualiza catálogo", f"Destinatarios. Filas: {len(df)}")
    read_destinatarios.clear()


def page_catalogos_admin():
    st.markdown('<div class="section-title">Catálogos del sistema</div>', unsafe_allow_html=True)
    st.markdown('<div class="admin-help">Desde esta pantalla puede agregar, editar o desactivar funcionarios y destinatarios. Los cambios quedan guardados permanentemente en Supabase.</div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["Funcionarios por oficina", "Destinatarios"])
    with t1:
        st.subheader("Funcionarios por oficina")
        cols_func = ["id", "oficina", "seccion", "funcionario", "cargo", "correo", "activo"]
        df_func = read_funcionarios(include_inactivos=True)[cols_func]
        edit_func = st.data_editor(df_func, use_container_width=True, hide_index=True, num_rows="dynamic", key="editor_funcionarios", column_config={"activo": st.column_config.SelectboxColumn("activo", options=["SI", "NO"], required=True)})
        if st.button("Guardar funcionarios", key="guardar_funcionarios"):
            save_funcionarios(edit_func)
            st.success("Funcionarios actualizados correctamente.")
            st.rerun()
    with t2:
        st.subheader("Destinatarios")
        cols_dest = ["id", "seccion", "jefatura", "nombre", "correo", "activo"]
        df_dest = read_destinatarios(include_inactivos=True)[cols_dest]
        edit_dest = st.data_editor(df_dest, use_container_width=True, hide_index=True, num_rows="dynamic", key="editor_destinatarios", column_config={"activo": st.column_config.SelectboxColumn("activo", options=["SI", "NO"], required=True)})
        if st.button("Guardar destinatarios", key="guardar_destinatarios"):
            save_destinatarios(edit_dest)
            st.success("Destinatarios actualizados correctamente.")
            st.rerun()


def page_auditoria_admin():
    st.markdown('<div class="section-title">Auditoría del sistema</div>', unsafe_allow_html=True)
    aud = db_query_df("select to_char(fecha_hora at time zone 'America/Santiago', 'YYYY-MM-DD HH24:MI:SS') as fecha_hora, usuario, accion, detalle from auditoria order by id desc limit 300")
    if aud.empty:
        st.info("No existen movimientos de auditoría.")
    else:
        st.dataframe(aud, use_container_width=True, hide_index=True)


def page_admin():
    st.markdown('<div class="section-title">Administración</div>', unsafe_allow_html=True)
    st.markdown('<div class="admin-help">Panel reservado para Administrador y Jefatura. Los registros, correlativos, usuarios, catálogos y auditoría quedan guardados en Supabase.</div>', unsafe_allow_html=True)
    docs_count = db_query_one("select count(*) as n from documentos")["n"]
    users_count = db_query_one("select count(*) as n from usuarios where activo=true")["n"]
    aud_count = db_query_one("select count(*) as n from auditoria")["n"]
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="admin-card"><div class="admin-card-title">Documentos registrados</div><div class="admin-card-text"><b>{docs_count}</b> documentos en el sistema.</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="admin-card"><div class="admin-card-title">Usuarios activos</div><div class="admin-card-text"><b>{users_count}</b> usuarios habilitados.</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="admin-card"><div class="admin-card-title">Auditoría</div><div class="admin-card-text"><b>{aud_count}</b> movimientos registrados.</div></div>', unsafe_allow_html=True)
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
                estado = f"Anulado - {motivo}" if motivo else "Anulado"
                engine = get_engine()
                with engine.begin() as conn:
                    conn.execute(text("update documentos set estado=:estado where id=:id"), {"estado": estado, "id": int(row["id"])})
                    log_auditoria_db(conn, st.session_state["user"]["usuario"], "Anula documento", etiqueta)
                registros_df.clear()
                ultimos_documentos.clear()
                st.success("Registro anulado.")
                st.rerun()
        else:
            st.info("No existen documentos para anular.")
    with tab5:
        page_auditoria_admin()


def main():
    init_once()
    mostrar_inicio()
    if "user" not in st.session_state:
        login_box()
        return
    user = st.session_state["user"]
    if bool(user.get("debe_cambiar_password", False)):
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
    st.caption("Versión 2.1 optimizada Supabase · SEREMI de Salud Región Metropolitana · Departamento de Acción Sanitaria · Sección Gestión Ambiental")


if __name__ == "__main__":
    main()
