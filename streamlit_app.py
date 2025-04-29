import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
from stop_words import get_stop_words

# Configuración de la página
st.set_page_config(
    page_title="Generador de núvols de paraules",
    layout="wide"
)

# Título de la aplicación
st.title("Anàlisi de respostes")
st.write("Aquesta aplicació permet generar núvols de paraules a partir de text filtrat per àmbit i pregunta")

# Función para limpiar texto
def limpiar_texto(texto):
    if isinstance(texto, str):
        # Convertir a minúsculas
        texto = texto.lower()
        # Eliminar caracteres especiales y números
        texto = re.sub(r'[^\w\s]', '', texto)
        texto = re.sub(r'\d+', '', texto)
        # Eliminar espacios extra
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
    else:
        return ""

# Función para generar nube de palabras
def generar_nube_palabras(texto, titulo, palabras_excluir=None):
    if not palabras_excluir:
        palabras_excluir = set()
    else:
        palabras_excluir = set(palabras_excluir)
    
    # Contar frecuencia de palabras
    palabras = texto.split()
    # Filtrar palabras a excluir
    palabras = [p for p in palabras if p not in palabras_excluir and len(p) > 2]
    
    # Verificar si hay palabras después de filtrar
    if not palabras:
        st.warning(f"No hi ha suficients paraules per a generar '{titulo}'")
        return None
    
    # Crear la nube de palabras
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        max_words=100,
        contour_width=1, 
        contour_color='steelblue'
    ).generate(' '.join(palabras))
    
    # Mostrar la nube
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_title(f"{titulo}")
    ax.axis("off")
    
    return fig

# Cargar stopwords en español y catalán
stopwords_es = set(get_stop_words("spanish"))
stopwords_ca = set(get_stop_words("catalan"))
stopwords_combined = stopwords_es.union(stopwords_ca)
stopwords_combined.add('_x000D_')

