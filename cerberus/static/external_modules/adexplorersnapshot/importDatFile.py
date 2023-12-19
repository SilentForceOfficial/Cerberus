

# ========== IMPORTADO DE BIBLIOTECAS ==========
from .adexpsnapshot.adexpsnapshot import parseDatFile

import os, zipfile, subprocess

# ========== CODIFICACIÓN DE FUNCIONES ==========
def importDatFile(inputFileName, outputZIP):

    outputFolder = "cerberus/static/.tmp/adExplorerSnapshot"

    # Abrimos el fichero e intentamos parsearlo
    with open(inputFileName, "rb") as snapshot:
        parseDatFile(snapshot=snapshot, output=outputFolder)

    # Empaquetamos los ficheros en un zip
    with zipfile.ZipFile(outputZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(outputFolder):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file),
                        os.path.join(outputFolder, '..')
                    )
                )
    
    # Eliminamos la carpeta temporal
    subprocess.Popen(["rm", "-rf", outputFolder])
    