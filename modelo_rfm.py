import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib
import datetime as dt

# 1. Configuración de conexión (Ya probada y exitosa)
nombre_servidor = 'localhost'
base_de_datos = 'e_commerce_data'

params = urllib.parse.quote_plus(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={nombre_servidor};'
    f'DATABASE={base_de_datos};'
    f'Trusted_Connection=yes;'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

try:
    print("Extrayendo datos de SQL...")
    df = pd.read_sql("SELECT CustomerID, InvoiceDate, InvoiceNo, Total_Venta FROM ecommerce_procesada", con=engine)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    # Fecha de referencia: un día después del último registro
    snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)

    # 2. CÁLCULO DE MÉTRICAS RFM
    print("Calculando Recencia, Frecuencia y Monetario...")
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'Total_Venta': 'sum'
    })

    # Renombramos para no tener errores
    rfm.rename(columns={
        'InvoiceDate': 'Recencia',
        'InvoiceNo': 'Frecuencia',
        'Total_Venta': 'Monetario'
    }, inplace=True)

    # 3. ASIGNACIÓN DE PUNTAJES (Sclicing por quintiles)
    print("Generando puntuaciones del 1 al 5...")
    # Recencia: Menor es mejor (5), por eso invertimos los labels
    rfm['R'] = pd.qcut(rfm['Recencia'], 5, labels=[5, 4, 3, 2, 1])
    
    # Frecuencia y Monetario: Mayor es mejor (5)
    # Usamos rank(method='first') para evitar errores si hay muchos valores iguales
    rfm['F'] = pd.qcut(rfm['Frecuencia'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M'] = pd.qcut(rfm['Monetario'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

    # 4. SEGMENTACIÓN FINAL
    # Combinamos R y F para obtener el mapa que me mostraste
    rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str)

    seg_map = {
        r'[1-2][1-2]': 'Hibernando/Perdidos',
        r'[1-2][3-4]': 'En Riesgo',
        r'[1-2]5': 'No podemos perderlos',
        r'3[1-2]': 'Cerca de dormir',
        r'33': 'Necesitan atención',
        r'[3-4][4-5]': 'Leales',
        r'41': 'Prometedores',
        r'51': 'Nuevos clientes',
        r'[4-5][2-3]': 'Potenciales Leales',
        r'5[4-5]': 'Campeones'
    }

    rfm['Segmento'] = rfm['RFM_Score'].replace(seg_map, regex=True)

    # 5. GUARDAR EN SQL PARA POWER BI
    print("Guardando tabla definitiva 'ecommerce_rfm' en SQL Server...")
    rfm.reset_index().to_sql('ecommerce_rfm', con=engine, if_exists='replace', index=False)

    print("\n" + "="*40)
    print("¡MODELO RFM COMPLETADO CON ÉXITO!")
    print(f"Clientes procesados: {len(rfm)}")
    print("="*40)
    print(rfm['Segmento'].value_counts())

except Exception as e:
    print(f"\nError detectado: {e}")