

# ========== IMPORTADO DE BIBLIOTECAS ==========
from Wappalyzer import Wappalyzer, WebPage
from colorama import Fore
import argparse, requests

# ========== DECLARACIONES CONSTANTES ==========
NIST_CPES_API = "https://services.nvd.nist.gov/rest/json/cpes/2.0"
ATLAS_VULNS_API = "https://atlas.silentforce.io/api/v1/_internal/vulnerabilities"

# ========== FUNCIÓN PRINCIPAL MAIN ==========
def main():

    # Variables necesarias
    args = getArgs()

    targetURL = args.url
    exfilURL = args.exfil_url

    softwareVulnerabilities = []

    # Mostramos los argumentos introducidos por el usuario
    print(Fore.BLUE + "========== Parameters ==========")
    print(f"- Target URL: {targetURL}")
    print(f"- Server URL: {exfilURL}")
    print("================================")
    print(Fore.RESET)

    # Realizamos el análisis de la web
    analysisResults = analyzeWeb(targetURL)

    # Obtenemos las posibles vulnerabilidades del software encontrado
    softwareVulnerabilities = getSoftwareVulns(targetURL=targetURL, analysisResults=analysisResults)
    print(softwareVulnerabilities)

    # Mandamos los resultados a la API
    print(f"{Fore.CYAN}[*] Sending data to server...{Fore.RESET}")
    if(sendInfo(url=exfilURL, info=softwareVulnerabilities)):
        print(f"{Fore.RED}[X] ERROR: The information found couldn't be sent to the server{Fore.RESET}")
        return
    
    print(f"{Fore.GREEN}[+] Data sent to server successfully{Fore.RESET}")

# ========== CODIFICACIÓN DE FUNCIONES ==========
def getArgs():

    # Variables necesarias
    parser = argparse.ArgumentParser(description="Wappalyzer agent for SilentForce tools")

    # Argumentos
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-U", "--exfil-url", required=True, help="Exfiltration URL")

    return parser.parse_args()

def analyzeWeb(url: str) -> dict[str, dict[str, any]]:

    # Variables necesarias
    wappalyzer = Wappalyzer.latest()
    analysisResults: dict

    try:

        # Obtenemos la página web
        print(f"{Fore.CYAN}[*] Analyzing '{url}'...{Fore.RESET}")
        webpage = WebPage.new_from_url(url)

        # Analizamos la página web
        analysisResults = wappalyzer.analyze_with_versions_and_categories(webpage)
        print(f"{Fore.GREEN}[+] Web analyzed successfully{Fore.RESET}\n")
        
    except Exception as e:
        print(f"{Fore.RED}[X] ERROR: Ha ocurrido una excepción al intentar analizar la web '{url}':\n{e}{Fore.RESET}\n")
    
    return analysisResults

def getSoftwareVulns(targetURL: str, analysisResults: dict[str, dict[str, any]]) -> list[dict[str, any]]:

    # Variables necesarias
    softwareVulnerabilities: list[dict[str, any]] = []
    productVulnerabilities: list[dict[str, any]]
    analysisResultsIndex: int = 0

    print(f"{Fore.CYAN}[*] Searching vulnerabilities in website technologies...{Fore.RESET}")

    # Recorremos todo el software encontrado
    for productName in analysisResults:

        analysisResultsIndex += 1
        print(f"{Fore.CYAN}[*] Checking '{productName}' ({analysisResultsIndex}/{len(analysisResults)})...{Fore.RESET}")

        # Obtenemos el vendor del producto
        print(f"{Fore.CYAN}[*] Searching product vendor...{Fore.RESET}")
        productVendor = getProductVendor(productName=productName)

        # Si no hemos encontrado el vendor del producto saltamos al siguiente
        if productVendor == "":
            print(f"{Fore.YELLOW}[!] Product vendor not found, skipping to the next{Fore.RESET}\n")
            continue
        
        print(f"{Fore.GREEN}[+] Product vendor found: {productVendor}{Fore.RESET}")

        # En caso de que tengamos versión del producto la incluímos en la búsqueda de vulnerabilidades
        print(f"{Fore.CYAN}[*] Starting vulnerabilities lookup...{Fore.RESET}")
        if len(analysisResults[productName]["versions"]) > 0:
            for productVersion in analysisResults[productName]["versions"]:
                productVulnerabilities = getProductVulnerabilities(cpeProduct=productName, cpeVendor=productVendor, cpeVersion=productVersion)
                softwareVulnerabilities.append(buildSoftwareVulnerabilitiesJSON(
                    targetURL=targetURL,
                    productName=productName,
                    productVendor=productVendor,
                    productVersion=productVersion,
                    productVulnerabilities=productVulnerabilities
                ))
        else:
            productVulnerabilities = getProductVulnerabilities(cpeProduct=productName, cpeVendor=productVendor)
            softwareVulnerabilities.append(buildSoftwareVulnerabilitiesJSON(
                targetURL=targetURL,
                productName=productName,
                productVendor=productVendor,
                productVulnerabilities=productVulnerabilities
            ))
        print(f"{Fore.GREEN}[+] Vulnerabilities lookup finished ({analysisResultsIndex}/{len(analysisResults)}){Fore.RESET}\n")
    
    return softwareVulnerabilities

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

def buildSoftwareVulnerabilitiesJSON(
    targetURL: str,
    productName: str, 
    productVendor: str, 
    productVulnerabilities: list[dict[str, any]],
    productVersion: str = "" 
) -> dict[str, any]:
    
    return {
        "target": targetURL,
        "productName": productName,
        "productVendor": productVendor,
        "productVersion": productVersion,
        "productVulnerabilities": productVulnerabilities
    }

def sendInfo(url: str, info: list[dict[str, any]]) -> bool:

    # Mandamos la información por post a la ruta y comprobamos el código de respuesta
    requestResult = requests.post(url, json={"data": info})
    return requestResult.status_code != 200

# ========== EJECUCIÓN PRINCIPAL ==========
if __name__ == "__main__":
    main()

