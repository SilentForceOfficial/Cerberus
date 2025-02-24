

from flask import current_app
import json
nmapxml_upload_path=f"{current_app.root_path}/static/.tmp"



#############################################
#                                           #
#     Funciones para las tecnologías        #
#                                           #
#############################################

def getProductVulnerabilities(productVendor, productName, productVersion):
    
    import requests

    # Variables necesarias
    atlasVulnsAPI = "https://atlas.silentforce.io/api/v1/_internal/vulnerabilities"
    vulnsApiRequestParams = dict(
        cpe_product = productName.lower(),
        cpe_vendor = productVendor.lower()
    ) if not productVersion else dict(
        cpe_product = productName.lower(),
        cpe_vendor = productVendor.lower(),
        cpe_version = productVersion
    )
    productVulnerabilities = []

    # Obtenemos las vulnerabilidades de la API de Atlas
    response = requests.get(atlasVulnsAPI, vulnsApiRequestParams)
    if response.status_code == 200:
        productVulnerabilities = response.json()
    
    return productVulnerabilities

def parseServicesTechnologies(session,data):
    try:
        # Convertir el JSON a un objeto Python
        data_obj = json.loads(data)
        # Acceder a la lista de datos
        data_list = data_obj.get('data', [])

        for item in data_list:
            
            # Obtener los valores requeridos de cada item
            target = item.get('target')
            port=item.get('port')
            product_name = item.get('productName')
            product_vendor = item.get('productVendor')
            product_version = item.get('productVersion')

            # Obtener las vulnerabilidades del producto
            product_vulnerabilities = item.get('productVulnerabilities', [])
            cve_list = []
            base_severity_list = []





            for vuln in product_vulnerabilities:
                cve = vuln.get('cve')
                cve_list.append(cve)

                cvss_v3 = vuln.get('cvss_v3', {})
                base_severity = cvss_v3.get('base_severity')
                base_severity_list.append(base_severity)

            
            uploadDataServicesTechnologies(session=session, target=target, product_vendor=product_vendor, product_name=product_name, product_version=product_version, cve_list=cve_list, base_severity_list=base_severity_list,port=port)
                    
        
        return True
    except Exception as e:
        print(f"Error parsing JSON data: {e}")
        return False


# ----------------------------- FIN DE parseTechnologies-----------------------------------------


#############################################
#                                           #
#       Función para subir los datos        #
#                                           #
#############################################

def uploadDataServicesTechnologies(session, target, product_vendor, product_name, product_version, cve_list, base_severity_list, port='', hostname_target=''):
    from cerberus import models as m
    try:
        # Verificar que las listas cve_list y base_severity_list tengan la misma longitud
        if len(cve_list) != len(base_severity_list):
            raise ValueError("Las listas cve_list y base_severity_list deben tener la misma longitud")

        if(len(cve_list)==0):
                uploadDataToDB(session=session,ip_target=target, port=port, vendor=product_vendor, product=product_name, version=product_version, cve=None, risk=None, hostname_target=None)
        else:
            for cve, severity in zip(cve_list, base_severity_list):
                uploadDataToDB(session=session,ip_target=target, port=port, vendor=product_vendor, product=product_name, version=product_version, cve=cve, risk=severity, hostname_target=None)
                
        session.commit()
        return True

    except Exception as e:
        print(f"Error uploading data to Technologies table: {e}")
        session.rollback()
        return False

# ----------------------------- FIN DE uploadDataNMAP-----------------------------------------

def uploadDataToDB(session, ip_target ,port, vendor, product, version, cve, risk=None, hostname_target=None):
    from cerberus import models as m
    existing_record = session.query(m.Technologies).filter_by(ip_target=ip_target, port=port, vendor=vendor, product=product, version=version,cve=cve).first()

    if not existing_record:
        # Si el registro no existe, creamos una nueva instancia y la agregamos a la sesión
        tech = m.Technologies(ip_target=ip_target, port=port, vendor=vendor,
                            product=product, version=version,
                            cve=cve, risk=risk, hostname_target=hostname_target)
        session.add(tech)