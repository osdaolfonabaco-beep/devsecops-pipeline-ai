import os
import anthropic
from dotenv import load_dotenv

# Cargar variables de entorno (ANTHROPIC_API_KEY) desde el archivo .env
load_dotenv()

# Configurar la API key de Anthropic
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Error: ANTHROPIC_API_KEY no encontrada.")
    print("Asegúrate de tener un archivo .env con tu clave.")
    exit(1)

# Inicializar el cliente de Anthropic
client = anthropic.Anthropic(api_key=api_key)

def read_file_content(filepath):
    """Lee y devuelve el contenido de un archivo."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en {filepath}")
        return None
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return None

def get_security_analysis(file_content, filename):
    """
    Envía el contenido del archivo a Anthropic Haiku para análisis de seguridad.
    """
    print(f"--- Iniciando análisis de IA (Haiku) para: {filename} ---")
    
    # El prompt del sistema es el mismo, define el rol de la IA
    SYSTEM_PROMPT = """
    Eres un experto en ciberseguridad y DevSecOps con 20 años de experiencia.
    Tu tarea es analizar el siguiente archivo de código en busca de vulnerabilidades 
    de seguridad y malas prácticas.
    
    Para cada vulnerabilidad encontrada:
    1.  Identifica el tipo de vulnerabilidad (ej. SQL Injection, S3 Public Access).
    2.  Cita la(s) línea(s) de código exactas que son problemáticas.
    3.  Explica por qué es una vulnerabilidad.
    4.  Proporciona una sugerencia de código para remediar el problema.
    
    Si no encuentras vulnerabilidades, indícalo explícitamente.
    Responde en formato Markdown.
    """
    
    USER_PROMPT = f"""
    Analiza el siguiente archivo: `{filename}`
    
    Contenido del archivo:
    ```
    {file_content}
    ```
    """
    
    try:
        # Usamos la API de Mensajes de Anthropic
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            temperature=0.2,
            system=SYSTEM_PROMPT, # El prompt de sistema va aquí
            messages=[
                {"role": "user", "content": USER_PROMPT}
            ]
        )
        
        # La respuesta se encuentra en el atributo content[0].text
        return message.content[0].text
        
    except Exception as e:
        return f"Error durante el análisis de IA: {e}"

if __name__ == "__main__":
    # Lista de archivos a analizar. Usamos rutas relativas desde la raíz.
    files_to_analyze = [
        "app/main.py",
        "infra/main.tf"
    ]
    
    for file_path in files_to_analyze:
        content = read_file_content(file_path)
        if content:
            analysis_report = get_security_analysis(content, file_path)
            print(analysis_report)
            print("--- Análisis completado --- \n")
