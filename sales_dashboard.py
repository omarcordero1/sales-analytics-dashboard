# sales_dashboard.py - CÓDIGO COMPLETO
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# =============================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =============================================
st.set_page_config(
    page_title="Sales Analytics - Omar Cordero", 
    layout="wide",
    page_icon="🚀"
)

# =============================================
# CSS PERSONALIZADO
# =============================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# =============================================
# HEADER PRINCIPAL
# =============================================
st.markdown("""
<div class="main-header">
    <h1>🚀 Sales Analytics Dashboard</h1>
    <h3>Omar Cordero - Data-Driven Sales Intelligence</h3>
    <p>Tecnología que impulsa decisiones comerciales inteligentes</p>
</div>
""", unsafe_allow_html=True)

# =============================================
# FUNCIONES AUXILIARES
# =============================================
def estandarizar_columnas(df):
    """Estandariza nombres de columnas automáticamente"""
    mapeo = {
        'fecha': ['fecha', 'date', 'fecha_venta', 'timestamp', 'Fecha'],
        'cliente': ['cliente', 'client', 'customer', 'empresa', 'Cliente', 'Customer'],
        'producto_servicio': ['producto_servicio', 'producto', 'servicio', 'service', 'product', 'Producto', 'Servicio'],
        'monto_venta': ['monto_venta', 'venta', 'monto', 'sales', 'amount', 'valor', 'Venta', 'Monto'],
        'vendedor': ['vendedor', 'seller', 'sales_rep', 'ejecutivo', 'Vendedor', 'Seller'],
        'industria': ['industria', 'sector', 'industry', 'rubro', 'Industria', 'Sector'],
        'estado_venta': ['estado_venta', 'estado', 'status', 'stage', 'Estado', 'Status'],
        'region': ['region', 'zona', 'territory', 'area', 'Region', 'Zona'],
        'costo': ['costo', 'cost', 'costo_venta', 'Costo', 'Cost'],
        'comision': ['comision', 'commission', 'comisión', 'Comision', 'Commission']
    }
    
    for estandar, alternativas in mapeo.items():
        for alt in alternativas:
            if alt in df.columns and estandar not in df.columns:
                df[estandar] = df[alt]
                st.sidebar.info(f"📝 Columna '{alt}' mapeada a '{estandar}'")
                break
                
    return df

def limpiar_datos(df):
    """Limpieza y transformación de datos"""
    
    # Asegurar que monto_venta es numérico
    if 'monto_venta' in df.columns:
        df['monto_venta'] = pd.to_numeric(df['monto_venta'], errors='coerce')
    
    # Convertir fecha si existe
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
    
    # Filtrar valores nulos en columnas críticas
    columnas_criticas = [col for col in ['fecha', 'cliente', 'monto_venta'] if col in df.columns]
    if columnas_criticas:
        df = df.dropna(subset=columnas_criticas)
    
    # Calcular utilidad si tenemos costo
    if 'costo' in df.columns and 'monto_venta' in df.columns:
        df['costo'] = pd.to_numeric(df['costo'], errors='coerce')
        df['utilidad'] = df['monto_venta'] - df['costo']
        df['margen'] = (df['utilidad'] / df['monto_venta']) * 100
    
    return df

