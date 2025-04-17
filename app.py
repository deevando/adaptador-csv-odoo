import streamlit as st
import pandas as pd
from io import StringIO
import csv

st.set_page_config(page_title="Adaptador CSV para Odoo", layout="centered")
st.title("📄 Adaptador de Extracto Bancario para Odoo")

archivo = st.file_uploader("Sube tu archivo CSV (formato bancario)", type=["csv"])

if archivo:
    try:
        # Intentar detectar el delimitador
        archivo.seek(0)
        sample = archivo.read(2048).decode('utf-8', errors='ignore')
        delimiter = csv.Sniffer().sniff(sample).delimiter
        archivo.seek(0)

        # Leer CSV con codificación utf-8 o fallback ISO-8859-1
        try:
            df = pd.read_csv(archivo, sep=delimiter, encoding='utf-8', engine='python')
        except UnicodeDecodeError:
            archivo.seek(0)
            df = pd.read_csv(archivo, sep=delimiter, encoding='ISO-8859-1', engine='python')

        # Procesar el CSV
        df['Importe'] = (
            df['Importe']
            .str.replace(' eur.', '', regex=False)
            .str.replace('.', '', regex=False)
            .str.replace(',', '.', regex=False)
            .astype(float)
        )

        df['Etiqueta'] = df['Operación'].fillna('') + ' - ' + df['Establecimiento'].fillna('')
        df['Fecha'] = pd.to_datetime(df['Fecha y hora'], format='%d/%m/%Y %H:%M').dt.strftime('%d/%m/%Y')

        df_final = df[['Fecha', 'Descripción', 'Importe']]

        st.subheader("✅ Vista previa del archivo para Odoo:")
        st.dataframe(df_final)

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
