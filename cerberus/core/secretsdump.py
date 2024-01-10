#############################################
#                                           #
#        Función para parsear secretsdump   #
#                                           #
#############################################

# FUNCION SECRETSDUMP
def parse_secretsdump(data, session):
    from cerberus import models as m
    # import db
    from cerberus.utils import current_datetime, checkneo4j, userAsOwned
    neo4j=checkneo4j()
    dc=False

    sam=[]
    cached_domain_logon=[]
    drsuapi=[[],[],[]]
    kerberos_keys=[[],[]]
    machine_acc=[]
    
    # Devuelve el apartado donde se encuentra
    def getApartado(line):
        main_words=["SAM","cached domain logon",
                    "LSA","$MACHINE.ACC","$MACHINE.ACC","DefaultPassword",
                    "DPAPI_SYSTEM","DPAPI_SYSTEM_history","NL$KM","NL$KM_history","Domain Credentials",
                    "DRSUAPI","Kerberos keys","Cleaning up..."]
        for i in main_words:
            if i in line:
                
                return i
    aux_apartado="SAM"
    d_template={"domain":None,
                        "machine":None,
                        "aes128":None,
                        "aes256":None,
                        "des":None,
                        "ntlm":None,
                        }
    k_template={"machine":None,
                "aes128":None,
                "aes256":None,
                "des":None,}
    for index,line in enumerate(data):
        
        if line.startswith("[*]"):
            aux_apartado=getApartado(line)
            continue
        
        if aux_apartado=="Cleaning up...":# Final documento
            break

        if aux_apartado=="SAM":
            if line.startswith("[-]"):
                continue
            _=line.split(":")
            d={"user":_[0],"lm":_[2],"nt":_[3].strip("\n")}
            sam.append(d)
        elif aux_apartado=="cached domain logon":
            _=line.split(":")
            d={"domain":_[0].split("/")[0].lower(),"user":_[0].split("/")[1],"hash":_[1].split("#")[2].strip("\n")}
            cached_domain_logon.append(d)
        elif aux_apartado=="LSA":
            pass
        elif aux_apartado=="$MACHINE.ACC":
            
            # d=copy.deepcopy(d_template)
            # _=line.split(":")

            # d={"domain":_[0].split("\\")[0],"machine":_[0].split("\\")[1].strip("$")}
            # if d not in machine_acc: # Se guardan los maquinas sin repetir
            #     machine_acc.append(d)

            _=line.split(":")
            if d_template["domain"] is None:
                d_template["domain"]=_[0].split("\\")[0].lower()
            if d_template["machine"] is None:
                d_template["machine"]=_[0].split("\\")[1].lower()
            if "aes128" in _[1] and d_template["aes128"] is None:
                d_template["aes128"]=_[2].strip("\n")
            elif "aes256" in _[1] and d_template["aes256"] is None:
                d_template["aes256"]=_[2].strip("\n")
            elif "des" in _[1] and d_template["des"] is None:
                d_template["des"]=_[2].strip("\n")
            elif "plain" in _[1]:
                pass
            else:
                if d_template["ntlm"] is None:
                    d_template["ntlm"]=_[2].strip("\n")

        elif aux_apartado=="$MACHINE.ACC_history":
            pass

        elif aux_apartado=="DefaultPassword":
            pass
        elif aux_apartado=="DPAPI_SYSTEM": # Se quiere? (Protege contraseñas en el equipo)
            pass
        elif aux_apartado=="DPAPI_SYSTEM_history": # Se quiere?
            pass
        elif aux_apartado=="NL$KM": # Se quiere?
            pass
        elif aux_apartado=="NL$KM_history": # Se quiere?
            pass
        # Output de dc
        elif aux_apartado=="Domain Credentials": # No hay datos
            dc=True
            pass
        # --- DOMINIO ---
        elif aux_apartado=="DRSUAPI":
            _=line.split(":")
            if "_history" in _[0]: # Si es historico
                normal=_[0].split("_history")[0]
                if normal[-1] == "$": # Si es una maquina pasamos
                    pass
                else: # Si es un usuario
                    d={"user":normal,"lm":_[2],"nt":_[3]}
                    if d not in drsuapi[2]:
                        drsuapi[2].append(d)

            else: # Si es actual
                if _[0][-1] == "$":
                    d={"machine":_[0].lower(),"lm":_[2],"nt":_[3]}
                    if d not in drsuapi[0]: # Se guardan los equipos sin repetir
                        drsuapi[0].append(d)
                else:
                    d={"user":_[0],"lm":_[2],"nt":_[3]}
                    if d not in drsuapi[1]: # Se guardan los usuarios sin repetir
                        drsuapi[1].append(d)        
                pass
        elif aux_apartado=="Kerberos keys":
            _=line.split(":")
            if _[0][-1] == "$":
                if k_template["machine"] is None:
                    k_template["machine"]=_[0].lower()
                elif k_template["machine"] is not None and k_template["machine"] != _[0].lower():
                    # kerberos_keys[0].append(k_template)
                    k_template={"machine":_[0].lower(),
                                "aes128":None,
                                "aes256":None,
                                "des":None,}
                if "aes128" in _[1] and k_template["aes128"] is None:
                    k_template["aes128"]=_[2].strip("\n")
                elif "aes256" in _[1] and k_template["aes256"] is None:
                    k_template["aes256"]=_[2].strip("\n")
                elif "des" in _[1] and k_template["des"] is None:
                    k_template["des"]=_[2].strip("\n")
                else:
                    pass
                if k_template["aes128"] is not None and k_template["aes256"] is not None and k_template["des"] is not None:
                    kerberos_keys[0].append(k_template)

                # if _ not in kerberos_keys[0]: # Se guardan los equipos sin repetir
                #     kerberos_keys[0].append(_)
            else:
                if _[0] not in kerberos_keys[1]: # Se guardan los usuarios sin repetir
                    kerberos_keys[1].append(_[0])
            pass
        
    
    
    pass
    

    # Insertamos la maquina en la bbdd
    
    machine_acc=m.Machines.get(hostname=d_template["machine"])
    if machine_acc is None:
        machine_acc=m.Machines(hostname=d_template["machine"],domain=d_template["domain"],aes128=d_template["aes128"],aes256=d_template["aes256"],des=d_template["des"],ntlm=d_template["ntlm"], date=current_datetime())
        session.add(machine_acc)
        session.commit()
    else:
        domain=d_template["domain"]
        if machine_acc.aes128 is None:
            machine_acc.aes128=d_template["aes128"]
        if machine_acc.aes256 is None:
            machine_acc.aes256=d_template["aes256"]
        if machine_acc.des is None:
            machine_acc.des=d_template["des"]
        if machine_acc.ntlm is None:
            machine_acc.ntlm=d_template["ntlm"]
        session.commit()

    # SAM
    for i in sam:
        cred=m.Credentials.get(ntlm=i['nt'])
        if cred is None:
            cred=m.Credentials(ntlm=i['nt'],location=0, date=current_datetime())
            session.add(cred)
            session.commit()
        else:
            if cred.ntlm is None:
                cred.ntlm=i['nt']
            if cred.location == 1:
                cred.location=2
            session.commit()
        user=m.LocalUsers.get(user=i['user'], machine_id=machine_acc.id)
        if user is None:
            user=m.LocalUsers(user=i['user'],machine_id=machine_acc.id, date=current_datetime())
            session.add(user)
            session.commit()
            tmp=m.CredsLocalUsers(cred_id=cred.id,localuser_id=user.id, date=current_datetime())
            session.add(tmp)
            session.commit()
        else:
            a=m.CredsLocalUsers.get(cred_id=cred.id,localuser_id=user.id)
            if a is None:
                tmp=m.CredsLocalUsers(cred_id=cred.id,localuser_id=user.id, date=current_datetime())
                session.add(tmp)
                session.commit()
            else:
                a.date=current_datetime()
                session.commit()
                

    # Cached domain logon

    for i in cached_domain_logon:
        cred=m.Credentials.get(ntlm=i['hash'])
        if cred is None:
            cred=m.Credentials(ntlm=i['hash'],location=1, date=current_datetime())
            session.add(cred)
            session.commit()
        else:
            if cred.location == 0:
                cred.location=2
                session.commit()

        user=m.DomainUsers.get(user=i['user'], domain=i['domain'])
        if user is None:
            user=m.DomainUsers(user=i['user'],domain=i['domain'], date=current_datetime(), owned=True)
            session.add(user)
            session.commit()
            tmp=m.CredsDomainUsers(cred_id=cred.id,domainuser_id=user.id, date=current_datetime())
            session.add(tmp)
            session.commit()
            if neo4j:userAsOwned(user)
        else:
            a=m.CredsDomainUsers.get(cred_id=cred.id,domainuser_id=user.id)
            if a is None:
                tmp=m.CredsDomainUsers(cred_id=cred.id,domainuser_id=user.id, date=current_datetime())
                session.add(tmp)
                # session.commit()
            else:
                a.date=current_datetime()
                
            user.owned=True
            session.commit()
            if neo4j:userAsOwned(user)
    
    # DRSUAPI
    # # Machines
    for i in drsuapi[0]:
        machine=m.Machines.get(hostname=i['machine'])
        if machine is None:
            machine=m.Machines(hostname=i['machine'],domain=d_template['domain'],ntlm=i['nt'], date=current_datetime())
            session.add(machine)
            session.commit()
        else:
            if machine.domain is None:
                machine.domain=d_template['domain']
            if machine.ntlm is None:
                machine.ntlm=i['ntlm']
            session.commit()
    # # Users
    for i in drsuapi[1]:
        if "\\" in i['user']: # Si tiene dominio en el nombre
            location=2
        else:
            location=1

        #cred
        cred=m.Credentials.get(ntlm=i['nt'])
        if cred is None:
            cred=m.Credentials(ntlm=i['nt'],location=location, date=current_datetime())
            session.add(cred)
            session.commit()
        else:
            if (cred.location == 2 and location == 1) or (cred.location == 1 and location == 2):
                cred.location=3
            else:
                cred.location=location
            session.commit()
        
        #user
        if location==2:  # dominio
            user=m.DomainUsers.get(user=i['user'].split("\\")[1], domain=i['user'].split("\\")[0])
            if user is None:
                user=m.DomainUsers(user=i['user'].split("\\")[1],domain=i['user'].split("\\")[0], date=current_datetime(), owned=True)
                session.add(user)
                session.commit()
                tmp=m.CredsDomainUsers(cred_id=cred.id,domainuser_id=user.id, date=current_datetime())
                session.add(tmp)
                session.commit()

                if neo4j:userAsOwned(user)
            else:
                a=m.CredsDomainUsers.get(cred_id=cred.id,domainuser_id=user.id)
                if a is None:
                    tmp=m.CredsDomainUsers(cred_id=cred.id,domainuser_id=user.id, date=current_datetime())
                    session.add(tmp)
                    # session.commit()
                else:
                    a.date=current_datetime()
                    # session.commit()
                user.owned=True
                session.commit()
                if neo4j:
                    userAsOwned(user)
        else: # local
            user=m.LocalUsers.get(user=i['user'], machine_id=machine_acc.id)
            if user is None:
                user=m.LocalUsers(user=i['user'],machine_id=machine_acc.id, date=current_datetime())
                session.add(user)
                session.commit()
                tmp=m.CredsLocalUsers(cred_id=cred.id,localuser_id=user.id, date=current_datetime())
                session.add(tmp)
                session.commit()
            else:
                a=m.CredsLocalUsers.get(cred_id=cred.id,localuser_id=user.id)
                if a is None:
                    tmp=m.CredsLocalUsers(cred_id=cred.id,localuser_id=user.id, date=current_datetime())
                    session.add(tmp)
                    session.commit()
                else:
                    a.date=current_datetime()
                    session.commit()
    # # Users history
    for i in drsuapi[2]:
        if "\\" in i['user']: # Si tiene dominio en el nombre
            location=2
        else:
            location=1

        #cred
        cred=m.Credentials.get(ntlm=i['nt'])
        if cred is None:
            cred=m.Credentials(ntlm=i['nt'],location=location, date=current_datetime())
            session.add(cred)
            session.commit()
        else:
            if (cred.location == 2 and location == 1) or (cred.location == 1 and location == 2):
                cred.location=3
            else:
                cred.location=location
            session.commit()
        
        #user
        if location==2:  # dominio
            user=m.DomainUsers.get(user=i['user'].split("\\")[1], domain=i['user'].split("\\")[0])
            if user is None:
                user=m.DomainUsers(user=i['user'].split("\\")[1],domain=i['user'].split("\\")[0], date=current_datetime(), owned=False)
                session.add(user)
                session.commit()
                tmp=m.CredsDomainUsers(cred_id=cred.id,domainuser_id=user.id, date=current_datetime(), historical=True)
                session.add(tmp)
                session.commit()
            else:
                a=m.CredsDomainUsers.get(cred_id=cred.id,domainuser_id=user.id)
                if a is None:
                    tmp=m.CredsDomainUsers(cred_id=cred.id,domainuser_id=user.id, date=current_datetime(), historical=True)
                    session.add(tmp)
                    # session.commit()
                else:
                    a.date=current_datetime()
                    # session.commit()
                user.owned=False
                session.commit()
        else: # local
            user=m.LocalUsers.get(user=i['user'], machine_id=machine_acc.id)
            if user is None:
                user=m.LocalUsers(user=i['user'],machine_id=machine_acc.id, date=current_datetime())
                session.add(user)
                session.commit()
                tmp=m.CredsLocalUsers(cred_id=cred.id,localuser_id=user.id, date=current_datetime(), historical=True)
                session.add(tmp)
                session.commit()
            else:
                a=m.CredsLocalUsers.get(cred_id=cred.id,localuser_id=user.id)
                if a is None:
                    tmp=m.CredsLocalUsers(cred_id=cred.id,localuser_id=user.id, date=current_datetime(), historical=True)
                    session.add(tmp)
                    session.commit()
                else:
                    a.date=current_datetime()
                    session.commit()

    # Kerberos
    # # Machines
    for i in kerberos_keys[0]:
        machine=m.Machines.get(hostname=i['machine'])
        if machine is None:
            machine=m.Machines(hostname=i['machine'],domain=d_template['domain'],aes128=i['aes128'],aes256=i['aes256'],des=i['des'], date=current_datetime())
            session.add(machine)
            # session.commit()
        else:
            if machine.domain is None:
                machine.domain=d_template['domain']
            if machine.aes128 is None:
                machine.aes128=i['aes128']
            if machine.aes256 is None:
                machine.aes256=i['aes256']
            if machine.des is None:
                machine.des=i['des']
        session.commit() 
    # # Users
    for i in kerberos_keys[1]:
        if "\\" in i: #dominio
            location=2
        else:
            location=1

        if location==1:
            user=m.LocalUsers.get(user=i, machine_id=machine_acc.id)
            if user is None:
                user=m.LocalUsers(user=i,machine_id=machine_acc.id, date=current_datetime())
                session.add(user)
                session.commit()
            else:
                pass
        else:
            user=m.DomainUsers.get(user=i.split("\\")[1], domain=i.split("\\")[0])
            if user is None:
                user=m.DomainUsers(user=i.split("\\")[1],domain=i.split("\\")[0], date=current_datetime())
                session.add(user)
                session.commit()
            else:
                pass



def insert_secretsdump(data):
    pass