def generar_datos_ejemplo():
    """Genera datos de ejemplo con la estructura requerida"""
    np.random.seed(42)
    
    # Fechas de los últimos 6 meses
    fechas = pd.date_range('2023-07-01', periods=180, freq='D')
    
    # Datos de ejemplo realistas B2B
    datos = {
        'fecha': np.random.choice(fechas, 120),
        'cliente': np.random.choice([
            'TechSolutions SA', 'CloudCorp MX', 'DataDriven Inc', 'InnovateLabs',
            'DigitalFlow', 'SmartSystems', 'NextGen Tech', 'FutureWorks',
            'MetaSystems', 'AI Ventures', 'BlockChain MX', 'CyberSecure'
        ], 120),
        'producto_servicio': np.random.choice([
            'SaaS Enterprise', 'Consultoría Estratégica', 'Implementación Cloud',
            'Soporte Premium', 'Capacitación Avanzada', 'Desarrollo Personalizado',
            'Auditoría Security', 'Migración Digital'
        ], 120, p=[0.2, 0.18, 0.15, 0.15, 0.12, 0.1, 0.05, 0.05]),
        'monto_venta': np.random.lognormal(10, 0.7, 120).round(2),  # Ventas entre 15k-60k
        'vendedor': np.random.choice(['Omar Cordero', 'Equipo Norte', 'Equipo Sur', 'Ana López', 'Carlos Ruiz'], 120, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
        'industria': np.random.choice(['Tecnología', 'Finanzas', 'Manufactura', 'Salud', 'Retail', 'Educación'], 120),
        'estado_venta': np.random.choice(['Completado', 'En proceso', 'Cotización', 'Negociación'], 120, p=[0.6, 0.2, 0.1, 0.1]),
        'region': np.random.choice(['Norte', 'Centro', 'Sur', 'Internacional'], 120, p=[0.3, 0.4, 0.2, 0.1]),
        'costo': np.random.lognormal(9, 0.6, 120).round(2),  # Costos ~60% de venta
    }
    
    df = pd.DataFrame(datos)
    df['comision'] = (df['monto_venta'] * np.random.uniform(0.08, 0.12, 120)).round(2)
    df['utilidad'] = df['monto_venta'] - df['costo']
    df['margen'] = (df['utilidad'] / df['monto_venta'] * 100).round(2)
    
    return df

# =============================================
# FUNCIÓN PRINCIPAL DE CARGA DE DATOS
# =============================================
def cargar_datos_flexible():
    st.sidebar.header("📁 Fuente de Datos")
    
    fuente = st.sidebar.radio(
        "Selecciona fuente:",
        ["📤 Subir CSV", "🔗 Google Sheets", "🎯 Datos de Ejemplo"]
    )
    
    df = None
    
    if fuente == "📤 Subir CSV":
        st.sidebar.subheader("Subir Archivo CSV")
        archivo = st.sidebar.file_uploader(
            "Selecciona tu archivo CSV", 
            type=['csv'],
            help="Asegúrate que tenga las columnas: fecha, cliente, producto_servicio, monto_venta"
        )
        
        if archivo:
            try:
                df = pd.read_csv(archivo)
                df = estandarizar_columnas(df)
                df = limpiar_datos(df)
                
                st.sidebar.success(f"✅ {archivo.name} cargado exitosamente!")
                st.sidebar.info(f"📊 {len(df)} registros - {len(df.columns)} columnas")
                
                # Mostrar preview en sidebar
                with st.sidebar.expander("🔍 Vista previa de datos"):
                    st.dataframe(df.head(3))
                
            except Exception as e:
                st.sidebar.error(f"❌ Error cargando archivo: {str(e)}")
    
    elif fuente == "🔗 Google Sheets":
        st.sidebar.subheader("Conectar Google Sheets")
        st.sidebar.info("🚧 Esta función estará disponible en la siguiente versión")
        
        sheet_url = st.sidebar.text_input(
            "URL de Google Sheets (próximamente):",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            disabled=True
        )
        
        # Para la próxima versión
        if sheet_url and sheet_url.startswith('https://docs.google.com/spreadsheets/d/'):
            try:
                csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
                df = pd.read_csv(csv_url)
                df = estandarizar_columnas(df)
                df = limpiar_datos(df)
                st.sidebar.success("✅ Google Sheets conectado")
            except:
                st.sidebar.error("❌ Error conectando con Google Sheets")
    
    else:  # Datos de ejemplo
        df = generar_datos_ejemplo()
        st.sidebar.success("📊 Datos de ejemplo generados")
        st.sidebar.info("Usa esta opción para explorar las funcionalidades")
    
    return df

def validar_estructura(df):
    """Valida que el DataFrame tenga la estructura mínima requerida"""
    columnas_requeridas = ['fecha', 'cliente', 'producto_servicio', 'monto_venta']
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        st.error(f"❌ Columnas requeridas faltantes: {columnas_faltantes}")
        st.info("""
        **Estructura mínima requerida en tu CSV:**
        - **fecha**: Fecha de la venta (YYYY-MM-DD)
        - **cliente**: Nombre del cliente/empresa
        - **producto_servicio**: Producto o servicio vendido
        - **monto_venta**: Valor numérico de la venta
        
        **Columnas opcionales (recomendadas):**
        - vendedor, industria, estado_venta, region, costo, comision
        """)
        return False
    
    return True

# =============================================
# FUNCIONES DE ANÁLISIS Y VISUALIZACIÓN
# =============================================
def mostrar_metricas_principales(df):
    """Muestra las métricas principales del dashboard"""
    st.header("📊 Dashboard de Performance")
    
    # Calcular métricas básicas
    total_ventas = df['monto_venta'].sum()
    total_clientes = df['cliente'].nunique()
    venta_promedio = df['monto_venta'].mean()
    total_transacciones = len(df)
    
    # Calcular métricas avanzadas si están disponibles
    utilidad_total = df['utilidad'].sum() if 'utilidad' in df.columns else total_ventas * 0.4
    margen_promedio = df['margen'].mean() if 'margen' in df.columns else 40.0
    
    # Mostrar métricas en columnas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Ventas", f"${total_ventas:,.0f}", "Revenue Total")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Clientes Únicos", f"{total_clientes}", "Base de Clientes")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Venta Promedio", f"${venta_promedio:,.0f}", "Ticket Medio")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Transacciones", f"{total_transacciones}", "Volumen de Ventas")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Segunda fila de métricas
    if 'utilidad' in df.columns:
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Utilidad Total", f"${utilidad_total:,.0f}", "Profit")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col6:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Margen Promedio", f"{margen_promedio:.1f}%", "Rentabilidad")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col7:
            if 'comision' in df.columns:
                comision_total = df['comision'].sum()
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Comisiones", f"${comision_total:,.0f}", "Incentivos")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col8:
            if 'vendedor' in df.columns:
                top_vendedor = df.groupby('vendedor')['monto_venta'].sum().idxmax()
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Top Vendedor", top_vendedor[:15], "Líder")
                st.markdown('</div>', unsafe_allow_html=True)

