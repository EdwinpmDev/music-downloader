# Librerias / libraries
import yt_dlp
from yt_dlp import YoutubeDL

# Estructura
def recibir_enlace(): 
    enlace = input("Pega el enlace del video: ")
    urls = [enlace]
    print(f"Enlace incrustado: ", enlace)
    return urls

            
def descarga_video(recibir_enlace):
    with YoutubeDL() as ydl:
        ydl.download(recibir_enlace)


def descarga_audio(recibir_enlace):
    print(f"Escoge el formato de audio para descargar:  \n1.- m4a \n2.- aac \n3.- mp3 \n4.- ogg \n5.- opus \n6.- webm" )
    while True:
        opcion_formato = int(input("\nFormato: "))
        if opcion_formato == 1:
            formato_selecc = 'm4a'
            break
        elif opcion_formato == 2:
            formato_selecc = 'aac'
            break
        elif opcion_formato == 3:
            formato_selecc = 'mp3'
            break
        elif opcion_formato == 4:
            formato_selecc = 'ogg'
            break
        elif opcion_formato == 5:
            formato_selecc = 'opus'
            break
        elif opcion_formato == 6:
            formato_selecc = 'webm'
            break
        else:
            print("Opción invalida, vuelva a intentarlo.")

    ydl_opts = {
        'format': f'{formato_selecc}/bestaudio/best',

        'postprocessors': [{  
        'key': 'FFmpegExtractAudio',
        'preferredcodec': formato_selecc,
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(recibir_enlace)

def menu():
    print(f"---------MENÚ DE SELECCIÓN---------", "\n1.- Video", "\n2.- Audio", "\n3.- Salir")

def ejecutar_menu():
    while True:
        menu()
        opcion = int(input(f"Ingresé su selección: "))

        # VIDEO
        if opcion == 1:
            print(f"\n----Ha seleccionado la opción 1 [Video]----")
            urls = recibir_enlace()
            descarga_video(urls)
        # AUDIO
        elif opcion == 2:
            print(f"\n----Ha seleccionado la opción 2 [Audio]----")
            urls = recibir_enlace()
            descarga_audio(urls)
        # SALIR DEL PROGRAMA
        elif opcion == 3:
            print(f"\n----Ha seleccionado la opción 3 [Salir]----")
            break
        else:
            print(f"\nOpción no valida, intenta de nuevo.")

if __name__ == "__main__":
    ejecutar_menu() 