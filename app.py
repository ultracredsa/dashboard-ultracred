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
# VINCULACIÓN CON LA NUBE (REEMPLAZÁ ESTA URL)
# ==========================================
# PEGÁ ACÁ ADENTRO el link de "Publicar como CSV" que te dio Google Sheets en la Etapa 1
URL_GOOGLE_SHEETS_CSV = "CONECTA_AQUÍ_TU_LINK_DE_GOOGLE"

@st.cache_data(ttl=10) # Se actualiza automáticamente cada 10 segundos si hay cambios
def cargar_datos_desde_nube(url):
    # Al ser un CSV web, lo leemos con read_csv indicando que no tiene encabezado fijo
    df = pd.read_csv(url, header=None, engine="python")
    df[0] = df[0].astype(str).str.strip().str.upper()
    return df

try:
    df_real = cargar_datos_desde_nube(URL_GOOGLE_SHEETS_CSV)
except:
    st.error("❌ No se pudo conectar con el reporte en la nube.")
    st.info("Verificá haber pegado correctamente el link de 'Publicar como CSV' de Google Sheets.")
    st.stop()

def buscar_valor_numerico(texto):
    try:
        fila = df_real[df_real[0] == texto.upper().strip()]
        if not fila.empty:
            raw_val = fila.iloc[0, 1]
            if pd.isna(raw_val): return 0.0
            if isinstance(raw_val, str):
                string_limpio = raw_val.replace("$", "").replace(" ", "")
                if "," in string_limpio and "." in string_limpio:
                    string_limpio = string_limpio.replace(".", "").replace(",", ".")
                elif "." in string_limpio and string_limpio.count(".") > 1:
                    string_limpio = string_limpio.replace(".", "")
                return float(string_limpio)
            return float(raw_val)
    except: pass
    return 0.0

# Mapeo de variables
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
st.subheader("🚨 Análisis de Mora por Cosecha Mensual")

meses_validos = [
    "ENERO 2025", "FEBRERO 2025", "MARZO 2025", "ABRIL 2025", "MAYO 2025", "JUNIO 2025",
    "JULIO 2025", "AGOSTO 2025", "SEPTIEMBRE 2025", "OCTUBRE 2025", "NOVIEMBRE 2025", "DICIEMBRE 2025",
    "ENERO 2026", "FEBRERO 2026", "MARZO 2026", "ABRIL 2026", "MAYO 2026", "JUNIO 2026"
]

df_mora = df_real[df_real[0].isin(meses_validos)].copy()
df_mora.columns = ["Período Comercial", "% En Mora"]

df_mora["% En Mora"] = df_mora["% En Mora"].apply(lambda x: float(x)*100 if 0 < float(x) < 1.0 else float(x))

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
    st.markdown("**Matriz Detallada:**")
    st.dataframe(df_estilizado, use_container_width=True, height=380)
with col_grafico:
    st.markdown("**Tendencia Histórica:**")
    st.line_chart(df_mora.set_index("Período Comercial"), height=380)