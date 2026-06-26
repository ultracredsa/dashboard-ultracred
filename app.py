import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL ESTILO CÁLIDO / DASHBOARD PROFESIONAL
st.set_page_config(page_title="UltraCred - Dashboard de Cobranzas", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
    }
    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.8rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
    }
    .card-caja {
        background: linear-gradient(135deg, #ffffff 0%, #fffdf9 100%);
        padding: 18px;
        border-radius: 14px;
        border-left: 5px solid #f59e0b;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 12px;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Panel de Control Operativo")
st.caption("Conectado en tiempo real a Google Sheets (Nube)")
st.markdown("---")

# ==========================================
# VINCULACIÓN CON LA NUBE (LINK REAL INCORPORADO)
# ==========================================
URL_GOOGLE_SHEETS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYzZVnpesIun4fZkyvu2G1wOytYnrMJYn7rv9B87Ko3kxzhN1XGw3VLmvGrUNveg/pub?output=csv"

@st.cache_data(ttl=5) # Se actualiza automáticamente cada 5 segundos si hay cambios
def cargar_datos_desde_nube(url):
    df = pd.read_csv(url, header=None, engine="python")
    df[0] = df[0].astype(str).str.strip().str.upper()
    return df

try:
    df_real = cargar_datos_desde_nube(URL_GOOGLE_SHEETS_CSV)
except:
    st.error("❌ No se pudo conectar con el reporte en la nube.")
    st.info("Verificá haber pegado correctamente el link de 'Publicar como CSV' de Google Sheets.")
    st.stop()

# Función auxiliar robusta para limpiar cualquier celda numérica de texto
def limpiar_y_convertir_numero(raw_val):
    try:
        if pd.isna(raw_val): return 0.0
        string_limpio = str(raw_val).replace("$", "").replace("%", "").replace(" ", "")
        if not string_limpio: return 0.0
        
        # Manejo de formatos decimales regionales (puntos y comas de Argentina)
        if "," in string_limpio and "." in string_limpio:
            string_limpio = string_limpio.replace(".", "").replace(",", ".")
        elif "," in string_limpio:
            string_limpio = string_limpio.replace(",", ".")
            
        return float(string_limpio)
    except:
        return 0.0

def buscar_valor_numerico(texto):
    try:
        fila = df_real[df_real[0] == texto.upper().strip()]
        if not fila.empty:
            return limpiar_y_convertir_numero(fila.iloc[0, 1])
    except: pass
    return 0.0

# Mapeo de variables según tu jerarquía de importancia
total_cobrado_dia_anterior = buscar_valor_numerico("TOTAL COBRADO") 
morosidad_total = buscar_valor_numerico("% EN MORA")     
creditos_a_cobrar = buscar_valor_numerico("CRÉDITOS A COBRAR")

efectivo = buscar_valor_numerico("EFECTIVO")
macro_fci = buscar_valor_numerico("MACRO+FCI")
debito_suarez = buscar_valor_numerico("DÉBITO + CNEL. SUAREZ")
total_caja = buscar_valor_numerico("TOTAL CAJA")

# ==========================================
# RENDERIZADO DEL DASHBOARD (JERARQUÍA COMPLETA)
# ==========================================
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric(label="💰 Total Cobrado (Día Anterior)", value=f"$ {total_cobrado_dia_anterior:,.2f}")
with col_kpi2:
    mora_display = morosidad_total * 100 if 0 < morosidad_total < 1.0 else morosidad_total
    st.metric(label="📊 Porcentaje Morosidad Total", value=f"{mora_display:.2f}%")
with col_kpi3:
    st.metric(label="💼 Créditos a Cobrar", value=f"$ {creditos_a_cobrar:,.2f}")

st.markdown("---")
st.subheader("🏦 Composición y Disponibilidad de Caja")
col_