try:
    df = pd.read_excel('Avaluació Qualitativa.xlsx')
    
    # --- INTERFAZ ---
    # Mostrar los primeros registros
    with st.expander("Veure dades d'exemple"):
        st.dataframe(df)

    # Añadir información de depuración
    # with st.expander("Informació del conjunt de dades"):
    #     st.write("Columnes disponibles en el DataFrame:")
    #     st.write(list(df.columns))
    #     st.write(f"Total de registres: {len(df)}")
    #     st.write("Valors únics en 'Descripcio_Ambit':")
    #     st.write(sorted(df['Descripcio_Ambit'].unique().tolist()))

    # Sidebar para filtros
    st.sidebar.header("Filtres")

    # Selección de categoría
    categorias = ["Tots"] + sorted(df['Descripcio_Ambit'].unique().tolist())
    categoria_seleccionada = st.sidebar.selectbox("Selecciona l'àmbit", categorias)

    # Filtrar dataframe por categoría
    if categoria_seleccionada == "Tots":
        df_filtrado_categoria = df.copy()
    else:
        df_filtrado_categoria = df[df['Descripcio_Ambit'] == categoria_seleccionada]
    
    # Información de depuración para el primer filtrado
    with st.expander("Estat després del filtre d'àmbit"):
        st.write(f"Àmbit seleccionat: {categoria_seleccionada}")
        st.write(f"Registres després del filtre d'àmbit: {len(df_filtrado_categoria)}")
        if len(df_filtrado_categoria) > 0:
            st.write("Preguntes disponibles després del filtre d'àmbit:")
            st.write(sorted(df_filtrado_categoria['Descripcio_Pregunta'].unique().tolist()))

    # Filtrar subcategorías basadas en la categoría seleccionada
    subcategorias = ["Totes"] + sorted(df_filtrado_categoria['Descripcio_Pregunta'].unique().tolist())
    
    # Selección de subcategoría
    subcategoria_seleccionada = st.sidebar.selectbox("Selecciona la pregunta que vulguis consultar", subcategorias)

    # Aplicar filtro de subcategoría
    if subcategoria_seleccionada == "Totes":
        df_filtrado = df_filtrado_categoria.copy()
    else:
        # Usamos .str.strip() para eliminar espacios en blanco antes de comparar
        df_filtrado = df_filtrado_categoria[df_filtrado_categoria['Descripcio_Pregunta'].str.strip() == subcategoria_seleccionada.strip()]
    
    # Información de depuración para el segundo filtrado
    with st.expander("Estat després del filtre de pregunta"):
        st.write(f"Pregunta seleccionada: {subcategoria_seleccionada}")
        st.write(f"Registres després del filtre de pregunta: {len(df_filtrado)}")
        if len(df_filtrado) > 0:
            st.write("Exemples de registres (primers 5):")
            st.dataframe(df_filtrado.head())

    # Mostrar palabras más comunes en los datos filtrados
    if not df_filtrado.empty:
        st.subheader(f"Dades filtrades: {len(df_filtrado)} registres")
        
        # Opciones adicionales
        with st.expander("Opcions avançades"):
            # Mostrar algunas de las stopwords como ejemplo
            st.write("S'estan excloent paraules de la llibreria stopwords automàticament, tant en espanyol com en català.")
            
            # Mostrar algunas stopwords de ejemplo sin usar expander anidado
            st.write("Algunes stopwords d'exemple:")
            st.write(", ".join(sorted(list(stopwords_combined))[:30]))
            st.write(f"Total de stopwords: {len(stopwords_combined)}")
            
            # Permitir añadir palabras adicionales a excluir
            palabras_adicionales = st.text_area(
                "Paraules addicionals a excloure (separades amb comes)",
                value=""
            )
            
            # Combinar stopwords predefinidas con palabras adicionales
            palabras_adicionales = [p.strip() for p in palabras_adicionales.split(',') if p.strip()]
            palabras_excluir = list(stopwords_combined) + palabras_adicionales
            
            max_palabras = st.slider("Màxim nombre de paraules en el núvol", 20, 200, 100)
        
        # Unir todos los textos filtrados
        todos_textos = " ".join(df_filtrado['Resposta_Qualitativa'].apply(limpiar_texto))
        
        # Generar y mostrar la nube de palabras
        titulo = f"Àmbit: {categoria_seleccionada if categoria_seleccionada != 'Tots' else 'Tots'}. "
        titulo += f"\nPregunta: {subcategoria_seleccionada if subcategoria_seleccionada != 'Totes' else 'Totes'}"
        
        fig = generar_nube_palabras(todos_textos, titulo, palabras_excluir)
        
        if fig:
            st.pyplot(fig)
        
        # Mostrar palabras más frecuentes
        # st.subheader("Paraules més freqüents")
        palabras = [p for p in todos_textos.split() if p not in palabras_excluir and len(p) > 2]
        contador = Counter(palabras).most_common(20)
        
        if contador:
            df_freq = pd.DataFrame(contador, columns=['Palabra', 'Frecuencia'])
            
            # Ordenar de mayor a menor frecuencia
            df_freq = df_freq.sort_values('Frecuencia', ascending=False)
            
            # Crear un gráfico personalizado para mostrar los datos ordenados
            fig, ax = plt.subplots(figsize=(9, 6))
            bars = ax.barh(df_freq['Palabra'], df_freq['Frecuencia'], color='steelblue')
            ax.set_xlabel('Freqüència')
            ax.set_ylabel('Paraula')
            ax.set_title('Paraules més freqüents')
            
            # Añadir los valores en las barras
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                        f'{width:.0f}', ha='left', va='center', fontsize = 8)
            
            # Invertir el orden para que la más frecuente esté arriba
            plt.gca().invert_yaxis()
            
            st.pyplot(fig)
    else:
        st.warning("No hi ha dades satisfent els filtres seleccionats.")
        
        # Información de diagnóstico adicional
        st.error("""
        Possibles causes del problema:
        1. Els valors en 'Descripcio_Pregunta' poden contenir espais addicionals o diferents majúscules/minúscules.
        2. És possible que no hi hagi registres amb aquesta combinació específica d'àmbit i pregunta.
        
        Recomanacions:
        1. Verifica que els valors en el fitxer Excel coincideixen exactament amb els valors mostrats en els desplegables.
        2. Intenta seleccionar 'Tots/Totes' en un dels filtres per veure si apareixen dades.
        """)

except Exception as e:
    st.error(f"S'ha produït un error: {str(e)}")
    import traceback
    st.code(traceback.format_exc())

# Información adicional
st.sidebar.markdown("---")
st.sidebar.info(""" 
    Aquesta aplicació permet generar núvols de paraules basades en les respostes dels ciutadans filtrant per àmbit i pregunta.
    
    Per modificar el fitxer de dades utilitzat:
    1. Reemplaça la ruta del fitxer en la línia on es carrega el fitxer Excel.
    2. Assegura't de mantindre sempre la mateixa nomenclatura a les columnes. Si no es manté, s'haurà d'adaptar el codi i s'obtindran errors.
""")