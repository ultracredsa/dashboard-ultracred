import streamlit as st
import pandas as pd

# =====================================================================
# 1. CONFIGURACIÓN VISUAL: DISEÑO DE ALTO CONTRASTE INSTITUTIONAL COMPACTO
# =====================================================================
st.set_page_config(page_title="UltraCred - Dashboard de Cobranzas", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    /* Fondo general de la app (Gris claro premium) */
    .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #f8fafc !important;
    }
    
    /* Reducir espacio muerto en la parte superior de la página */
    [data-testid="stAppViewContainer"] > section:first-child > div:first-child {
        padding-top: 1.5rem !important;
    }
    
    /* Títulos y textos en color azul oscuro/pizarra */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #0f172a !important;
        margin-bottom: 0.1rem !important;
    }
    
    /* Achicar espacio de separación nativo entre bloques de Streamlit */
    [data-testid="stVerticalBlock"] {
        gap: 0.6rem !important;
    }
    
    /* Ajuste fino para los subtítulos (st.subheader) originales */
    .st-emotion-cache-12w0qpk, h2, h3 {
        margin-top: 0.4rem !important;
        margin-bottom: 0.2rem !important;
        font-weight: 700 !important;
    }
    
    /* Tarjetas de Métricas Internas Ultra-Compactas */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 12px 16px !important;
        border-radius: 10px;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetric"] label {
        color: #475569 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.7rem !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
    }
    
    /* Bloque Especial de Créditos a Cobrar Compacto */
    .card-detalle-credito-nueva {
        background-color: #ffffff !important;
        padding: 12px 16px;
        border-radius: 10px;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    .linea-credito {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 4px 0;
        border-bottom: 1px solid #f1f5f9 !important;
    }
    .linea-credito:last-child {
        border-bottom: none !important;
    }
    .lbl-credito {
        color: #475569 !important;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .val-credito {
        color: #0f172a !important;
        font-size: 0.95rem;
        font-weight: 800;
    }
    
    /* Tarjetas de Caja Activa Compactas */
    .card-caja {
        background-color: #ffffff !important;
        padding: 12px;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    
    /* Tarjetas de Compensaciones Compactas */
    .card-compensacion {
        background-color: #ffffff !important;
        padding: 10px;
        border-radius: 8px;
        border-top: 3px solid #3b82f6;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        text-align: center;
        border-left: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. VINCULACIÓN CON LA NUBE Y CARGA INICIAL
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

# Extracción inmediata de la fecha de referencia para el título superior
try:
    fecha_referencia = str(df_real.iloc[0, 1]).strip()
except:
    fecha_referencia = "Fecha no disponible"

# TÍTULO DE LA APP CON FECHA INTEGRADA AL LADO
st.markdown(f"<h1>📈 Reporte UltraCred <span style='font-size: 1.3rem; color: #64748b; font-weight: 500; margin-left: 10px;'>({fecha_referencia})</span></h1>", unsafe_allow_html=True)
st.caption("Conectado en tiempo real a Google Sheets (Nube)")

# =====================================================================
# 3. PROCESAMIENTO DE NÚMEROS
# =====================================================================
def forzar_numero(val):
    if not val: return 0.0
    s = str(val).strip().upper().replace("$", "").replace("%", "").replace(" ", "")
    if not s: return 0.0
    try:
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."): s = s.replace(".", "").replace(",", ".")
            else: s = s.replace(",", "")
        elif "," in s:
            if s.count(",") == 1 and len(s.split(",")[1]) <= 2: s = s.replace(",", ".")
            else: s = s.replace(",", "")
        elif "." in s and s.count(".") > 1: s = s.replace(".", "")
        elif "." in s and len(s.split(".")[1]) == 3: s = s.replace(".", "")
        return float(s)
    except:
        return 0.0

def obtener_valor_kpi(lista_claves):
    for fila_idx, fila in df_real.iterrows():
        fila_texto = " ".join(fila.astype(str)).upper()
        if any(clave.upper() in fila_texto for clave in lista_claves):
            for celda in fila:
                celda_str = str(celda).strip().upper()
                if any(clave.upper() in celda_str for clave in lista_claves): continue
                num = forzar_numero(celda)
                if num != 0.0: return num
    return 0.0

# =====================================================================
# 4. EXTRACCIÓN MAESTRA DE DATOS
# =====================================================================
try: capital_vendido = forzar_numero(df_real.iloc[1, 1])
except: capital_vendido = 0.0
if capital_vendido == 0.0:
    capital_vendido = obtener_valor_kpi(["VENTA (K)", "VENTA (K) DEL DÍA"])

intereses_convenios = obtener_valor_kpi(["INTERESES CONVENIOS", "CONVENIOS"])
total_cobrado_dia_anterior = obtener_valor_kpi(["TOTAL COBRADO", "COBRADO"]) 

morosidad_total = obtener_valor_kpi(["MORA TOTAL", "% EN MORA"])     
efectivo = obtener_valor_kpi(["EFECTIVO"])
macro_fci = obtener_valor_kpi(["MACRO"])
debito_suarez = obtener_valor_kpi(["SUAREZ", "DÉBITO"])
total_caja = obtener_valor_kpi(["TOTAL CAJA", "CAJA TOTAL"])

# Ajuste por si la morosidad total viene como decimal (ej: 0.05 en lugar de 5.0)
if 0 < morosidad_total < 1.0: 
    morosidad_total = morosidad_total * 100.0

try:
    monto_vencido_lbl = str(df_real.iloc[90, 0]).strip() 
    monto_vencido_val = forzar_numero(df_real.iloc[90, 1])
    cobrado_lbl = str(df_real.iloc[91, 0]).strip()       
    cobrado_val = forzar_numero(df_real.iloc[91, 1])
    monto_total_a_cobrar_val = forzar_numero(df_real.iloc[92, 1]) 
except:
    monto_vencido_lbl, monto_vencido_val = "MONTO VENCIDO", 0.0
    cobrado_lbl, cobrado_val = "COBRADO", 0.0
    monto_total_a_cobrar_val = 0.0

# =====================================================================
# JERARQUÍA 1 y 2: TOTAL COBRADO Y CAPITAL VENDIDO
# =====================================================================
col_v, col_c, col_i = st.columns(3)
with col_v:
    st.metric(label="📉 Capital Vendido (K)", value=f"$ {capital_vendido:,.2f}")
with col_c:
    st.metric(label="💰 Total Cobrado", value=f"$ {total_cobrado_dia_anterior:,.2f}")
with col_i:
    st.metric(label="🤝 Intereses Convenios", value=f"$ {intereses_convenios:,.2f}")

# =====================================================================
# JERARQUÍA 3: PORCENTAJE MOROSIDAD TOTAL + RESUMEN CARTERA DE CRÉDITOS
# =====================================================================
col_mora, col_creditos = st.columns([1, 1])
with col_mora:
    st.metric(label="📊 Porcentaje Morosidad Total", value=f"{morosidad_total:.2f}%")
with col_creditos:
    st.markdown(f"""
        <div class='card-detalle-credito-nueva'>
            <label style='color: #475569; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; margin-bottom: 2px; display: block;'>💼 MONTO TOTAL A COBRAR</label>
            <div style='color: #0f172a; font-size: 1.5rem; font-weight: 800; margin-bottom: 6px;'>$ {monto_total_a_cobrar_val:,.2f}</div>
            <div style='border-top: 1px solid #e2e8f0; padding-top: 3px;'>
                <div class='linea-credito'>
                    <span class='lbl-credito'>🔹 {monto_vencido_lbl}</span>
                    <span class='val-credito'>$ {monto_vencido_val:,.2f}</span>
                </div>
                <div class='linea-credito'>
                    <span class='lbl-credito'>🔹 {cobrado_lbl}</span>
                    <span class='val-credito'>$ {cobrado_val:,.2f}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# =====================================================================
# JERARQUÍA 4: COMPOSICIÓN Y DISPONIBILIDAD DE CAJA
# =====================================================================
st.subheader("🏦 Composición y Disponibilidad de Caja")

col_caja1, col_caja2, col_caja3, col_caja4 = st.columns(4)
with col_caja1:
    st.markdown(f"<div class='card-caja' style='border-left-color: #10b981;'><span style='color:#475569; font-size:0.75rem; font-weight:700;'>💵 EFECTIVO</span><br><span style='font-size:1.2rem; font-weight:800; color:#059669;'>$ {efectivo:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja2:
    st.markdown(f"<div class='card-caja' style='border-left-color: #3b82f6;'><span style='color:#475569; font-size:0.75rem; font-weight:700;'>🏛️ BANCOS (MACRO + FCI)</span><br><span style='font-size:1.2rem; font-weight:800; color:#2563eb;'>$ {macro_fci:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja3:
    st.markdown(f"<div class='card-caja' style='border-left-color: #8b5cf6;'><span style='color:#475569; font-size:0.75rem; font-weight:700;'>💳 DÉBITO + CNEL. SUAREZ</span><br><span style='font-size:1.2rem; font-weight:800; color:#7c3aed;'>$ {debito_suarez:,.2f}</span></div>", unsafe_allow_html=True)
with col_caja4:
    st.markdown(f"<div class='card-caja' style='border-left-color: #475569;'><span style='color:#475569; font-size:0.75rem; font-weight:700;'>📈 TOTAL GENERAL EN CAJA</span><br><span style='font-size:1.2rem; font-weight:800; color:#1e293b;'>$ {total_caja:,.2f}</span></div>", unsafe_allow_html=True)

# =====================================================================
# JERARQUÍA 5: PRÓXIMAS COMPENSACIONES
# =====================================================================
st.subheader("📅 Próximas Compensaciones")

try:
    comp_datos = [
        {"fecha": str(df_real.iloc[118, 0]).strip(), "monto": forzar_numero(df_real.iloc[118, 1])},
        {"fecha": str(df_real.iloc[119, 0]).strip(), "monto": forzar_numero(df_real.iloc[119, 1])},
        {"fecha": str(df_real.iloc[120, 0]).strip(), "monto": forzar_numero(df_real.iloc[120, 1])},
        {"fecha": str(df_real.iloc[121, 0]).strip(), "monto": forzar_numero(df_real.iloc[121, 1])},
    ]
    col_comp1, col_comp2, col_comp3, col_comp4 = st.columns(4)
    columnas_lista = [col_comp1, col_comp2, col_comp3, col_comp4]
    for i, item in enumerate(comp_datos):
        with columnas_lista[i]:
            if item["fecha"] and item["monto"] > 0:
                st.markdown(f"<div class='card-compensacion'> <span style='color:#475569; font-size:0.75rem; font-weight:700; text-transform:uppercase;'>⏳ {item['fecha']}</span><br><span style='font-size:1.1rem; font-weight:800; color:#1d4ed8;'>$ {item['monto']:,.2f}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='card-compensacion' style='border-top-color: #cbd5e1; padding: 6px;'><span style='color:#64748b; font-size:0.75rem;'>Sin compensaciones</span></div>", unsafe_allow_html=True)
except:
    st.warning("⚠️ Nota: Inconveniente al cargar compensaciones.")

# =====================================================================
# JERARQUÍA 6: PANEL DE CONTROL DE MORA HISTÓRICA (CORRECCIÓN DECIMALES)
# =====================================================================
st.subheader("🚨 Panel de Control de Mora Histórica")

dic_meses = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5, "JUNIO": 6,
    "JULIO": 7, "AGOSTO": 8, "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
}

registros_mora = []

try:
    for idx in range(10, len(df_real)):
        if idx > 250: 
            break 
            
        celda_a = str(df_real.iloc[idx, 0]).strip().upper()
        celda_b = df_real.iloc[idx, 1]
        
        if any(mes in celda_a for mes in dic_meses.keys()):
            periodo = celda_a  
            
            anio_detectado = "2025"
            for anio_posible in ["2020", "2021", "2022", "2023", "2024", "2025", "2026", "2027"]:
                if anio_posible in celda_a:
                    anio_detectado = f"{anio_posible}"
                    break
            
            mes_num = 1
            for mes_nombre, mes_id in dic_meses.items():
                if mes_nombre in celda_a:
                    mes_num = mes_id
                    break
            
            # Extraemos el valor numérico directo
            num_mora = forzar_numero(celda_b)
            
            # CORRECCIÓN DEFINITIVA: Se eliminó la multiplicación automática por 100 
            # para evitar transformar 0.70% en 70.0% de forma incorrecta.
            
            registros_mora.append({
                "Período Comercial": periodo, 
                "% En Mora": num_mora,
                "Año": anio_detectado,
                "Orden_Fecha": int(anio_detectado) * 100 + mes_num
            })
except Exception as e:
    st.error(f"Error al procesar el rango de mora histórica: {e}")

if registros_mora:
    df_mora = pd.DataFrame(registros_mora).drop_duplicates(subset=["Período Comercial"])
    df_mora = df_mora.sort_values(by="Orden_Fecha").reset_index(drop=True)

    lista_anios = ["Todos los años"] + sorted(list(df_mora["Año"].unique()), reverse=True)

    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        filtro_anio = st.selectbox("📅 Filtrar por Año Comercial:", lista_anios)
    with col_filtro2:
        filtro_mora = st.selectbox("🔍 Filtrar por Nivel de Criticidad:", 
                                   ["Todos los meses", "Mora Crítica (Mayor a 12%)", "Mora Alerta (10% a 12%)", "Mora Controlada (Menor a 10%)"])

    if filtro_anio != "Todos los años":
        df_filtrado = df_mora[df_mora["Año"] == filtro_anio]
    else:
        df_filtrado = df_mora

    if filtro_mora == "Mora Crítica (Mayor a 12%)": 
        df_filtrado = df_filtrado[df_filtrado["% En Mora"] > 12.0]
    elif filtro_mora == "Mora Alerta (10% a 12%)": 
        df_filtrado = df_filtrado[(df_filtrado["% En Mora"] >= 10.0) & (df_filtrado["% En Mora"] <= 12.0)]
    elif filtro_mora == "Mora Controlada (Menor a 10%)": 
        df_filtrado = df_filtrado[df_filtrado["% En Mora"] < 10.0]

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
        if not df_filtrado.empty:
            st.line_chart(df_filtrado.set_index("Período Comercial")["% En Mora"])
        else:
            st.info("No hay registros coincidentes para el filtro seleccionado.")
else:
    st.warning("⚠️ No se encontraron meses históricos con porcentajes de mora válidos en las columnas A y B.")

# =====================================================================
# 7. REVISIÓN DE ESTRUCTURA REAL (DIAGNÓSTICO)
# =====================================================================
with st.expander("🔍 PASO DE CONTROL: Ver cómo Streamlit está leyendo tu Planilla"):
    st.dataframe(df_real)
