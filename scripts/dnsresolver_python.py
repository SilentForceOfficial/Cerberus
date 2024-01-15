import socket
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

# Función para resolver la dirección IP de un nombre de host
def resolver_ip(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return "not resolved"

def resolver_ip_concurrente(host):
    return host, resolver_ip(host)

def main():
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description="Resolve IP addresses of host names in a file using threads.")
    parser.add_argument("input_file", help="Path to the input file containing host names.")
    parser.add_argument("output_file", help="Path to the output file where results will be saved.")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of threads to use (default: 5).")
    parser.add_argument("-r", "--resolved-only", action="store_true", help="Output only the resolved hosts.")
    args = parser.parse_args()

    # Leer nombres de host desde el archivo de entrada
    with open(args.input_file, "r") as file:
        hosts = file.readlines()

    # Resolver IPs de manera concurrente usando hilos
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        resultados = list(executor.map(resolver_ip_concurrente, map(str.strip, hosts)))

    # Filtrar solo los hosts resueltos si la opción está activada
    if args.resolved_only:
        resueltas = [(host, ip) for host, ip in resultados if ip != "not resolved"]
        no_resueltas = []
    else:
        # Separar las entradas resueltas y no resueltas
        resueltas = []
        no_resueltas = []
        for host, ip in resultados:
            if ip != "not resolved":
                resueltas.append((host, ip))
            else:
                no_resueltas.append((host, ip))

    # Preparar las líneas de salida
    lineas_salida = [f"{host}->{ip}\n" for host, ip in resueltas] + [f"{host}-{ip}\n" for host, ip in no_resueltas]

    # Escribir los resultados en el archivo de salida
    with open(args.output_file, "w") as file:
        file.writelines(lineas_salida)

    print(f"{len(hosts)} hosts detected.")
    print(f"|-{len(resueltas)} hosts resolved.")
    print(f"|-{len(no_resueltas)} hosts not resolved.")
    print(f"Results output: '{args.output_file}'.")

if __name__ == "__main__":
    init_time = time.time()
    main()
    print(f"Time elapsed: {time.time() - init_time} seconds.")
