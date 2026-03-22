import os
import json
from datetime import datetime
import yt_dlp

def get_download_directory():
    """Determina directorio de descarga según el entorno"""
    if os.getenv('GITHUB_ACTIONS') == 'true':
        temp_dir = os.getenv('RUNNER_TEMP', '/tmp')
        download_dir = os.path.join(temp_dir, 'youtube_downloads')
    else:
        download_dir = os.path.join(
            os.path.expanduser('~'), 
            'Downloads', 
            'YouTube_Downloader'
        )
    
    os.makedirs(download_dir, exist_ok=True)
    return download_dir

def descargar_video_con_metadatos(url, calidad='highest'):
    """
    Descarga video y guarda metadatos usando yt-dlp
    """
    try:
        download_dir = get_download_directory()
        print(f"📁 Directorio: {download_dir}")
        
        # Configurar formato según calidad
        if calidad == 'highest':
            format_spec = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        elif calidad == 'audio':
            format_spec = 'bestaudio[ext=m4a]/bestaudio'
        else:  # lowest
            format_spec = 'worst[ext=mp4]/worst'
        
        ydl_opts = {
            'format': format_spec,
            'outtmpl': os.path.join(download_dir, '%(id)s_%(title).50s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extraer info sin descargar primero
            print("🔍 Obteniendo información del video...")
            info = ydl.extract_info(url, download=False)
            
            print(f"🎬 Título: {info.get('title', 'Desconocido')}")
            print(f"👤 Canal: {info.get('uploader', 'Desconocido')}")
            print(f"⏱️  Duración: {info.get('duration', 0)} segundos")
            
            # Crear metadatos
            duration = info.get('duration', 0)
            metadatos = {
                'titulo': info.get('title'),
                'descripcion': info.get('description'),
                'canal': info.get('uploader'),
                'url': url,
                'url_canonical': info.get('webpage_url'),
                'duracion_segundos': duration,
                'duracion_formateada': f"{duration // 60}:{duration % 60:02d}" if duration else "N/A",
                'vistas': info.get('view_count'),
                'fecha_publicacion': info.get('upload_date'),
                'video_id': info.get('id'),
                'thumbnail_url': info.get('thumbnail'),
                'tags': info.get('tags', []),
                'categorias': info.get('categories', []),
                'fecha_descarga': datetime.now().isoformat(),
                'calidad_descarga': calidad,
                'formato': info.get('format'),
                'resolucion': info.get('resolution'),
            }
            
            video_id = info.get('id')
            
            # Guardar metadatos JSON
            metadata_file = os.path.join(download_dir, f"{video_id}_metadatos.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadatos, f, ensure_ascii=False, indent=2)
            print(f"💾 Metadatos guardados: {metadata_file}")
            
            # Guardar descripción en TXT
            descripcion_file = os.path.join(download_dir, f"{video_id}_descripcion.txt")
            with open(descripcion_file, 'w', encoding='utf-8') as f:
                f.write(f"TÍTULO: {info.get('title', 'N/A')}\n")
                f.write(f"CANAL: {info.get('uploader', 'N/A')}\n")
                f.write(f"URL: {url}\n")
                f.write(f"URL CANONICAL: {info.get('webpage_url', 'N/A')}\n")
                f.write(f"FECHA: {info.get('upload_date', 'N/A')}\n")
                f.write(f"DURACIÓN: {metadatos['duracion_formateada']}\n")
                f.write(f"VISTAS: {info.get('view_count', 'N/A')}\n")
                f.write("=" * 50 + "\n")
                f.write("DESCRIPCIÓN:\n")
                f.write("=" * 50 + "\n")
                f.write(info.get('description') or "Sin descripción")
            print(f"📝 Descripción guardada: {descripcion_file}")
            
            # Descargar video
            print(f"⬇️  Descargando video...")
            ydl.download([url])
            
            # Encontrar el archivo descargado
            downloaded_files = [f for f in os.listdir(download_dir) if f.startswith(video_id) and not f.endswith(('.json', '.txt'))]
            if downloaded_files:
                video_path = os.path.join(download_dir, downloaded_files[0])
                file_size = os.path.getsize(video_path)
                print(f"✅ Video guardado: {video_path}")
                print(f"📊 Tamaño: {file_size / 1024 / 1024:.2f} MB")
                
                return {
                    'video_path': video_path,
                    'metadata_path': metadata_file,
                    'descripcion_path': descripcion_file,
                    'video_id': video_id,
                    'titulo': info.get('title'),
                    'tamaño_mb': file_size / 1024 / 1024
                }
            else:
                print("⚠️  No se encontró el archivo descargado")
                return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Descargar video de YouTube con metadatos')
    parser.add_argument('--url', required=True, help='URL del video de YouTube')
    parser.add_argument('--calidad', default='highest', choices=['highest', 'lowest', 'audio'])
    args = parser.parse_args()
    
    resultado = descargar_video_con_metadatos(args.url, args.calidad)
    
    if resultado:
        print(f"\n{'='*60}")
        print("RESUMEN DE DESCARGA:")
        print(f"{'='*60}")
        print(f"Video: {resultado['video_path']}")
        print(f"Metadatos: {resultado['metadata_path']}")
        print(f"Descripción: {resultado['descripcion_path']}")
        print(f"Tamaño: {resultado['tamaño_mb']:.2f} MB")
        print(f"{'='*60}")
    else:
        print("La descarga falló")
        exit(1)
