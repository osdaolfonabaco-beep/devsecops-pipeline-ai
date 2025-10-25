import os
import anthropic
import requests # Usaremos 'requests' para hablar con la API de GitHub
from dotenv import load_dotenv

# --- 1. CONFIGURACIÓN Y CARGA DE VARIABLES ---
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Variables del entorno de GitHub Actions
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
PR_NUMBER = os.getenv("PR_NUMBER")
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

if not ANTHROPIC_API_KEY:
    print("Error: ANTHROPIC_API_KEY no encontrada.")
    exit(1)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# --- 2. FUNCIONES DE ANÁLISIS (Sin cambios) ---

def read_file_content(filepath):
    """Lee y devuelve el contenido de un archivo."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: Archivo no encontrado en {filepath}"
    except Exception as e:
        return f"Error leyendo {filepath}: {e}"

def get_security_analysis(file_content, filename):
    """Envía el contenido del archivo a Anthropic Haiku."""
    print(f"--- Iniciando análisis de IA (Haiku) para: {filename} ---")
    
    SYSTEM_PROMPT = """
    Eres un experto en ciberseguridad y DevSecOps con 20 años de experiencia.
    Tu tarea es analizar el siguiente archivo de código en busca de vulnerabilidades 
    de seguridad y malas prácticas.
    
    Para cada vulnerabilidad encontrada:
    1.  Identifica el tipo de vulnerabilidad.
    2.  Cita la(s) línea(s) de código exactas que son problemáticas.
    3.  Explica por qué es una vulnerabilidad.
    4.  Proporciona una sugerencia de código para remediar el problema.
    
    Si no encuentras vulnerabilidades, indícalo explícitamente.
    Responde en formato Markdown.
    """
    
    USER_PROMPT = f"Analiza el siguiente archivo: `{filename}`\n\nContenido:\n```{file_content}```"
    
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            temperature=0.2,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": USER_PROMPT}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error durante el análisis de IA: {e}"

# --- 3. NUEVA FUNCIÓN: POSTEAR EN GITHUB ---

def post_comment_to_pr(report_body):
    """Publica el reporte de análisis como un comentario en el PR."""
    
    if not all([GITHUB_TOKEN, PR_NUMBER, GITHUB_REPOSITORY]):
        print("Faltan variables de entorno de GitHub. No se publicará el comentario.")
        return

    # Construye la URL de la API para los comentarios del PR
    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/issues/{PR_NUMBER}/comments"
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # El cuerpo del comentario que se publicará
    body = {
        "body": report_body
    }
    
    print(f"--- Publicando comentario en el Pull Request #{PR_NUMBER} ---")
    
    try:
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status() # Lanza un error si la petición falla (ej. 403, 404)
        print("¡Comentario publicado con éxito!")
    except requests.exceptions.RequestException as e:
        print(f"Error al publicar el comentario en GitHub: {e}")
        if e.response is not None:
            print(f"Respuesta del servidor: {e.response.text}")

# --- 4. SCRIPT PRINCIPAL (Modificado) ---

if __name__ == "__main__":
    files_to_analyze = [
        "app/main.py",
        "infra/main.tf"
    ]
    
    # Encabezado del reporte
    full_report = "## 🤖 Reporte de Análisis de Seguridad por IA (Haiku)\n\n"
    full_report += "He analizado los archivos modificados y he encontrado lo siguiente:\n\n"
    
    # Acumulamos todos los análisis en un solo reporte
    for file_path in files_to_analyze:
        content = read_file_content(file_path)
        analysis_report = get_security_analysis(content, file_path)
        
        full_report += f"### Análisis de: `{file_path}`\n"
        full_report += analysis_report
        full_report += "\n---\n" # Separador
    
    # Si estamos en un PR, publicamos el comentario.
    if PR_NUMBER:
        post_comment_to_pr(full_report)
    else:
        # Si no, solo imprimimos en la consola (como antes)
        print("--- EJECUCIÓN LOCAL O EN 'MAIN' (NO EN PR) ---")
        print(full_report)
