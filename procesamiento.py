import pandas as pd
from sqlalchemy import create_engine
import urllib

# 1. Configuración para la instancia MSSQLSERVER (la que tienes activa)
# Al ser la instancia principal, usamos 'localhost' sin barras adicionales
nombre_servidor = 'localhost' 
base_de_datos = 'e_commerce_data'

# Cadena de conexión profesional
params = urllib.parse.quote_plus(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={nombre_servidor};'
    f'DATABASE={base_de_datos};'
    f'Trusted_Connection=yes;'
    f'TrustServerCertificate=yes;'
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

try:
    print(f"Conectando a la instancia activa: {nombre_servidor}...")
    
    # Intentamos leer la tabla original
    # Nota: Asegúrate de haber importado el CSV a esta instancia específicamente
    df = pd.read_sql("SELECT * FROM ecommerce_raw", con=engine)
    print(f"Éxito: Se han extraído {len(df)} filas.")

    # --- PROCESAMIENTO DE DATOS ---
    print("Limpiando datos...")
    
    # Eliminamos filas sin ID de cliente y valores incoherentes
    df_clean = df.dropna(subset=['CustomerID']).copy()
    df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]
    
    # Calculamos la métrica de ventas
    df_clean['Total_Venta'] = df_clean['Quantity'] * df_clean['UnitPrice']
    
    print(f"Limpieza terminada. Registros finales: {len(df_clean)}")

    # --- CARGA DE DATOS PARA POWER BI ---
    print("Creando tabla 'ecommerce_procesada' en SQL...")
    df_clean.to_sql('ecommerce_procesada', con=engine, if_exists='replace', index=False)

    print("\n" + "="*40)
    print("¡PROCESO COMPLETADO CON ÉXITO!")
    print(f"Venta Total: ${df_clean['Total_Venta'].sum():,.2f}")
    print("="*40)

except Exception as e:
    print(f"\nERROR TÉCNICO: {e}")
    print("\nSi el error es 'Invalid object name', recuerda importar el CSV")
    print(f"dentro de la base de datos '{base_de_datos}' en MSSQLSERVER.")