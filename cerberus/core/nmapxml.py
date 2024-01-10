

from flask import current_app

nmapxml_upload_path=f"{current_app.root_path}/static/.tmp"



#############################################
#                                           #
#        Función para parsear nmapxml       #
#                                           #
#############################################
"""
Esta funcion se encarga del parseo de un fichero .xml en busqueda de los datos como la ip, puertos abiertos y hostname de la maquina.
Precondiciones: Ninguna
Parametros:
    0 -> filePath [String]: Cadena con la ruta al archivo a analizar
Retorno
    0 -> Data [Diccionario]: Dinccionario con el formato de clave IP, valor [lista de hostname, lista de puertos]
    

"""
def parseXML(filePath):
    import xml.etree.ElementTree as ET
    
    try:
        # Crear un diccionario para almacenar la información
        data = {}

        # Parsear el XML
        tree = ET.parse(filePath)
        root = tree.getroot()

        # Iterar sobre los elementos de host
        for host in root.iter("host"):
            # Obtener la dirección IP
            ip = host.find("address").get("addr")

            # Obtener los hostnames de tipo "user"
            hostnames = [hostname.get("name") for hostname in host.findall("hostnames/hostname[@type='PTR']")]

            # Obtener los puertos abiertos
            open_ports = [port.get("portid") for port in host.iter("port") if port.find("state").get("state") == "open"]

            # Almacenar la información en el diccionario
            data[ip] = [hostnames, open_ports]
      
       
        return data
    except Exception as e:
        # Lanzar una excepción con un mensaje de error
        file=filePath.split("/")[-1]
        raise Exception(f"Error al analizar el archivo XML: {file}")

# ----------------------------- FIN DE PARSEXML-----------------------------------------


#############################################
#                                           #
# Función para subir los datos del nmapxml  #
#                                           #
#############################################
"""
Esta funcion se encarga del parseo de un fichero .xml en busqueda de los datos como la ip, puertos abiertos y hostname de la maquina.
Precondiciones: Ninguna
Parametros:
    0 -> data [Diccionario]: Diccionario con la información del parseo
    1 -> session [db obcject]: objeto con la conexion a la bbdd
Retorno: Ninguno
    

"""
def uploadDataNmap(data,session,filename):
    from cerberus.utils import checkneo4j
    from cerberus import models as m
    neo4j=checkneo4j()

    for ip in data:

        if(len(data[ip][0])):
            hostname,domain=data[ip][0][0].split(".",1)
            hostname=hostname+'$'
            ports=data[ip][1]
            #DATOS REALES PARA SACER EL DOMINIO A PARTIR DE LOS HOSTNAMES
            #Actualizamos los datos en la base de datos
            if (len(hostname)>0):
                machine=m.Machines.get(hostname=hostname)
                if machine is None:
                    machine=m.Machines(hostname=hostname,domain=domain.lower(),ip=ip)
                    session.add(machine)
                    session.commit()
                else:
                    if machine.ip is None:
                        machine.ip = ip
                    session.commit()
            
            if(len(ports))>0:
                if neo4j: machineAsNmapTarget(machine,filename)

def machineAsNmapTarget(machine,filename):
    from neo4j import GraphDatabase
    from flask import g
    
    try:
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
            # Asumiendo que tienes un nodo con la etiqueta "Machine" y una propiedad "hostname"
            driver.execute_query(f"MATCH (m:Computer) WHERE m.name='{machine.hostname}' SET m.nmapTarget = True")
            driver.execute_query("MERGE (:File {fileName: '"+filename+"'})")
            driver.execute_query("MATCH (m:Computer {name: '"+machine.hostname+"'}) MATCH (file:File {fileName: '"+filename+"'}) MERGE (m)-[:SALIDA_DE]->(file)")
            #MERGE (:File {fileName: 'archivo1'});
            #MATCH (m:Computer {name: "ARES-MAD-DC01.ARESBANK.ES"})
            #File {fileName: 'archivo1'})
            #MERGE (m)-[:SALIDA_DE]->(file);

    except Exception as e:
        print("Error al actualizar neo4j")
        print(e)






        
        





# ----------------------------- FIN DE uploadDataNMAP-----------------------------------------
