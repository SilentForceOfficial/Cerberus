#!/bin/bash

# Función para imprimir la ayuda
function show_help {

    echo "Resolve IP addresses of host names in a file."
    echo ""
    echo "Arguments: "
    echo -e "\t-inputFile\t Path to the input file containing host names."
    echo -e "\t-outputFile\t Path to the output file where results will be saved."
    echo -e "\t-resolvedOnly\t Output only the resolved hosts."
    echo -e "\t-h, --help \t Show help."
    echo ""
    echo "Example: $0 -inputFile <archivo1> -outputFile <archivo2> [-onlyResolved]"
    exit 1
}

# Función para resolver la dirección IP de un nombre de host
resolver_ip() {
    local host=$1
    local ip
    ip=$(nslookup "$host" | awk '/^Address: / { print $2 }' | head -n 1)
    if [ -z "$ip" ]; then
        echo "not resolved"
    else
        echo "$ip"
    fi
}

# Función para resolver la dirección IP de manera concurrente
resolver_ip_concurrente() {
    local host=$1
    local ip
    ip=$(resolver_ip "$host")
    echo "$host-$ip"
}



# Verificar la cantidad de argumentos
if [ "$#" -lt 4 ] || [ "$#" -gt 5 ]; then
    show_help
fi

# Verificar si se proporciona el parámetro -h o --help en cualquier posición
for arg in "$@"; do
    if [ "$arg" = "-h" ] || [ "$arg" = "--help" ]; then
        show_help
    fi
done

# Inicializar variables
inputFile=""
outputFile=""
resolvedOnly=false

# Procesar argumentos
while [ "$#" -gt 0 ]; do
    case "$1" in
        -inputFile)
            inputFile="$2"
            shift 2
            ;;
        -outputFile)
            outputFile="$2"
            shift 2
            ;;
        -resolvedOnly)
            resolvedOnly=true
            shift
            ;;
        *)
            show_help
            ;;
    esac
done

# Verificar que se hayan proporcionado inputFile y outputFile
if [ -z "$inputFile" ] || [ -z "$outputFile" ]; then
    show_help
fi

# Verificar si el archivo de salida existe y borrarlo si es así
if [ -e "$outputFile" ]; then
    rm "$outputFile"
fi

# Inicializar arrays
resolvedDataArray=()
unresolvedDataArray=()
lineCont=0

while IFS= read -r line; do
    ((lineCont++))
    resolvedData=$(resolver_ip_concurrente "$line")

    # Verificar si la IP está resuelta
    if [[ "$resolvedData" == *not\ resolved* ]]; then
        unresolvedDataArray+=("$resolvedData")
    else
        resolvedDataArray+=("$resolvedData")
    fi

done < "$inputFile"

# Imprimir resultados en el outputFile según la condición
if $resolvedOnly; then
    for resolved in "${resolvedDataArray[@]}"; do
        echo "$resolved" >> "$outputFile"
    done
else
    for resolved in "${resolvedDataArray[@]}" "${unresolvedDataArray[@]}"; do
        echo "$resolved" >> "$outputFile"
    done
fi

echo "$lineCont host detected."
echo "|-${#resolvedDataArray[@]} hosts resolved."
echo "|-${#unresolvedDataArray[@]} hosts not resolved."
echo "Results output: '$outputFile'."


