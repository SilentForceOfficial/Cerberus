# Función para detectar encoding del fichero
import binascii
import codecs
import copy
import hashlib
import re
from passlib.hash import nthash


#############################################
#                                           #
#     Función para dectectar el encoding    #
#                                           #
#############################################
# Función para detectar encoding del fichero
def detectEncoding(f):
    """
    This helper method returns the file encoding corresponding to path f.
    This handles UTF-8, which is itself an ASCII extension, so also ASCII.
    """
    encoding = 'ascii'
    try:
        with codecs.open(f, 'r', encoding='utf-16') as source:
            source.readline() # Read one line to ensure correct encoding
    except UnicodeError:
        try:
            with codecs.open(f, 'r', encoding='utf-8') as source:
                source.readline() # Read one line to ensure correct encoding
        except UnicodeError:
            with codecs.open(f, 'r', encoding='ascii') as source:
                source.readline() # Read one line to ensure correct encoding
        else:
            encoding = 'utf-8'
    else:
        encoding = 'utf-16'

    return encoding
# ------------------fin detectEncoding----------------

#############################################
#                                           #
#  Función para saber si es local o dominio #
#                                           #
#############################################
def isLocal(sid_data):
    sid=sid_data.split("-")
    if sid[-1] == "":
        pass
    elif int(sid[3]) != 21:
        return True
    else:
        if int(sid[-1]) >= 1000 and int(sid[-1]) <= 1100:
            return True
        else:
            return False
# ------------------fin isLocal----------------

#############################################
#                                           #
#        Función para crear hash NTLM       #
#                                           #
#############################################
# Función para crear hash NTLM a partir de la contraseña en texto plano
def calculate_ntlm(password):
    ntlm_hash = nthash.hash(password)
    return ntlm_hash

#############################################
#                                           #
#   Función para saber si es hexadecimal    #
#                                           #
#############################################
# Función para saber si es hexadecimal
def is_hex(password):

    # Comprobar si la contraseña es hexadecimal
    if re.search(r"[^0-9a-fA-F\s]", password):
        return False
    else:
        return True
    # return False if re.search(r"[^0-9a-fA-F\s]", password) else True
# ------------------fin is_hex----------------

#############################################
#                                           #
#   Función para leer el fichero de input   #
#                                           #
#############################################
# Leer el input_file
# def readFile(input_file, input_type):
#     # Set linea inicio
#     if input_type == 'logonpasswords':
#         start_line = "Authentication Id"
#     elif input_type == 'lsadump':
#         start_line = "lsadump::"
#     elif input_type == 'tickets':
#         start_line = "Authentication Id"
#     elif input_type == 'secretsdump':
#         start_line = "[*] Dumping local SAM hashes"

#     #Open input file
#     if detectEncoding(input_file) == 'ascii':
#         file = open(input_file, "r")
#     else:
#         file = codecs.open(input_file, "r", encoding=detectEncoding(input_file))

#     # Read file
#     lines=file.readlines()
#     init_index = 0
#     for index,line in enumerate(lines):
#         if start_line in line:
#             init_index = index
#             break
    
#     # data=[i.strip() for i in lines[init_index:]]
#     data=lines[init_index:]
    
#     # Close file
#     file.close()
#     return(data)
# ------------------fin readFile----------------

#############################################
#                                           #
#   Funcion para leer el fichero de input   #
#                    2                      #
#                                           #
#############################################
# Leer el input_file

def readFile2(input_data, input_type):
    # Set linea inicio
    if input_type == 'logonpasswords':
        start_line = "Authentication Id"
    elif input_type == 'lsadump':
        start_line = "lsadump::"
    elif input_type == 'tickets':
        start_line = "Authentication Id"
    elif input_type == 'secretsdump':
        start_line = "[*] Dumping local SAM hashes"

    # Read the content from BytesIO and decode as string
    input_data.seek(0)
    content = input_data.read().decode('utf-8')

    # Split the input data into lines
    lines = content.split('\n')

    init_index = 0
    for index, line in enumerate(lines):
        if start_line in line:
            init_index = index
            break

    # Extract the relevant lines
    data = lines[init_index:]

    return data

#############################################
#                                           #
#   Funcion para guardar un fichero en el   #
#           sistema de ficheros             #
#                                           #
#############################################
# Leer el input_file
def saveFile(input_data, upload_path):

    try:
        # Read the content from BytesIO
        content = input_data.read()

        # Check if upload_path exists
        import os
        if os.path.exists(upload_path):
            print("ERROR: Upload path not empty...")
            return True

        # Save the content to file
        with open(upload_path, "wb") as file:
            file.write(content)
        
        return False
    except Exception as e:
        print(e)
        return True

#############################################
#                                           #
#   Funcion para leer el fichero de import  #
#                 de hashcat                #
#                                           #
#############################################
# Leer el input_file

def readFileHashcat(input_data):
    # Read the content from BytesIO and decode as string
    input_data.seek(0)
    content = input_data.read().decode('utf-8')

    # Split the input data into lines
    lines = content.split('\n')

    cracked = []

    for line in enumerate(lines):
        # Agregar los valores separados a la lista
        line=line[1]
        cracked.append(line.strip().split(':'))

    return cracked

#############################################
#                                           #
#   Funcion para leer el fichero de import  #
#                 de dnsresolver            #
#                                           #
#############################################
# Leer el input_file

