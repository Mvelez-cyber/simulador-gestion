import streamlit as st
import pandas as pd
import os

# Definir una clase para la simulación de inversión
class SimulacionInversion:
    def __init__(self, ruta_archivo_excel="utils/presupuesto_inversion_inicial.xlsx"):
        # Verificar si el archivo existe
        if not os.path.isfile(ruta_archivo_excel):
            st.error(f"Archivo no encontrado en la ruta: {ruta_archivo_excel}")
            return

        # Cargar ambas hojas en dataframes
        self.df_servicios = pd.read_excel(ruta_archivo_excel, sheet_name="Servicios y Productos")
        self.df_capital_humano = pd.read_excel(ruta_archivo_excel, sheet_name="Capital Humano y Operacion")

        # Asegurarse de que la columna 'Cantidad (USD)' sea numérica en df_capital_humano
        self.df_capital_humano["Cantidad (USD)"] = pd.to_numeric(self.df_capital_humano["Cantidad (USD)"], errors='coerce')

    def mostrar_resumen(self):
        # Mostrar un resumen de los costos totales actuales para servicios/productos y capital humano/operación
        total_servicios = self.df_servicios["Costo Total (USD)"].sum()
        total_capital_humano = self.df_capital_humano["Cantidad (USD)"].sum()
        return total_servicios, total_capital_humano

    def actualizar_costos_servicios(self, df_servicios_editado):
        # Actualizar el dataframe de servicios con los valores editados
        self.df_servicios = df_servicios_editado.copy()
        
        # Recalcular el costo total para cada fila de servicios
        self.df_servicios["Costo Total (USD)"] = self.df_servicios["Costo Unitario (USD)"] * self.df_servicios["Cantidad"]
        
        # Calcular el total general de servicios
        total_servicios = self.df_servicios["Costo Total (USD)"].sum()
        return total_servicios

# Inicializar la simulación con la ruta a su archivo de Excel
ruta_archivo = "utils/presupuesto_inversion_inicial.xlsx"  # Ruta relativa
simulacion = SimulacionInversion(ruta_archivo)

# Streamlit UI
st.title("Simulación de Inversión")

# Mostrar resumen inicial si el archivo fue cargado correctamente
if hasattr(simulacion, 'df_servicios') and hasattr(simulacion, 'df_capital_humano'):
    total_servicios, total_capital_humano = simulacion.mostrar_resumen()
    st.write(f"Costo total de servicios/productos: ${total_servicios:.2f}")
    st.write(f"Costo total de capital humano y operación: ${total_capital_humano:.2f}")

    # Ajustar Costos de Servicios/Productos
    st.header("Ajustar Costos de Servicios/Productos")
    df_servicios_editado = st.data_editor(
        simulacion.df_servicios,
        column_config={
            "Descripción": st.column_config.TextColumn(
                "Descripción",
                help="Edita la descripción del servicio/producto"
            ),
            "Cantidad": st.column_config.NumberColumn(
                "Cantidad",
                help="Edita la cantidad",
                min_value=0,
                step=1,
                format="%d"
            ),
            "Costo Unitario (USD)": st.column_config.NumberColumn(
                "Costo Unitario (USD)",
                help="Edita el costo unitario",
                min_value=0,
                format="%.4f"
            ),
            "Costo Total (USD)": st.column_config.NumberColumn(
                "Costo Total (USD)",
                help="Costo total calculado automáticamente",
                format="%.4f",
                disabled=True  # Deshabilitar edición en esta columna
            )
        }
    )

    # Botón para actualizar costos de servicios
    if st.button("Actualizar Precios de Servicios"):
        total_servicios_actualizado = simulacion.actualizar_costos_servicios(df_servicios_editado)
        st.write(f"Costo total de servicios actualizado: ${total_servicios_actualizado:.4f}")

    # Ajustar Costos de Capital Humano
    st.header("Ajustar Costos de Capital Humano")
    df_capital_humano_editado = st.data_editor(
        simulacion.df_capital_humano,
        column_config={
            "Descripción": st.column_config.TextColumn(
                "Descripción",
                help="Edita la descripción del puesto/operación"
            ),
            "Cantidad (USD)": st.column_config.NumberColumn(
                "Cantidad (USD)",
                help="Edita el costo",
                min_value=0,
                format="%.4f"
            )
        }
    )

    # Botón para actualizar costos de capital humano
    if st.button("Actualizar Precios de Capital Humano"):
        # Convertir la columna a numérico, ignorando errores y excluyendo valores no numéricos
        valores_numericos = pd.to_numeric(df_capital_humano_editado["Cantidad (USD)"], errors='coerce')
        total_capital_humano_actualizado = valores_numericos.sum()
        st.write(f"Costo total de capital humano actualizado: ${total_capital_humano_actualizado:.4f}")

    # Botón para calcular el total general
    if st.button("Calcular Total General"):
        total_servicios_final = simulacion.df_servicios["Costo Total (USD)"].sum()
        valores_numericos = pd.to_numeric(df_capital_humano_editado["Cantidad (USD)"], errors='coerce')
        total_capital_humano_final = valores_numericos.sum()
        total_general = total_servicios_final + total_capital_humano_final
        st.header(f"Total General: ${total_general:.2f}")

else:
    st.error("No se pudo cargar el archivo de Excel. Verifica la ruta y vuelve a intentar.")
