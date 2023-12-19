
#############################################
#                                           #
#    Función para parsear logonpasswords    #
#                                           #
#############################################
# FUNCION LOGONPASSWORD_TEST
def parse_logonpasswords(data):
    
    from cerberus.utils import clean_lower, clean_none, is_hex, re, copy
    output = []
    sections=[]
    section = []
    # bloque = []


    d_template={ "username":None,
        "domain":None,
        "logon_server":None,
        "logon_time":None,
        "sid":None,
            "msv":{ "username":None,
                    "domain":None,
                    "lm":None,
                    "ntlm":None,
                    "sha1":None},
            "tspkg":{"username":None,
                     "domain":None,
                     "password":None},
            "wdigest":{"username":None,
                     "domain":None,
                     "password":None},
            "kerberos":{"username":None,
                     "domain":None,
                     "password":None},
            # "ssp":{},
            # "credman":{}
       }

    for index,line in enumerate(data):
        # get number of spaces at the beginning of the line
        num_espacios = len(re.match(r'^\s*', line).group(0))
        # end of section (2 spaces and empty line) -> Ahora es 1 espacio y linea vacia
        if num_espacios==0  and line.strip()== "" and len(section)>3:
            sections.append(section)
            section = []
            continue
        else:
            section.append(line.strip("\n"))
    
    for section in sections:
        # d=d_template.copy()
        d=copy.deepcopy(d_template)

        d["username"]=clean_none(section[2])
        d["domain"]=clean_none(section[3])
        d["logon_server"]=clean_none(section[4])
        d["logon_time"]=section[5].split(": ")[1].strip()
        d["sid"]=section[6].split(":")[1].strip()


        name_subsection=""
        msv_index=None
        tspkg_index=None
        wdigest_index=None
        kerberos_index=None

        
        # Sacamos el indice de cada sección
        for index, line in enumerate(section[7:]):
            num_espacios = len(re.match(r'^\s*', line).group(0))
            if num_espacios == 1:
                name_subsection = line.strip()[:-2]
                continue
            elif num_espacios == 2:
                if name_subsection=="msv" and "Primary" in line:
                    msv_index=index+8
                elif name_subsection=="tspkg" and "* Username" in line:
                    tspkg_index=index+7
                elif name_subsection=="wdigest" and "* Username" in line:
                    kerberos_index=index+7
                elif name_subsection=="kerberos" and "* Username" in line:
                    wdigest_index=index+7
                # etc

        # con el indice de cada sección, sacamos los datos
        if msv_index is not None:
            d["msv"]["username"]=clean_none(section[msv_index+0])
            d["msv"]["domain"]=clean_none(section[msv_index+1])
            # _=clean_lower(section[msv_index+0]);d["msv"]["username"]=_ if _!="(null)" else None
            # _=clean_lower(section[msv_index+1]);d["msv"]["domain"]=_ if _!="(null)" else None
            if "NTLM" in section[msv_index+2]:
                d["msv"]["ntlm"]=clean_none(section[msv_index+2])
                d["msv"]["sha1"]=clean_none(section[msv_index+3])
                # _=clean_lower(section[msv_index+2]);d["msv"]["ntlm"]=_ if _!="(null)" else None
                # _=clean_lower(section[msv_index+3]);d["msv"]["sha1"]=_ if _!="(null)" else None
            else:
                d["msv"]["lm"]=clean_none(section[msv_index+2])
                d["msv"]["ntlm"]=clean_none(section[msv_index+3])
                d["msv"]["sha1"]=clean_none(section[msv_index+4])
                # _=clean_lower(section[msv_index+2]);d["msv"]["lm"]=_ if _!="(null)" else None
                # _=clean_lower(section[msv_index+3]);d["msv"]["ntlm"]=_ if _!="(null)" else None 
                # _=clean_lower(section[msv_index+4]);d["msv"]["sha1"]=_ if _!="(null)" else None 
            
                

        if tspkg_index is not None:
            # Comprobamos si la contraseña es hexadecimal, si es no rellenamos los datos
            p=clean_none(section[tspkg_index+2])
            # _=clean_lower(section[tspkg_index+2]);p=_ if _!="(null)" else None

            if p is None:
                pass
            elif is_hex(p):
                pass
            else:
                d["tspkg"]["username"]=clean_none(section[tspkg_index+0])
                d["tspkg"]["domain"]=clean_none(section[tspkg_index+1])
                # _=clean_lower(section[tspkg_index+0]); d["tspkg"]["username"]=_ if _!="(null)" else None 
                # _=clean_lower(section[tspkg_index+1]); d["tspkg"]["domain"]=_ if _!="(null)" else None 
                d["tspkg"]["password"]=p            

        if wdigest_index is not None:
            p=clean_none(section[wdigest_index+2])
            # _=clean_lower(section[wdigest_index+2]);p=_ if _!="(null)" else None

            if p is None:
                pass
            elif is_hex(p):
                pass
            else:
                d["wdigest"]["username"]=clean_none(section[wdigest_index+0])
                d["wdigest"]["domain"]=clean_none(section[wdigest_index+1])
                # _=clean_lower(section[wdigest_index+0]); d["wdigest"]["username"]=_ if _!="(null)" else None 
                # _=clean_lower(section[wdigest_index+1]); d["wdigest"]["domain"]=_ if _!="(null)" else None 
                d["wdigest"]["password"]=p

        if kerberos_index is not None:
            p=clean_none(section[kerberos_index+2])
            # _=clean_lower(section[kerberos_index+2]);p=_ if _!="(null)" else None

            if p is None:
                pass
            elif is_hex(p):
                pass
            else:
                d["kerberos"]["username"]=clean_none(section[kerberos_index+0])
                d["kerberos"]["domain"]=clean_none(section[kerberos_index+1])
                # _=clean_lower(section[kerberos_index+0]);d["kerberos"]["username"]=_ if _!="(null)" else None 
                # _=clean_lower(section[kerberos_index+1]);d["kerberos"]["domain"]=_ if _!="(null)" else None 
                d["kerberos"]["password"]=p
        
        output.append(d)
        
    return output
 
            