def mostrar_analisis_visual(df):
    """Muestra los análisis visuales interactivos"""
    st.header("📈 Análisis Visual Interactivo")
    
    # Tabs para diferentes análisis
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Ventas por Producto", 
        "📅 Trend Temporal", 
        "👥 Performance por Vendedor",
        "🌍 Análisis Geográfico", 
        "📋 Vista de Datos"
    ])
    
    with tab1:
        st.subheader("Análisis por Producto/Servicio")
        
        # Ventas por producto/servicio
        ventas_producto = df.groupby('producto_servicio')['monto_venta'].sum().sort_values(ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_barras = px.bar(
                ventas_producto,
                title='Ventas Totales por Producto/Servicio',
                labels={'value': 'Ventas Totales (USD)', 'producto_servicio': 'Producto/Servicio'},
                color=ventas_producto.values,
                color_continuous_scale='Viridis'
            )
            fig_barras.update_layout(showlegend=False)
            st.plotly_chart(fig_barras, use_container_width=True)
        
        with col2:
            fig_torta = px.pie(
                values=ventas_producto.values,
                names=ventas_producto.index,
                title='Distribución % por Producto'
            )
            st.plotly_chart(fig_torta, use_container_width=True)
        
        # Top productos por utilidad si está disponible
        if 'utilidad' in df.columns:
            st.subheader("Productos más Rentables")
            utilidad_producto = df.groupby('producto_servicio')['utilidad'].sum().nlargest(10)
            fig_utilidad = px.bar(
                utilidad_producto,
                title='Top 10 Productos por Utilidad',
                labels={'value': 'Utilidad Total (USD)', 'producto_servicio': 'Producto/Servicio'},
                color=utilidad_producto.values,
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_utilidad, use_container_width=True)
    
    with tab2:
        st.subheader("Análisis Temporal")
        
        if 'fecha' in df.columns:
            # Selector de frecuencia
            freq = st.selectbox("Frecuencia de análisis:", ['Mensual', 'Semanal', 'Trimestral'])
            freq_map = {'Mensual': 'M', 'Semanal': 'W', 'Trimestral': 'Q'}
            
            # Ventas por período
            ventas_periodo = df.groupby(pd.Grouper(key='fecha', freq=freq_map[freq]))['monto_venta'].sum()
            
            fig_trend = px.line(
                ventas_periodo,
                title=f'Trend de Ventas {freq}',
                labels={'value': f'Ventas {freq} (USD)', 'fecha': 'Período'},
                markers=True
            )
            fig_trend.update_traces(line=dict(width=3), marker=dict(size=8))
            fig_trend.update_layout(hovermode='x unified')
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Growth rate
            if len(ventas_periodo) > 1:
                crecimiento = ((ventas_periodo.iloc[-1] - ventas_periodo.iloc[-2]) / ventas_periodo.iloc[-2] * 100)
                st.metric(f"Crecimiento {freq}", f"{crecimiento:.1f}%")
    
    with tab3:
        st.subheader("Performance por Vendedor")
        
        if 'vendedor' in df.columns:
            # Métricas por vendedor
            perf_vendedor = df.groupby('vendedor').agg({
                'monto_venta': ['sum', 'count', 'mean'],
                'cliente': 'nunique'
            }).round(0)
            
            perf_vendedor.columns = ['Total Ventas', 'N° Transacciones', 'Ticket Promedio', 'Clientes Únicos']
            perf_vendedor = perf_vendedor.sort_values('Total Ventas', ascending=False)
            
            # Formatear para display
            display_df = perf_vendedor.style.format({
                'Total Ventas': '${:,.0f}',
                'Ticket Promedio': '${:,.0f}'
            })
            
            st.dataframe(display_df, use_container_width=True)
            
            # Gráfico de comparación
            fig_vendedores = px.bar(
                perf_vendedor.reset_index(),
                x='vendedor',
                y='Total Ventas',
                title='Comparativa de Ventas por Vendedor',
                color='Total Ventas',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_vendedores, use_container_width=True)
        else:
            st.info("ℹ️ No hay datos de vendedor para mostrar este análisis")
    
    with tab4:
        st.subheader("Análisis Geográfico")
        
        if 'region' in df.columns:
            # Ventas por región
            ventas_region = df.groupby('region')['monto_venta'].sum().sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_region_barras = px.bar(
                    ventas_region,
                    title='Ventas por Región',
                    labels={'value': 'Ventas Totales (USD)', 'region': 'Región'},
                    color=ventas_region.values,
                    color_continuous_scale='Reds'
                )
                st.plotly_chart(fig_region_barras, use_container_width=True)
            
            with col2:
                fig_region_torta = px.pie(
                    values=ventas_region.values,
                    names=ventas_region.index,
                    title='Distribución por Región'
                )
                st.plotly_chart(fig_region_torta, use_container_width=True)
            
            # Mapa de calor región vs producto
            if 'producto_servicio' in df.columns:
                pivot_data = df.pivot_table(
                    values='monto_venta', 
                    index='region', 
                    columns='producto_servicio', 
                    aggfunc='sum'
                ).fillna(0)
                
                fig_heatmap = px.imshow(
                    pivot_data,
                    title='Ventas: Región vs Producto',
                    aspect="auto",
                    color_continuous_scale='Blues'
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("ℹ️ No hay datos de región para mostrar este análisis")
    
    with tab5:
        st.subheader("Datos Originales y Estadísticas")
        
        # Filtros interactivos
        col1, col2 = st.columns(2)
        
        with col1:
            if 'producto_servicio' in df.columns:
                productos_seleccionados = st.multiselect(
                    "Filtrar por producto:",
                    options=df['producto_servicio'].unique(),
                    default=df['producto_servicio'].unique()[:3]
                )
                if productos_seleccionados:
                    df_filtrado = df[df['producto_servicio'].isin(productos_seleccionados)]
                else:
                    df_filtrado = df
            else:
                df_filtrado = df
        
        with col2:
            if 'vendedor' in df.columns:
                vendedores_seleccionados = st.multiselect(
                    "Filtrar por vendedor:",
                    options=df['vendedor'].unique(),
                    default=df['vendedor'].unique()[:2]
                )
                if vendedores_seleccionados:
                    df_filtrado = df_filtrado[df_filtrado['vendedor'].isin(vendedores_seleccionados)]
        
        # Mostrar datos filtrados
        st.dataframe(df_filtrado, use_container_width=True)
        
        # Estadísticas descriptivas
        st.subheader("Estadísticas Descriptivas")
        st.dataframe(df_filtrado.describe(), use_container_width=True)

# =============================================
# APLICACIÓN PRINCIPAL
# =============================================
def main():
    # Cargar datos
    df = cargar_datos_flexible()
    
    # Procesar y mostrar datos si están disponibles
    if df is not None and not df.empty:
        if validar_estructura(df):
            # Mostrar información del dataset
            st.sidebar.markdown("---")
            st.sidebar.subheader("📋 Información del Dataset")
            st.sidebar.write(f"**Registros:** {len(df)}")
            st.sidebar.write(f"**Período:** {df['fecha'].min().strftime('%Y-%m-%d') if 'fecha' in df.columns else 'N/A'} a {df['fecha'].max().strftime('%Y-%m-%d') if 'fecha' in df.columns else 'N/A'}")
            st.sidebar.write(f"**Clientes únicos:** {df['cliente'].nunique()}")
            st.sidebar.write(f"**Productos únicos:** {df['producto_servicio'].nunique() if 'producto_servicio' in df.columns else 'N/A'}")
            
            # Mostrar análisis principal
            mostrar_metricas_principales(df)
            mostrar_analisis_visual(df)
            
            # Exportar datos
            st.sidebar.markdown("---")
            st.sidebar.subheader("📤 Exportar Datos")
            if st.sidebar.button("Descargar Datos Procesados"):
                csv = df.to_csv(index=False)
                st.sidebar.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"datos_procesados_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    else:
        # Mensaje de bienvenida cuando no hay datos
        st.info("""
        👋 **¡Bienvenido al Sales Analytics Dashboard!**
        
        **Para comenzar:**
        1. 📤 **Selecciona "Subir CSV"** en la barra lateral
        2. 📁 **Sube tu archivo CSV** con datos de ventas
        3. 📊 **Explora los análisis automáticos**
        
        **Estructura esperada de tu CSV:**
        ```csv
        fecha,cliente,producto_servicio,monto_venta
        2024-01-15,Empresa ABC,SaaS Enterprise,25000
        2024-01-18,Startup XYZ,Consultoría Cloud,18000
        ```
        
        **Columnas opcionales recomendadas:** vendedor, industria, estado_venta, region, costo, comision
        """)
        
        # Mostrar ejemplo de datos
        with st.expander("🎯 Ver ejemplo de estructura de datos"):
            df_ejemplo = generar_datos_ejemplo()
            st.dataframe(df_ejemplo.head(10), use_container_width=True)
            st.download_button(
                label="📥 Descargar CSV de Ejemplo",
                data=df_ejemplo.to_csv(index=False),
                file_name="ejemplo_estructura.csv",
                mime="text/csv"
            )

# =============================================
# EJECUCIÓN
# =============================================
if __name__ == "__main__":
    main()

# Footer final
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Sales Analytics Dashboard</strong> • Desarrollado para Omar Cordero</p>
    <p>Tecnología que impulsa decisiones comerciales inteligentes 🚀</p>
</div>
""", unsafe_allow_html=True)
