#############################################
#                                           #
#        Función para parsear lsadump       #
#                                           #
#############################################

# FUNCION LSADUMP
def parse_lsadump(data):
    from cerberus.utils import clean_lower, copy, current_datetime
    data_template={ "domain":None,
        "syskey":None,
        "sid":None,
        "samkey":None,
        "creds":[]
       }

    tipo=data[0].split("::")[1].strip()
    data.pop(0)
    if tipo=="sam":
        data_dict=copy.deepcopy(data_template)
        # Datos del equipo
        data_dict["domain"]=f'{clean_lower(data[0])}$'
        data_dict["syskey"]=clean_lower(data[1])
        data_dict["sid"]=clean_lower(data[2])
        data_dict["samkey"]=clean_lower(data[4])
        
        # id_maquina=insertMachineL(hostname, syskey, sid, samkey)
        users=[]
        cred_dict={"user":None,"lm":None,"ntlm":None}
        for i in data[5:]:
            if "RID" in i:
                cred_dict={"user":None,"lm":None,"ntlm":None}
                    
            elif "User" in i:
                cred_dict["user"]=i.split(":")[1].strip()
            elif "Hash LM" in i:
                cred_dict["lm"]=clean_lower(i)
            elif "Hash NTLM" in i:
                cred_dict["ntlm"]=clean_lower(i)
            
            if cred_dict["user"]!=None and cred_dict["ntlm"]!=None:
                data_dict["creds"].append(cred_dict)
                cred_dict={"user":None,"lm":None,"ntlm":None}
        return(data_dict)

    else:
        print("Not implemented yet")
# ----------------------Fin parse_lsadump-----------------------------------------

#############################################
#                                           #
#       Función para insertar lsadump       #
#                                           #
#############################################
# FUNCION LSADUMP_TEST

def insert_lsadump(data, session):
    from cerberus import models as m
    # import db
    from cerberus.utils import current_datetime

    machine=m.Machines.get(hostname=data['domain'])
    # Si no existe la maquina la creamos
    if machine is None:
        machine=m.Machines(hostname=data['domain'], sid=data['sid'], sam_key=data['samkey'], date=current_datetime())
        session.add(machine)
        session.commit()
    else:
        machine.update(sam_key=data['samkey'], sid=data['sid'])

    # Credenciales
    for cred in data['creds']:
        # Credencial
        c=m.Credentials.get(ntlm=cred['ntlm'])
        # Si no existe la credencial la creamos
        if c is None:
            if cred['lm'] is None:
                c=m.Credentials(ntlm=cred['ntlm'], date=current_datetime())
            else:
                c=m.Credentials(ntlm=cred['ntlm'], lm=cred['lm'], date=current_datetime())
            session.add(c)
            session.commit()
        else:
            if c.lm is None:
                c.update(lm=cred['lm'])
        #Usuario
        u=m.LocalUsers.get(user=cred['user'], machine_id=machine.id)
        # Si no existe el usuario lo creamos
        if u is None:
            u=m.LocalUsers(user=cred['user'], machine_id=machine.id, date=current_datetime())
            session.add(u)
            session.commit()
            
        # Credenciales de usuario
        relation=m.CredsLocalUsers.get(localuser_id=u.id, cred_id=c.id)
        if not relation:
            _=m.CredsLocalUsers(localuser_id=u.id, cred_id=c.id, date=current_datetime())
            session.add(_)
            session.commit()
        else:
            relation.date=current_datetime()
            # db.session.add(relation)
            session.commit()
        # if not m.CredsLocalUsers.get(localuser_id=u.id, cred_id=c.id):
        #     db.session.add(m.CredsLocalUsers(localuser_id=u.id, cred_id=c.id))
        #     db.session.commit()