# ----------------------Fin parse_logonpassword-----------------------------------------

#############################################
#                                           #
#    Función para insertar logonpasswords   #
#                                           #
#############################################
# FUNCION LOGONPASSWORD_TEST
def insert_longonpasswords(section, session):
    from cerberus import models as m
    # import db
    from cerberus.utils import isLocal, calculate_ntlm, current_datetime

    if section['username'] is None:
        return
    ### ES LOCAL ###
    if isLocal(section['sid']): # Es local
        # Es una maquina
        if section['username'][-1] == '$':
            machine=m.Machines.get(hostname=section['username'])
            # Si no existe la maquina la creamos
            if machine is None:
                machine=m.Machines(hostname=section['username'], domain=section['domain'], sid=section['sid'], ntlm=section['msv']['ntlm'],date=current_datetime())
                session.add(machine)
                session.commit()
            else:
                if machine.ntlm is None:
                    machine.update(ntlm=section['msv']['ntlm'], domain=section['domain'])
        # NO es una maquina
        else:
            if section['domain']=='nt authority' or section['domain']=='window manager' :
                pass
            else:
                # Meter para usuario locales de la máquina.
                pass
    ### ES DOMINIO ###
    else:
        from cerberus.utils import checkneo4j, userAsOwned
        neo4j=checkneo4j()
        user=m.DomainUsers.get(user=section['username'], domain=section['domain'])
        # Si no existe el usuario lo creamos
        if user is None:
            user=m.DomainUsers(user=section['username'], domain=section['domain'], logon_server=section['logon_server'], logon_time=section['logon_time'], sid=section['sid'], date=current_datetime())
            session.add(user)
            session.commit()
        else:
            pass # ACTUALIZAR DATOS

        # CREDENCIALES
        msv=False
        tspkg=False
        wdigest=False
        kerberos=False
        password=None

        if section['msv']['ntlm'] is not None:
            msv=True
            cred=m.Credentials.get(ntlm=section['msv']['ntlm'])
            # Si no existe la credencial la creamos
            if cred is None:
                cred=m.Credentials(ntlm=section['msv']['ntlm'], msv=msv, location=2, date=current_datetime())
                session.add(cred)
                session.commit()
            else:
                if cred.location==0:
                    cred.update(location=2, msv=True)
                elif cred.location==1:
                    cred.update(location=3, msv=True)
                
        
        
        if section['tspkg']['password'] is not None:
            tspkg=True
            password=section['tspkg']['password']
        if section['wdigest']['password'] is not None:
            wdigest=True
            password=section['wdigest']['password']
        if section['kerberos']['password'] is not None:
            kerberos=True
            password=section['kerberos']['password']

        if password is not None:
            hash=calculate_ntlm(password)
            cred=m.Credentials.get(ntlm=hash)
            # Si no existe la credencial la creamos
            if cred is None:
                cred=m.Credentials(plain=password, ntlm=hash, tspkg=tspkg, wdigest=wdigest, kerberos=kerberos,location=2, date=current_datetime())
                session.add(cred)
                session.commit()
            else:
                if cred.plain is None:
                    cred.plain=password

                if cred.location==0:
                    cred.location=2
                elif cred.location==1:
                    cred.location=3

                if tspkg:
                    cred.tspkg=True
                if wdigest:
                    cred.wdigest=True
                if kerberos:
                    cred.kerberos=True
                session.add(cred)
                session.commit()

        #Creamos la relación entre el usuario y la credencial, añadiendo la fecha de la última vez que se ha visto
        relation=m.CredsDomainUsers.get(domainuser_id=user.id, cred_id=cred.id)
        if relation is None:
            session.add(m.CredsDomainUsers(domainuser_id=user.id, cred_id=cred.id, date=current_datetime()))
            # session.commit()
        else:
            relation.date=current_datetime()
            # session.add(relation)
        user.owned=True
        session.commit()
        if neo4j:
            userAsOwned(user)