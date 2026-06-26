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

@st.cache_data(ttl=5) 
def cargar_datos_desde_nube(url):
    # Cargamos el dataframe completo sin asumir nombres de columnas
    df = pd.read_csv(url, header=None, engine="python")
    return df

try:
    df_real = cargar_datos_desde_nube(URL_GOOGLE_SHEETS_CSV)
except:
    st.error("❌ No se pudo conectar con el reporte en la nube.")
    st.stop()

# Función robusta para limpiar cualquier celda numérica de texto
def limpiar_y_convertir_numero(raw_val):
    try:
        if pd.isna(raw_val): return 0.0
        string_limpio = str(raw_val).replace("$", "").replace("%", "").replace(" ", "")
        if not string_limpio: return 0.0
        
        if "," in string_limpio and "." in string_limpio:
            string_limpio = string_limpio.replace(".", "").replace(",", ".")
        elif "," in string_limpio:
            string_limpio = string_limpio.replace(",", ".")
            
        return float(string_limpio)
    except:
        return 0.0

# NUEVA FUNCIÓN DE BÚSQUEDA GLOBAL MULTICOLUMNA
def buscar_valor_numerico_global(lista_palabras_clave):
    try:
        for texto in lista_palabras_clave:
            texto_buscado = texto.upper().strip()
            # Buscamos la palabra clave en cualquier columna del archivo
            for col in df_real.columns:
                match = df_real[df_real[col].astype(str).str.upper().str.contains(texto_buscado, na=False)]
                if not match.empty:
                    # Si la palabra clave está en la columna actual, el número debería estar en la siguiente columna a la derecha
                    col_index = list(df_real.columns).index(col)
                    if col_index + 1 < len(df_real.columns):
                        valor_derecha = match.iloc[0, col_index + 1]
                        return limpiar_y_convertir_numero(valor_derecha)
    except: pass
    return 0.0

# Búsqueda de variables principales con el nuevo motor global
total_cobrado_dia_anterior = buscar_valor_numerico_global(["TOTAL COBRADO", "COBRADO"]) 
morosidad_total = buscar_valor_numerico_global(["% EN MORA", "MOROSIDAD TOTAL"])     
creditos_a_cobrar = buscar_valor_numerico_global(["CRÉDITOS A COBRAR", "CREDITOS A COBRAR"])

efectivo = buscar_valor_numerico_global(["EFECTIVO"])
macro_fci = buscar_valor_numerico_global(["MACRO+FCI", "MACRO"])
debito_suarez = buscar_valor_numerico_global(["DÉBITO + CNEL. SUAREZ", "DEBITO", "SUAREZ"])
total_caja = buscar_valor_numerico_global(["TOTAL CAJA", "CAJA TOTAL"])

# ==========================================
# RENDERIZADO DEL DASHBOARD
# ==========================================
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric(label="💰 Total Cobrado", value=f"$ {total_cobrado_dia_anterior:,.2f}")
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
st.subheader("🚨 PORCENTAJE DE MORA POR MES-AÑO")

meses_validos = [
    "ENERO 2025", "FEBRERO 2025", "MARZO 2025", "ABRIL 2025", "MAYO 2025", "JUNIO 2025",
    "JULIO 2025", "AGOSTO 2025", "SEPTIEMBRE 2025", "OCTUBRE 2025", "NOVIEMBRE 2025", "DICIEMBRE 2025",
    "ENERO 2026", "FEBRERO 2026", "MARZO 2026", "ABRIL 2026", "MAYO 2026", "JUNIO 2026"
]

# Buscamos los meses válidos inspeccionando todas las columnas disponibles
mascara_meses = df_real.map(lambda cell: str(cell).strip().upper() in meses_validos).any(axis=1)
df_mora_raw = df_real[mascara_meses].copy()

registros_mora = []
for idx, fila in df_mora_raw.iterrows():
    for col_idx, celda in enumerate(fila):
        val_str = str(celda).strip().upper()
        if val_str in meses_validos and (col_idx + 1 < len(fila)):
            val_num = limpiar_y_convertir_numero(fila.iloc[col_idx + 1])
            if 0 < val_num < 1.0:
                val_num = val_num * 100
            registros_mora.append({"Período Comercial": val_str, "% En Mora": val_num})

df_mora = pd.DataFrame(registros_mora) if registros_mora else pd.DataFrame(columns=["Período Comercial", "% En Mora"])

filtro_mora = st.selectbox("🔍 Filtrar meses por nivel de criticidad en la mora:", ["Todos los meses", "Mora Crítica (Mayor a 12%)", "Mora Alerta (10% a 12%)", "Mora Controlada (Menor a 10%)"])

if not df_mora.empty:
    if filtro_mora == "Mora Crítica (Mayor a 12%)": 
        df_filtrado = df_mora[df_mora["% En Mora"] > 12.0]
    elif filtro_mora == "Mora Alerta (10% a 12%)": 
        df_filtrado = df_mora[(df_mora["% En Mora"] >= 10.0) & (df_mora["% En Mora"] <= 12.0)]
    elif filtro_mora == "Mora Controlada (Menor a 10%)": 
        df_filtrado = df_mora[df_mora["% En Mora"] < 10.0]
    else: 
        df_filtrado = df_mora

    def colorear_celda(val):
        if val > 12.0: 
            return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
        elif val > 10.0: 
            return 'background-color: #fef3c7; color: #92400e;'
        return 'background-color: #e8f5e9; color: #1b5e20;'

    df_estilizado = (df_filtrado.style.map(colorear_celda, subset=["% En Mora"]).format({"% En Mora": "{:.2f}%"}))

    col_tabla, col_grafico = st.columns([4, 5])
    with col_tabla:
        st.markdown("**Matriz Detallada:**")
        st.dataframe(df_estilizado, use_container_width=True, height=380)
    with col_grafico:
        st.markdown("**Tendencia Histórica:**")
        st.line_chart(df_mora.set_index("Período Comercial"), height=380)
else:
    st.info("ℹ️ No se detectaron filas históricas de meses comerciales en el formato esperado dentro del archivo.")
