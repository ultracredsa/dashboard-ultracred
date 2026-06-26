import streamlit as st
import pandas as pd

# =====================================================================
# 1. CONFIGURACIÓN VISUAL DASHBOARD PROFESIONAL
# =====================================================================
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
    .card-compensacion {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border-top: 4px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin-bottom: 10px;
    }
    .fecha-kpi {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 500;
        margin-top: -5px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📈 Panel de Control Operativo")
st.caption("Conectado en tiempo real a Google Sheets (Nube)")
st.markdown("---")

# =====================================================================
# 2. VINCULACIÓN CON LA NUBE
# =====================================================================
URL_GOOGLE_SHEETS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYzZVnpesIun4fZkyvu2G1wOytYnrMJYn7rv9B87Ko3kxzhN1XGw3VLmvGrUNveg/pub?output=csv"

@st.cache_data(ttl=2) 
def cargar_datos_desde_nube(url):
    try:
        df = pd.read_csv(url, header=None, engine="python")
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(f"❌ No se pudo conectar con el reporte en la nube. Error: {e}")
        st.stop()

df_real = cargar_datos_desde_nube(URL_GOOGLE_SHEETS_CSV)

# =====================================================================
# 3. PROCESAMIENTO Y PARSING DE NÚMEROS (BLINDADO REGIONAL ARGENTINA)
# =====================================================================
def forzar_numero(val):
    try:
        s = str(val).strip().replace("$", "").replace("%", "").replace(" ", "")
        if not s:
            return 0.0
        
        if "," in s:
            s = s.replace(".", "").replace(",", ".")
            return float(s)
        
        if "." in s:
            if s.count(".") > 1:
                s = s.replace(".", "")
            else:
                partes = s.split(".")
                if len(partes[1]) == 3:
                    s = s.replace(".", "")
                    
        return float(s)
    except:
        return 0.0

def obtener_valor_kpi(lista_claves):
    for fila_idx, fila in df_real.iterrows():
        fila_texto = " ".join(fila.astype(str)).upper()
        if any(clave.upper() in fila_texto for clave in lista_claves):
            for celda in reversed(fila):
                num = forzar_numero(celda)
                if num is not None and num != 0.0:
                    return num
    return 0.0

# =====================================================================
# 4. EXTRACCIÓN DE DATOS DINÁMICOS
# =====================================================================
try:
    fecha_referencia = str(df_real.iloc[0, 1]).strip()
except:
    fecha_referencia = "Fecha no disponible"

total_cobrado_dia_anterior = obtener_valor_kpi(["COBRADO", "TOTAL COBRADO"]) 
morosidad_total = obtener_valor_kpi(["MORA TOTAL", "MOROSIDAD ACUMULADA", "% EN MORA"])     
creditos_a_cobrar = obtener_valor_kpi(["COBRAR", "CRÉDITOS A COBRAR"])

efectivo = obtener_valor_kpi(["EFECTIVO"])
macro_fci = obtener_valor_kpi(["MACRO"])
debito_suarez = obtener_valor_kpi(["SUAREZ", "DÉBITO"])
total_caja = obtener_valor_kpi(["TOTAL CAJA", "CAJA TOTAL"])

if 0 < morosidad_total < 1.0:
    morosidad_total = morosidad_total * 100.0

# =====================================================================
# 5. RENDERIZADO DEL DASHBOARD (INTERFAZ)
# =====================================================================
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric(label="💰 Total Cobrado", value=f"$ {total_cobrado_dia_anterior:,.2f}")
    st.markdown(f"<p class='fecha-kpi'>📅 Ref: {fecha_referencia}</p>", unsafe_allow_html=True)
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

# =====================================================================
# REFACTORIZADO: SECCIÓN DE PRÓXIMAS COMPENSACIONES (FILAS 119 A 122)
# =====================================================================
st.markdown("---")
st.subheader("📅 Próximas Compensaciones")

try:
    # Mapeo exacto indexando en base 0 para Pandas:
    # Fila Excel 119 es índice 118, Fila 120 es 119, Fila 121 es 120, Fila 122 es 121
    # Columna A es índice 0 (Información/Fecha), Columna B es índice 1 (Monto)
    comp_datos = [
        {"fecha": str(df_real.iloc[118, 0]).strip(), "monto": forzar_numero(df_real.iloc[118, 1])},
        {"fecha": str(df_real.iloc[119, 0]).strip(), "monto": forzar_numero(df_real.iloc[119, 1])},
        {"fecha": str(df_real.iloc[120, 0]).strip(), "monto": forzar_numero(df_real.iloc[120, 1])},
        {"fecha": str(df_real.iloc[121, 0]).strip(), "monto": forzar_numero(df_real.iloc[121, 1])},
    ]

    # Creamos 4 columnas en la pantalla para poner cada tarjeta de compensación lado a lado
    col_comp1, col_comp2, col_comp3, col_comp4 = st.columns(4)
    columnas_lista = [col_comp1, col_comp2, col_comp3, col_comp4]

    for i, item in enumerate(comp_datos):
        with columnas_lista[i]:
            if item["fecha"] and item["monto"] > 0:
                st.markdown(f"""
                    <div class='card-compensacion'>
                        <span style='color:#4b5563; font-size:0.85rem; font-weight:700; text-transform:uppercase;'>⏳ {item['fecha']}</span><br>
                        <span style='font-size:1.4rem; font-weight:800; color:#1d4ed8;'>$ {item['monto']:,.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Si la celda está vacía o en cero en la planilla, muestra un indicador sutil
                st.markdown("""
                    <div class='card-compensacion' style='border-top-color: #e5e7eb;'>
                        <span style='color:#9ca3af; font-size:0.85rem;'>Sin compensaciones programadas</span>
                    </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.warning("⚠️ Nota: Asegurate de tener datos cargados en el rango de filas 119 a 122 (Columnas A y B) en tu Google Sheets.")

# =====================================================================
# 6. PORCENTAJE DE MORA POR MES-AÑO
# =====================================================================
st.markdown("---")
st.subheader("🚨 PORCENTAJE DE MORA POR MES-AÑO")

dic_meses = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
    "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
}

registros_mora = []
for idx, fila in df_real.iterrows():
    fila_str = " ".join(fila.astype(str)).upper()
    if any(m in fila_str for m in dic_meses.keys()) and ("2025" in fila_str or "2026" in fila_str):
        periodo = ""
        mes_num = 1
        anio = 2025
        
        for m, n in dic_meses.items():
            if m in fila_str:
                anio = 2026 if "2026" in fila_str else 2025
                periodo = f"{m} {anio}"
                mes_num = n
                break
        
        for celda in reversed(fila):
            num = forzar_numero(celda)
            if num is not None and 0.0 < num < 100.0:
                val_mora = num * 100.0 if num < 1.0 else num
                registros_mora.append({
                    "Período Comercial": periodo, 
                    "% En Mora": val_mora,
                    "Orden_Fecha": anio * 100 + mes_num
                })
                break

if registros_mora:
    df_mora = pd.DataFrame(registros_mora).drop_duplicates(subset=["Período Comercial"])
    df_mora = df_mora.sort_values(by="Orden_Fecha").reset_index(drop=True)

    filtro_mora = st.selectbox("🔍 Filtrar meses por nivel de criticidad en la mora:", 
                               ["Todos los meses", "Mora Crítica (Mayor a 12%)", "Mora Alerta (10% a 12%)", "Mora Controlada (Menor a 10%)"])

    if filtro_mora == "Mora Crítica (Mayor a 12%)": df_filtrado = df_mora[df_mora["% En Mora"] > 12.0]
    elif filtro_mora == "Mora Alerta (10% a 12%)": df_filtrado = df_mora[(df_mora["% En Mora"] >= 10.0) & (df_mora["% En Mora"] <= 12.0)]
    elif filtro_mora == "Mora Controlada (Menor a 10%)": df_filtrado = df_mora[df_mora["% En Mora"] < 10.0]
    else: df_filtrado = df_mora

    def colorear_celda(val):
        if val > 12.0: return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
        elif val > 10.0: return 'background-color: #fef3c7; color: #92400e;'
        return 'background-color: #e8f5e9; color: #1b5e20;'

    df_tabla_render = df_filtrado[["Período Comercial", "% En Mora"]]
    df_estilizado = (df_tabla_render.style.map(colorear_celda, subset=["% En Mora"]).format({"% En Mora": "{:.2f}%"}))

    col_tabla, col_grafico = st.columns([4, 5])
    with col_tabla:
        st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
    with col_grafico:
        st.line_chart(df_mora.set_index("Período Comercial")["% En Mora"])

# =====================================================================
# 7. REVISIÓN DE ESTRUCTURA REAL (SOLO PARA DIAGNÓSTICO)
# =====================================================================
st.markdown("---")
with st.expander("🔍 PASO DE CONTROL: Ver cómo Streamlit está leyendo tu Planilla"):
    st.write("Acá abajo podés ver exactamente la matriz de datos que viene desde tu Google Sheets:")
    st.dataframe(df_real)