def readFileDNSResolver(input_data):
    # Read the content from BytesIO and decode as string
    input_data.seek(0)
    content = input_data.read().decode('utf-8')

    # Split the input data into lines
    lines = content.split('\n')

    results = []

    for line in enumerate(lines):
        # Agregar los valores separados a la lista
        line=line[1]
        results.append(line.strip().split('->'))

    return results

#*******************************************#
#                                           #
#   Funciones para parsear ficheros de      #
#   input de diferentes tipos               #
#                                           #
#*******************************************#

def clean_lower(data):
    return data.split(":")[1].strip().lower()

def clean_none(data):
    _=clean_lower(data)
    if _!="(null)":
        return _
    else:
        return None


#*******************************************#
#                                           #
#   Funciones para obtener el formato de    #
#  la fecha de los tickets a partir de los  #
#  segundos ficheros de input               #
#                                           #
#*******************************************#
def convertir_tiempo(segundos):
    import datetime
    fecha = datetime.datetime.fromtimestamp(segundos)
    formato = fecha.strftime("%d/%m/%Y %H:%M:%S")
    return formato

def current_datetime():
    import datetime
    fecha = datetime.datetime.now()
    formato = fecha.strftime("%d/%m/%Y %H:%M:%S")
    return formato





def checkneo4j():
    from neo4j import GraphDatabase
    from flask import g
    
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    if g.user["neo4j_user"] is None or g.user["neo4j_password"] is None or g.user["neo4j_url"] is None:
        return False
    
    try:
        with GraphDatabase.driver(uri=g.user["neo4j_url"], auth=(g.user["neo4j_user"], g.user["neo4j_password"])) as driver:
            with driver.session() as session:
                # Ejecutar una consulta de prueba para verificar la conectividad
                result = session.run("RETURN 1")
                print(result)
                return True
    except Exception as e:
        print(e)
        return False

def neo4jNodeAsOwned(nodeID, value="true"):
    from neo4j import GraphDatabase
    from flask import g
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    try:
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
            driver.execute_query(f"MATCH (n) WHERE ID(n) = {nodeID} SET n.owned = {value}")
    except Exception as e:
        print("Error al actualizar neo4j")
        print(e)

def userAsOwned(user, value="true"):
    from neo4j import GraphDatabase
    from flask import g
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    try:
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
            driver.execute_query(f"MATCH (n:User) WHERE n.samaccountname='{user.user}' SET n.owned = {value}")
    except Exception as e:
        print("Error al actualizar neo4j")
        print(e)

def usersAsOwned(users):
    from neo4j import GraphDatabase
    from flask import g
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    try:
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
            for user in users:
                try:
                    driver.execute_query(f"MATCH (n:User) WHERE n.samaccountname='{user.user}' SET n.owned = true")
                except:
                    print(f"ERROR: No se ha podido actualizar el usuario '{user.user}'")
                    pass
    except Exception as e:
        print("Error al actualizar neo4j")
        print(e)
        return ("danger", "Neo4j connection error")
    
    return ("success", "Neo4j synced successfully")

def nodeAsHighValue(nodeID, value="true"):
    from neo4j import GraphDatabase
    from flask import g
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    try:
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
            driver.execute_query(f"MATCH (n) WHERE ID(n) = {nodeID} SET n.highvalue = {value}")
    except Exception as e:
        print("Error al actualizar neo4j")
        print(e)

"""
    Nombre: neo4j Graph DashBoard
    Descripcion: Funcion para obetener los datos principales de neo4j sobre un dominio para ponerlos en el gráfico del dashboard
    Parametros: Ninguno 
    Retorno: Lista con el resultado de si ha ido bien y diccionario con los valores de neo4j en caso de que la conexion se estableca
"""
def neo4jGraphDashBoard():

    from neo4j import GraphDatabase
    from flask import g
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    
    try:
        #Establecemos conexión
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
                try:
                    cql=('''MATCH (u:User)
                            WITH count(u) AS userCount
                            
                            OPTIONAL MATCH (g:Group)
                            WITH userCount, count(g) AS groupCount
                            
                            OPTIONAL MATCH (c:Computer)
                            WITH userCount, groupCount, count(c) AS computerCount
                            
                            OPTIONAL MATCH (ou:OU)
                            WITH userCount, groupCount, computerCount, count(ou) AS ouCount
                            
                            OPTIONAL MATCH (gpo:GPO)
                            WITH userCount, groupCount, computerCount, ouCount, count(gpo) AS gpoCount
                            
                            OPTIONAL MATCH (d:Domain)
                            RETURN COALESCE(userCount, 0) AS userCount, COALESCE(groupCount, 0) AS groupCount, COALESCE(computerCount, 0) AS computerCount, COALESCE(ouCount, 0) AS ouCount, COALESCE(gpoCount, 0) AS gpoCount, COALESCE(count(d), 0) AS domainCount;
                        ''')

                    #Ejecutamos la qry y obtenemos los resultados
                    with driver.session() as graphDB_Session:
                        result = graphDB_Session.run(cql)
                        
                        result = result.single()
                        result = ('success', {'userCount': result [0], 'groupCount':result[1],'computerCount':result[2], 'ouCount':result[3],'gpoCount':result[4],'domainCount':result[5]})    

                except Exception as j:
                    result = ('danger',"ERROR: No se ha podido realizar la consulta del neo4jDashboard")
                    print(j)
                    pass
    except Exception as e:
        print("Error al realizar peticion neo4j")
        print(e)
        result = ("danger", "Neo4j connection error") 
    
    return result
