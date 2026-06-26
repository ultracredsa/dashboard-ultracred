import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN VISUAL DASHBOARD PROFESIONAL
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
# VINCULACIÓN CON LA NUBE
# ==========================================
URL_GOOGLE_SHEETS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYzZVnpesIun4fZkyvu2G1wOytYnrMJYn7rv9B87Ko3kxzhN1XGw3VLmvGrUNveg/pub?output=csv"

@st.cache_data(ttl=2) 
def cargar_datos_desde_nube(url):
    df = pd.read_csv(url, header=None, engine="python")
    # Limpieza básica de espacios en todo el dataframe para evitar fallos de coincidencia
    df = df.fillna("")
    return df

try:
    df_real = cargar_datos_desde_nube(URL_GOOGLE_SHEETS_CSV)
except:
    st.error("❌ No se pudo conectar con el reporte en la nube.")
    st.stop()

# Función ultra-segura de conversión
def forzar_numero(val):
    try:
        s = str(val).strip().replace("$", "").replace("%", "").replace(" ", "")
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        return float(s)
    except:
        return None

# NUEVO BUSCADOR COMPRENSIVO (Busca por palabra clave en cualquier celda y extrae el primer número de esa fila)
def obtener_valor_kpi(lista_claves):
    for fila_idx, fila in df_real.iterrows():
        fila_texto = " ".join(fila.astype(str)).upper()
        # Si la fila contiene alguna de nuestras palabras clave
        if any(clave.upper() in fila_texto for clave in lista_claves):
            # Recorremos los elementos de la fila para encontrar el valor numérico
            for celda in fila:
                num = forzar_numero(celda)
                if num is not None and num != 0.0:
                    return num
    return 0.0

# Búsqueda de variables con alias cortos y directos para maximizar aciertos
total_cobrado_dia_anterior = obtener_valor_kpi(["COBRADO", "TOTAL COBRADO"]) 
morosidad_total = obtener_valor_kpi(["MORA", "MOROSIDAD", "% EN MORA"])     
creditos_a_cobrar = obtener_valor_kpi(["COBRAR", "CRÉDITOS A COBRAR"])

efectivo = obtener_valor_kpi(["EFECTIVO"])
macro_fci = obtener_valor_kpi(["MACRO"])
debito_suarez = obtener_valor_kpi(["SUAREZ", "DÉBITO"])
total_caja = obtener_valor_kpi(["TOTAL CAJA", "CAJA TOTAL"])

# Normalizar porcentaje de morosidad si viene en formato decimal
if 0 < morosidad_total < 1.0:
    morosidad_total = morosidad_total * 100.0

# ==========================================
# RENDERIZADO DEL DASHBOARD
# ==========================================
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric(label="💰 Total Cobrado", value=f"$ {total_cobrado_dia_anterior:,.2f}")
with col_kpi2:
    st.metric(label="📊 Porcentaje Morosidad Total", value=f"{morosidad_total:.2f}%")
with col_kpi3:
    st.metric(label="💼 Créditos a Cobrar", value=f"$ {creditos_a_cobrar:,.2f}")

st.markdown("---")
st.subheader("🏦 Composición y Disponibilidad de Caja")
col_caja1, col_caja2, col_caja3, col_caja4 = st.columns(4)

with col_caja1:
    st.markdown(f"<div class='card-caja' style='border-left-color: #10b981;'><span style='color:#64748b; font-size:0.85rem; font-weight:700;'>💵 EFECTIVO</span><br><span style='font-size:1.5rem; font-weight:800; color:#059669;'>$ {efectivo:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja2:
    st.markdown(f"<div class='card-caja' style='border-left-color: #3b82f6;'><span style='color:#64748b; font-size:0.85rem; font-weight:700;'>🏛️ BANCOS (MACRO + FCI)</span><br><span style='font-size:1.5rem; font-weight:800; color:#2563eb;'>$ {macro_fci:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja3:
    st.markdown(f"<div class='card-caja' style='border-left-color: #8b5cf6;'><span style='color:#64748b; font-size:0.85rem; font-weight:700;'>💳 DÉBITO + CNEL. SUAREZ</span><br><span style='font-size:1.5rem; font-weight:800; color:#7c3aed;'>$ {debito_suarez:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja4:
    st.markdown(f"<div class='card-caja' style='border-left-color: #475569;'><span style='color:#64748b; font-size:0.85rem; font-weight:700;'>📈 TOTAL GENERAL EN CAJA</span><br><span style='font-size:1.5rem; font-weight:800; color:#1e293b;'>$ {total_caja:,.2f}</span></div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("🚨 PORCENTAJE DE MORA POR MES-AÑO")

meses_validos = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]

registros_mora = []
for idx, fila in df_real.iterrows():
    fila_str = " ".join(fila.astype(str)).upper()
    if any(m in fila_str for m in meses_validos) and ("2025" in fila_str or "2026" in fila_str):
        # Detectar el nombre del período
        periodo = ""
        for m in meses_validos:
            if m in fila_str:
                anio = "2026" if "2026" in fila_str else "2025"
                periodo = f"{m} {anio}"
                break
        
        for celda in fila:
            num = forzar_numero(celda)
            if num is not None and 0.0 < num < 100.0:
                val_mora = num * 100.0 if num < 1.0 else num
                registros_mora.append({"Período Comercial": periodo, "% En Mora": val_mora})
                break

if registros_mora:
    df_mora = pd.DataFrame(registros_mora).drop_duplicates(subset=["Período Comercial"])
    filtro_mora = st.selectbox("🔍 Filtrar meses por nivel de criticidad en la mora:", ["Todos los meses", "Mora Crítica (Mayor a 12%)", "Mora Alerta (10% a 12%)", "Mora Controlada (Menor a 10%)"])

    if filtro_mora == "Mora Crítica (Mayor a 12%)": df_filtrado = df_mora[df_mora["% En Mora"] > 12.0]
    elif filtro_mora == "Mora Alerta (10% a 12%)": df_filtrado = df_mora[(df_mora["% En Mora"] >= 10.0) & (df_mora["% En Mora"] <= 12.0)]
    elif filtro_mora == "Mora Controlada (Menor a 10%)": df_filtrado = df_mora[df_mora["% En Mora"] < 10.0]
    else: df_filtrado = df_mora

    def colorear_celda(val):
        if val > 12.0: return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
        elif val > 10.0: return 'background-color: #fef3c7; color: #92400e;'
        return 'background-color: #e8f5e9; color: #1b5e20;'

    df_estilizado = (df_filtrado.style.map(colorear_celda, subset=["% En Mora"]).format({"% En Mora": "{:.2f}%"}))

    col_tabla, col_grafico = st.columns([4, 5])
    with col_tabla:
        st.dataframe(df_estilizado, use_container_width=True)
    with col_grafico:
        st.line_chart(df_mora.set_index("Período Comercial"))

# ==========================================
# REVISIÓN DE ESTRUCTURA REAL (SOLO PARA DIAGNÓSTICO)
# ==========================================
st.markdown("---")
with st.expander("🔍 PASO DE CONTROL: Ver cómo Streamlit está leyendo tu Planilla"):
    st.write("Acá abajo podés ver exactamente la matriz de datos que viene desde tu Google Sheets. Revisá en qué filas y columnas están los valores de Efectivo, Cobrado, etc.:")
    st.dataframe(df_real)
