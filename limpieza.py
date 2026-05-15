import pandas as pd
from sqlalchemy import create_engine
import urllib

# 1. Configuración de tu servidor local
nombre_servidor = r'localhost'
base_de_datos = 'e_commerce_data'

print("--- Iniciando proceso de carga ---")

try:
    # 2. Cargar el archivo de datos
    # Como 'data.csv' está en la misma carpeta que este script, no necesitas ruta larga
    df = pd.read_csv('data.csv', encoding='ISO-8859-1')
    print(f"Éxito: Se leyeron {len(df)} filas del archivo CSV.")

    # 3. Preparar la conexión a SQL Server
    params = urllib.parse.quote_plus(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={nombre_servidor};'
        f'DATABASE={base_de_datos};'
        f'Trusted_Connection=yes;'
    )
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

    # 4. Enviar los datos a la tabla
    print("Subiendo datos a SQL Server... ten paciencia, es mucha información.")
    df.to_sql('ecommerce_raw', con=engine, if_exists='replace', index=False)
    
    print("\n¡TERMINADO CON ÉXITO!")
    print(f"Los datos ya están en la tabla 'ecommerce_raw' de tu SQL Server.")

except Exception as e:
    print(f"\n--- ERROR ---")
    print(f"Detalle del problema: {e}")
    
    
    
import pandas as pd
from sqlalchemy import create_engine
import urllib

# 1. Configuración de la conexión (la misma que ya te funcionó)
nombre_servidor = r'DESKTOP-9S3P1BF\LENOVO'
base_de_datos = 'e_commerce_data'

params = urllib.parse.quote_plus(
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={nombre_servidor};'
    f'DATABASE={base_de_datos};'
    f'Trusted_Connection=yes;'
    f'TrustServerCertificate=yes;'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# 2. Extraer los datos de SQL para procesarlos en Python
print("Extrayendo datos de SQL Server...")
df = pd.read_sql("SELECT * FROM ecommerce_raw", con=engine)

# 3. Lógica de Limpieza
print("Iniciando limpieza profunda...")
# Eliminar filas sin ID de cliente
df_clean = df.dropna(subset=['CustomerID'])
# Mantener solo transacciones positivas
df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]
# Calcular ingresos totales
df_clean['Total_Revenue'] = df_clean['Quantity'] * df_clean['UnitPrice']

# 4. Cargar la data LIMPIA en una nueva tabla
print(f"Cargando {len(df_clean)} filas limpias a una nueva tabla...")
df_clean.to_sql('ecommerce_limpia', con=engine, if_exists='replace', index=False)

print("--- ¡PROCESO DE LIMPIEZA TERMINADO CON ÉXITO! ---")