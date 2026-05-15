import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import urllib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# 1. Conexión (localhost / MSSQLSERVER)
nombre_servidor = 'localhost'
base_de_datos = 'e_commerce_data'
params = urllib.parse.quote_plus(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={nombre_servidor};DATABASE={base_de_datos};Trusted_Connection=yes;')
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

try:
    print("Extrayendo datos y mejorando características...")
    df_rfm = pd.read_sql("SELECT * FROM ecommerce_rfm", con=engine)

    # --- INGENIERÍA DE CARACTERÍSTICAS ---
    # Creamos el 'Ticket Promedio': Dinero total / Frecuencia
    df_rfm['Ticket_Promedio'] = df_rfm['Monetario'] / df_rfm['Frecuencia']
    
    # Creamos la etiqueta Churn (nuestro objetivo a predecir)
    df_rfm['Churn'] = (df_rfm['Recencia'] > 90).astype(int)

    # 2. SELECCIÓN DE VARIABLES (Sin Recencia para evitar trampa)
    # Agregamos Ticket_Promedio para darle más "pistas" al modelo
    X = df_rfm[['Frecuencia', 'Monetario', 'Ticket_Promedio']]
    y = df_rfm['Churn']

    # 3. ENTRENAMIENTO CON BALANCEO
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Usamos 'class_weight' para que el modelo preste más atención a los que se fugan
    modelo_churn = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
    modelo_churn.fit(X_train, y_train)

    # 4. RESULTADOS
    y_pred = modelo_churn.predict(X_test)
    print("\n--- REPORTE DE MODELO MEJORADO ---")
    print(classification_report(y_test, y_pred))

    # Guardar probabilidades actualizadas en SQL
    df_rfm['Probabilidad_Fuga'] = modelo_churn.predict_proba(X)[:, 1]
    df_rfm.to_sql('ecommerce_predicciones', con=engine, if_exists='replace', index=False)
    
    print("\n¡Proceso terminado! Datos actualizados en SQL Server.")

except Exception as e:
    print(f"Error: {e}")