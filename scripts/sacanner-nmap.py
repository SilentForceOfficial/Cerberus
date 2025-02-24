import nmap
from colorama import Fore
import argparse, requests

# ========== DECLARACIONES CONSTANTES ==========
NIST_CPES_API = "https://services.nvd.nist.gov/rest/json/cpes/2.0"
ATLAS_VULNS_API = "https://atlas.silentforce.io/api/v1/_internal/vulnerabilities"


def print_banner(title):
    banner_length = len(title) + 4
    print("\n" + "*" * banner_length)
    print(f"* {title} *")
    print("*" * banner_length + "\n")

def getProductVendor(productName: str) -> str:

    # Variables necesarias
    productVendor: str = ""

    # Obtenemos el vendor del producto mediante la API del NIST
    requestResult = requests.get(NIST_CPES_API, params=dict(
        cpeMatchString = f"cpe:2.3:*:*:{productName.lower()}",
        resultsPerPage = 1
    ))
    
    if requestResult.status_code == 200:
        if len(requestResult.json()["products"]) > 0:
            productVendor = requestResult.json()["products"][0]["cpe"]["cpeName"].split(":")[3]
    else:
        print(f"{Fore.RED}[X] ERROR: The vendor of '{productName}' has not been found, status code: {requestResult.status_code}{Fore.RESET}")

    return productVendor

def getProductVulnerabilities(cpeProduct: str, cpeVendor: str, cpeVersion: str = "") -> list[dict[str, any]]:

    # Variables necesarias
    requestParams: dict
    productVulnerabilities: list[dict[str, any]] = []

    # Construimos los parámetros en función de si sabemos la versión o no
    requestParams = dict(
        cpe_product = cpeProduct.lower(),
        cpe_vendor = cpeVendor.lower()
    ) if cpeVersion == "" else dict(
        cpe_product = cpeProduct.lower(),
        cpe_vendor = cpeVendor.lower(),
        cpe_version = cpeVersion
    )

    # Obtenemos las vulnerabilidades del producto
    requestResult = requests.get(ATLAS_VULNS_API, params=requestParams)

    if requestResult.status_code == 200:
        productVulnerabilities = requestResult.json()
    else:
        print(f"[X] ERROR: The vulnerabilities of '{cpeProduct} - {cpeVersion} ({cpeVendor})' have not been found, status code: {requestResult.status_code}")
    
    return productVulnerabilities


def sendInfo(url: str, info: list[dict[str, any]]) -> bool:

    # Mandamos la información por post a la ruta y comprobamos el código de respuesta
    requestResult = requests.post(url, json={"data": info})
    return requestResult.status_code != 200



def buildSoftwareVulnerabilitiesJSON(
    targetURL: str,
    port: str,
    productName: str, 
    productVendor: str, 
    productVulnerabilities: list[dict[str, any]],
    productVersion: str = "" 
) -> dict[str, any]:
    return {
        "target": targetURL,
        "port": port,
        "productName": productName,
        "productVendor": productVendor,
        "productVersion": productVersion,
        "productVulnerabilities": productVulnerabilities
    }



def scan_network(scanner, timing, sV, sC, verbose, port, target, exfilURL, xml_output=None ):
    # Variables necesarias
    softwareVulnerabilities: list[dict[str, any]] = []
    productVulnerabilities: list[dict[str, any]]
    analysisResultsIndex: int = 0

    # results_dict 
    results_dict = {}
    # Make the argument 
    scan_arguments = ""
    if timing:
        scan_arguments += f"-T{timing} "
    if sV:
        scan_arguments += "-sV "
    if sC:
        scan_arguments += "-sC "
    if verbose:
        scan_arguments += "-vvv "
    
    # Start the scam
    scanner.scan(target, port, arguments=scan_arguments)
    
    # Print the results
    for host in scanner.all_hosts():

        host_info = {}
        host_info['ports'] = []

        print("\n")
        print(f"Host: {host} ({scanner[host].hostname()})")
        print(f"State: {scanner[host].state()}")
        for proto in scanner[host].all_protocols():
            print("----------")
            print(f"Protocol: {proto}")
            lport = scanner[host][proto].keys()
            for port in sorted(lport):
                service_info = scanner[host][proto][port]
                service = service_info.get('name', 'unknown service')

                product = service_info.get('product', '')
                version = service_info.get('version', '')
                extra_info = service_info.get('extrainfo', '')

                productVendor = getProductVendor(productName=product.split(" ")[0])


                    
                productVulnerabilities = getProductVulnerabilities(cpeProduct=product, cpeVendor=productVendor, cpeVersion=version)
                softwareVulnerabilities.append(buildSoftwareVulnerabilitiesJSON(
                    targetURL=host,
                    port=port,
                    productName=product,
                    productVendor=productVendor,
                    productVersion=version,
                    productVulnerabilities=productVulnerabilities
                ))

                
                
                # Guardar la información del puerto en el diccionario del host
                host_info['ports'].append({
                    'port': port,
                    'service': service,
                    'product': product,
                    'version': version
                })

    # Mandamos los resultados a la API
    print(f"{Fore.CYAN}[*] Sending data to server...{Fore.RESET}")
    if(sendInfo(url=exfilURL, info=softwareVulnerabilities)):
        print(f"{Fore.RED}[X] ERROR: The information found couldn't be sent to the server{Fore.RESET}")
        return
    
    
    print(f"{Fore.GREEN}[+] Data sent to server successfully{Fore.RESET}")
        
    print(softwareVulnerabilities)
    # Export a XML File
    if xml_output:
        xml_data = scanner.get_nmap_last_output()
        if isinstance(xml_data, bytes):
            xml_data = xml_data.decode('utf-8')  # Transform to bytes 
        with open(xml_output, 'w') as xml_file:
            xml_file.write(xml_data)

    return results_dict





def main():
    parser = argparse.ArgumentParser(description='Network Scanner with customizable options.')
    parser.add_argument('--target', help='Specifies the target IP or range (e.g., 192.168.1.1 or 192.168.1.0/24)', required=True)
    parser.add_argument('-U', '--exfil-url', help='Sets Exfil Web URL', required=True)
    parser.add_argument('-T', '--timing', help='Sets the timing for the scan (e.g., -T4 for a faster scan)', required=True)
    parser.add_argument('-sV', action='store_true', help='Enables version detection of services', required=False)
    parser.add_argument('-sC', action='store_true', help='Executes default Nmap scripts against detected targets', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase verbosity level (-vvv for more verbose output)', required=False)
    parser.add_argument('-p', '--port', help='Specifies port range (e.g., 22-80)', required=False)
    parser.add_argument('--nmap-path', help='Specifies the custom path to the Nmap executable', required=False, default="nmap")
    parser.add_argument('-oX','--xml-output', help='Exports the scan result to an XML file at the specified path', required=False)
    
    args = parser.parse_args()
    
    print_banner("Version Detector")

    # Create the scanner object with the custom Nmap path
    nm = nmap.PortScanner(nmap_search_path=(args.nmap_path,))
    
    # Realizar el escaneo y obtener los resultados
    scan_results = scan_network(nm, args.timing, args.sV, args.sC, args.verbose, args.port, args.target,args.exfil_url ,args.xml_output)
    
    # Imprimir los resultados
    for host, info in scan_results.items():
        print(f"\nHost: {host}")
        for port_info in info['ports']:
            print(f"Port: {port_info['port']}\tService: {port_info['service']}\tProduct: {port_info['product']}\tVersion: {port_info['version']}")



if __name__ == "__main__":
    main()
