import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Adaptador CSV para Odoo", layout="centered")
st.title("📄 Adaptador de Extracto Bancario para Odoo")

archivo = st.file_uploader("Sube tu archivo CSV (formato bancario)", type=["csv"])

if archivo:
    try:
        try:
            df = pd.read_csv(archivo, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(archivo, sep=';', encoding='ISO-8859-1')


        # Limpiar y convertir el importe
        df['Importe'] = (
            df['Importe']
            .str.replace(' eur.', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

        # Crear columna Descripción a partir de Operación + Establecimiento
        df['Descripción'] = df['Operación'].fillna('') + ' - ' + df['Establecimiento'].fillna('')

        # Convertir y formatear la fecha
        df['Fecha'] = pd.to_datetime(df['Fecha y hora'], format='%d/%m/%Y %H:%M').dt.strftime('%d/%m/%Y')

        # Seleccionar columnas finales
        df_final = df[['Fecha', 'Descripción', 'Importe']]

        st.subheader("✅ Vista previa del archivo para Odoo:")
        st.dataframe(df_final)

        # Convertir a CSV para descarga
        csv_buffer = StringIO()
        df_final.to_csv(csv_buffer, index=False, sep=';', decimal=',', encoding='utf-8')
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="📥 Descargar archivo compatible con Odoo",
            data=csv_data,
            file_name='extracto_odoo.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
