import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Don Chicharron - Dashboard de Compras",
    page_icon="🐷",
    layout="wide"
)

# 2. Load Data (with caching for performance optimization)
@st.cache_data
def load_data():
    df = pd.read_csv("ordenes_de_compra_don_chicharron.csv")
    # Convert dates to datetime objects for accurate filtering
    df["Fecha_Emision"] = pd.to_datetime(df["Fecha_Emision"])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("❌ El archivo 'ordenes_de_compra_don_chicharron.csv' no fue encontrado. Asegúrate de que está en la misma carpeta.")
    st.stop()

# 3. Header / Branding
st.title("🐷 Don Chicharron - Dashboard de Órdenes de Compra")
st.markdown("Herramienta de análisis analítico para el control de insumos, proveedores y costos.")
st.write("---")

# 4. Sidebar Filters (Interactivity Layer)
st.sidebar.header("Filtros Globales")

# Filter by Supplier
all_suppliers = ["Todos"] + list(df["Proveedor"].unique())
selected_supplier = st.sidebar.selectbox("Selecciona un Proveedor", all_suppliers)

# Filter by Order Status
all_statuses = ["Todos"] + list(df["Estado"].unique())
selected_status = st.sidebar.selectbox("Selecciona el Estado de la Orden", all_statuses)

# Apply Interactive Filtering
df_filtered = df.copy()
if selected_supplier != "Todos":
    df_filtered = df_filtered[df_filtered["Proveedor"] == selected_supplier]
if selected_status != "Todos":
    df_filtered = df_filtered[df_filtered["Estado"] == selected_status]

# 5. Key Performance Indicators (KPIs Metrics Layer)
st.subheader("📊 Indicadores Clave de Rendimiento (KPIs)")
col1, col2, col3, col4 = st.columns(4)

total_spend = df_filtered["Total_COP"].sum()
total_orders = df_filtered["ID_Orden"].nunique()
avg_order_value = df_filtered["Total_COP"].mean() if total_orders > 0 else 0
pending_orders = df_filtered[df_filtered["Estado"].isin(["Pendiente", "En Tránsito"])]["ID_Orden"].nunique()

with col1:
    st.metric(label="Gasto Total (COP)", value=f"${total_spend:,.0f}")
with col2:
    st.metric(label="Total Órdenes", value=total_orders)
with col3:
    st.metric(label="Ticket Promedio (COP)", value=f"${avg_order_value:,.0f}")
with col4:
    st.metric(label="Órdenes Abiertas", value=pending_orders)

st.write("---")

# 6. Data Visualization Layer (Charts)
st.subheader("📈 Análisis de Distribución y Gastos")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Gasto Total por Proveedor**")
    # Aggregate data for the bar chart
    spend_by_supplier = df_filtered.groupby("Proveedor")["Total_COP"].sum().reset_index()
    fig_bar = px.bar(
        spend_by_supplier, 
        x="Proveedor", 
        y="Total_COP", 
        labels={"Total_COP": "Total Gasto ($)"},
        template="plotly_white",
        color="Proveedor"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with chart_col2:
    st.markdown("**Proporción de Gastos por Centro de Costos**")
    fig_pie = px.pie(
        df_filtered, 
        values="Total_COP", 
        names="Centro_Costos", 
        hole=0.4,
        template="plotly_white"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.write("---")

# 7. Granular Data Layer (The Table)
st.subheader("🔍 Detalle de Transacciones")
st.markdown("Tabla filtrada con base en los criterios seleccionados en la barra lateral:")

# Display cleanly formatted DataFrame
st.dataframe(
    df_filtered.style.format({
        "Precio_Unitario_COP": "${:,.0f}",
        "Subtotal_COP": "${:,.0f}",
        "IVA_19_COP": "${:,.0f}",
        "Total_COP": "${:,.0f}"
    }), 
    use_container_width=True
)
