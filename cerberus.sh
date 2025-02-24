#!/bin/bash

# Function to display general help menu
show_help() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --install         Install and configure the environment"
  echo "    -U, --user        Specify the username (default: cerberus)"
  echo "    -P, --password    Specify the password (default: cerberus)"
  echo "  Example:"
  echo "    sudo $0 --install -U myuser -P mypassword"
  echo ""
  echo "  --run             Run the application"
  echo "    -h, --host        Specify the host (default: 127.0.0.1)"
  echo "    -p, --port        Specify the password (default: 5000)"
  echo "    -v, --debug       Enable debug mode"
  echo "  Example:"
  echo "    sudo $0 --run -h 0.0.0.0 -p 8080"
  echo ""
  echo "  --reconfigure     Reconfigure the application"
  echo "    -U, --user        Specify the username (default: cerberus)"
  echo "    -P, --password    Specify the password (default: cerberus)"
  echo "  Example:"
  echo "    sudo $0 --reconfigure -U myuser -P mypassword"
  echo ""
}

# Default values
USER_PARAM="cerberus"
PASSWORD_PARAM="cerberus"
HOST_PARAM="127.0.0.1"
PORT_PARAM="5000"
DEBUG_FLAG=false
INSTALL_FLAG=false
RUN_FLAG=false
RECONFIGURE_FLAG=false

echo "              ..--++####++---.                    
            .######### -#########.             
         .##### ##  ##          ####.          
       .###+      ##-          ##  ###.       
     .###                     ##     ###.      
    .##-    +###-        ######        ##+.    
   .####   ##   ##########   #       ## ###.   
  .##  ##   #####        #####       ##  ##.   
 .######                               #  ##.  
 .##                                      ###. 
 .##                                       ##. 
 .#-     #####       #####-       #####    ##. 
 .#   +###   ##      #+  ##########   ##   ##. 
 .#####  -####      ######         ####   .##. 
 .##               ##                     ###. 
 .###             ##                      ##.  
  .######-    #####                  ### ##.   
   .##  ##   ##   #     ######     .##  ##-.   
    .###-     ####+     ##  ##      ##.##.     
     .###                ######-     ###.      
       .####      ###          ##.-###.        
         .#####  ##  #+         ####.          
            .#######-##+#########.
               ..---+++++---.. "


# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -U|--user) USER_PARAM="$2"; shift ;;
    -P|--password) PASSWORD_PARAM="$2"; shift ;;
    -h|--host) HOST_PARAM="$2"; shift ;;
    -p|--port) PORT_PARAM="$2"; shift ;;
    -v|--debug) DEBUG_FLAG=true ;;
    --install) INSTALL_FLAG=true ;;
    --run) RUN_FLAG=true ;;
    --reconfigure) RECONFIGURE_FLAG=true ;;
    -h|--help) show_help; exit 0 ;;
    *) echo "Unknown parameter passed: $1"; show_help; exit 1 ;;
  esac
  shift
done

# Check for mutually exclusive flags
FLAG_COUNT=0
if [ "$INSTALL_FLAG" = true ]; then
  FLAG_COUNT=$((FLAG_COUNT + 1))
fi
if [ "$RUN_FLAG" = true ]; then
  FLAG_COUNT=$((FLAG_COUNT + 1))
fi
if [ "$RECONFIGURE_FLAG" = true ]; then
  FLAG_COUNT=$((FLAG_COUNT + 1))
fi

if [ "$FLAG_COUNT" -gt 1 ]; then
  echo "Error: --install, --run, and --reconfigure flags are mutually exclusive."
  show_help
  exit 1
fi

if [ "$FLAG_COUNT" -eq 0 ]; then
  show_help
  exit 1
fi

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root."
  exit 1
fi


install_environment() {
  #Update package list and install venv if not installed
  echo "[+] Updating package list"
  apt update

  echo "[+] Installing python3 venv"
  apt install -y python3-venv

  # Install Docker
  echo "[+] Installing docker"
  apt install -y docker.io
  systemctl enable docker --now

  # Add user to docker group
  echo "[+] Adding current user to docker's group"
  usermod -aG docker $USER

  # Create virtual environment .cerberusenv
  echo "[+] creating venv"
  python3 -m venv .cerberusenv

  # Install dependencies in cerberusenv
  echo "[+] Installing dependencies"
  .cerberusenv/bin/pip install -r requirements.txt

  echo "[+] Environment installed successfully."
  reconfigure_application
}

run_application() {
  echo "[+] Running the application"
  # Aquí puede ir el comando para ejecutar la aplicación
  if [ "$DEBUG_FLAG" = true ]; then
    .cerberusenv/bin/flask --debug --app cerberus run --host=$HOST_PARAM --port=$PORT_PARAM
  else
    .cerberusenv/bin/flask --app cerberus run --host=$HOST_PARAM --port=$PORT_PARAM
  fi
  
  echo "[+] Cerberus running on http://$HOST_PARAM:$PORT_PARAM"
}

reconfigure_application() {
  # Run Flask command with user and password parameters
  echo "[+] Configuring cerberus"
  .cerberusenv/bin/flask --app cerberus setup --user "$USER_PARAM" --password "$PASSWORD_PARAM"

  echo "[+] CERBERUS successfully configured"
  echo "[+]     User - $USER_PARAM"
  echo "[+]     Password - $PASSWORD_PARAM"
}



if [ "$INSTALL_FLAG" = true ]; then
  install_environment
fi

if [ "$RUN_FLAG" = true ]; then
  run_application
fi

if [ "$RECONFIGURE_FLAG" = true ]; then
  reconfigure_application
fi

if [ "$INSTALL_FLAG" = false ] && [ "$RUN_FLAG" = false ] && [ "$RECONFIGURE_FLAG" = false ]; then
  show_help
fi


