from . import db2 as db

from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Float, Boolean
from sqlalchemy.sql.expression import func    
# Class Credentials
class Credentials(db.Base):
    __tablename__ = 'credentials'

    id = Column(Integer, primary_key=True)
    plain = Column(String, nullable=True)
    lm = Column(String, nullable=True)
    ntlm = Column(String, nullable=True)
    date = Column(String, nullable=True)
    msv = Column(Boolean, default=False)
    tspkg = Column(Boolean, default=False)
    wdigest = Column(Boolean, default=False)
    kerberos = Column(Boolean, default=False)
    credman = Column(Boolean, default=False)
    location = Column(Integer, default=0) # 0: No se sabe, 1: Local, 2: Dominio, 3: Ambos

    def __init__(self, plain=None, lm=None, ntlm=None, date=None, msv=None, tspkg=None, wdigest=None, kerberos=None, credman=None, location=None):
        self.plain = plain
        self.lm = lm
        self.ntlm = ntlm
        self.date = date
        self.msv = msv
        self.tspkg = tspkg
        self.wdigest = wdigest
        self.kerberos = kerberos
        self.credman = credman
        self.location = location
        db.session.add(self)
        db.session.commit()
    
    def update(self,plain=None,lm=None,ntlm=None,date=None, msv=None, wdigest=None, kerberos=None, credman=None, location=None):
        self.plain = plain if plain else self.plain
        self.lm = lm if lm else self.lm
        self.ntlm = ntlm if ntlm else self.ntlm
        self.date = date if date else self.date
        self.msv = msv if msv else self.msv
        self.wdigest = wdigest if wdigest else self.wdigest
        self.kerberos = kerberos if kerberos else self.kerberos
        self.credman = credman if credman else self.credman
        self.location = location if location else self.location
        db.session.commit()

    def get(ntlm):
        return db.session.query(Credentials).filter_by(ntlm=ntlm).first()
    
    def getById(id):
        return db.session.query(Credentials).filter_by(id=id).first()
    
    def getCredentialsToCrack():
        return db.session.query(Credentials.ntlm).filter(Credentials.plain == None).limit(100).all()
    
    # Estadisticas
    def count_clear_passwords():
        return db.session.query(func.count()).select_from(Credentials).filter(Credentials.plain != None).scalar()
    
    def count_hashed_passwords():
        return db.session.query(func.count()).select_from(Credentials) \
            .filter(Credentials.plain == None) \
            .filter(Credentials.ntlm != None) \
            .scalar()
    
    # Query datos tabla de credenciales
    def get_all():
        # return db.session.query(Credentials).all()

        subquery_count_domainuser = db.session.query(
            CredsDomainUsers.cred_id,
            func.count().label('ntlm_count')) \
                .filter(CredsDomainUsers.cred_id == Credentials.id) \
                .filter_by(historical=0) \
                .group_by(CredsDomainUsers.cred_id) \
                .subquery()

        subquery_count_localuser = db.session.query(
            CredsLocalUsers.cred_id,
            func.count().label('ntlm_count')) \
                .filter(CredsLocalUsers.cred_id == Credentials.id) \
                .group_by(CredsLocalUsers.cred_id) \
                .subquery()

        query = db.session.query(
            Credentials,
            func.coalesce(subquery_count_domainuser.c.ntlm_count, 0),
            func.coalesce(subquery_count_localuser.c.ntlm_count, 0),
        ).outerjoin(
            subquery_count_domainuser, Credentials.id == subquery_count_domainuser.c.cred_id
        ).outerjoin(
            subquery_count_localuser, Credentials.id == subquery_count_localuser.c.cred_id
        ).all()
    
        return query
    
    def getHeaders():
        return Credentials.__table__.columns.keys()
    

    def __repr__(self):
        return f'Credentials({self.plain}, {self.ntlm})'

    def __str__(self):
        return self
# ---------fin class Credentials----------------

# Class DomainUsers
class DomainUsers(db.Base):
    __tablename__ = 'domainusers'

    id = Column(Integer, primary_key=True)
    user = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    sid = Column(String, nullable=True)
    logon_server = Column(String, nullable=True)
    logon_time = Column(String, nullable=True)
    date = Column(String, nullable=True)
    owned = Column(Boolean, default=False)

    def __init__(self, user=None, domain=None, sid=None, logon_server=None, logon_time=None, date=None, owned=False):
        self.user = user
        self.domain = domain
        self.sid = sid
        self.logon_server = logon_server
        self.logon_time = logon_time
        self.date = date
        self.owned = owned

    def update(self,user=None,domain=None,sid=None,logon_server=None,logon_time=None,date=None,owned=None):
        self.user = user if user else self.user
        self.domain = domain if domain else self.domain
        self.sid = sid if sid else self.sid
        self.logon_server = logon_server if logon_server else self.logon_server
        self.logon_time = logon_time if logon_time else self.logon_time
        self.date = date if date else self.date
        self.owned = owned if owned is not None else self.owned
        db.session.commit()
    
    # Devuelve la info de un usuario de dominio
    def get_all():
        # Return data but instead machine_id return machine hostname
        # results=db.session.query(DomainUsers, Credentials.plain).all()
        results = db.session.query(DomainUsers, Credentials).\
        join(CredsDomainUsers, DomainUsers.id == CredsDomainUsers.domainuser_id).\
        join(Credentials, CredsDomainUsers.cred_id == Credentials.id).\
        filter(CredsDomainUsers.historical == 0).\
        all()
        resultados=[]
        # for i in results:
        #     _=[i[0],"Empty"]
        #     if i[1] != None:
        #         # new_row = i._replace(column_name_to_delete=i[2], i[1]=new_value)
        #         _[1] = "Clear text"
        #     elif i[2] != None:
        #         _[1] = "Hashed"
        #     resultados.append(_)
            
        return results
    

    def get(user, domain):
        return db.session.query(DomainUsers).filter_by(user=user, domain=domain).first()
    
    def getWithCredentials(user, domain):
        return db.session.query(DomainUsers, Credentials).join(CredsDomainUsers, DomainUsers.id == CredsDomainUsers.domainuser_id).\
        join(Credentials, CredsDomainUsers.cred_id == Credentials.id).\
        filter(CredsDomainUsers.historical == 0, DomainUsers.user == user, DomainUsers.domain == domain).first()
    
    def getInsensitive(user, domain):
        return db.session.query(DomainUsers).filter(DomainUsers.user.ilike(user), DomainUsers.domain.ilike(domain)).first()

    def getById(id):
        return db.session.query(DomainUsers).filter_by(id=id).first()
    
    def getByDomain(domain):
        return db.session.query(DomainUsers).filter_by(domain=domain).all()
    
    def get_data(id):
        data=[]
        data.append(DomainUsers.getById(id))
        data.append(CredsDomainUsers.getByUser_actual(id))
        data.append(CredsDomainUsers.getByUser_historical(id))
        data.append(Tickets.getByUserId(id))
        return data

    def count():
        return db.session.query(func.count()).select_from(DomainUsers).scalar()
    
    def get_owned():
        return db.session.query(DomainUsers) \
            .filter(DomainUsers.owned == True).all()

    def get_domains():
        return db.session.query(DomainUsers.domain).distinct(DomainUsers.domain).all()

    def get_usernames():
        return db.session.query(DomainUsers.user).all()
    
    def get_username_with_domain():
        return db.session.query(DomainUsers.user, DomainUsers.domain).all()
    
    def count_owned():
        return db.session.query(func.count()).select_from(DomainUsers) \
            .filter(DomainUsers.owned == True) \
            .scalar()

    
    def __repr__(self):
        return f'DomainUsers({self.user}, {self.domain})'

    def __str__(self):
        return self.user
# ---------fin class DomainUsers----------------

# Class CredsDomainUsers
class CredsDomainUsers(db.Base):
    __tablename__ = 'credsdomainusers'

    cred_id = Column(Integer, ForeignKey(Credentials.id), primary_key=True)
    domainuser_id = Column(Integer, ForeignKey(DomainUsers.id), primary_key=True)
    date = Column(String, nullable=True)
    historical = Column(Boolean, default=False)

    def __init__(self, cred_id=None, domainuser_id=None, date=None, historical=False):
        self.cred_id = cred_id
        self.domainuser_id = domainuser_id

        self.date = date
        self.historical = historical

    def get(domainuser_id, cred_id):
        return db.session.query(CredsDomainUsers).filter_by(domainuser_id=domainuser_id, cred_id=cred_id).first()
    
    # Devuelve todas las credenciales de un usuario
    def getByUser_actual(_id):
        query= db.session.query(Credentials)
        query = query.join(CredsDomainUsers, Credentials.id == CredsDomainUsers.cred_id)
        query = query.filter(CredsDomainUsers.domainuser_id == _id).filter(CredsDomainUsers.historical == 0).all()
        return query
    
    def getByUser_historical(_id):
        query= db.session.query(Credentials)
        query = query.join(CredsDomainUsers, Credentials.id == CredsDomainUsers.cred_id)
        query = query.filter(CredsDomainUsers.domainuser_id == _id).filter(CredsDomainUsers.historical == 1).all()
        return query


    
    def get_users_by_cred_id(cred_id):
        results = db.session.query(DomainUsers).\
            join(CredsDomainUsers, DomainUsers.id == CredsDomainUsers.domainuser_id).\
            filter(CredsDomainUsers.historical == 0).\
            filter(CredsDomainUsers.cred_id == cred_id).\
            all()

        return results



    
    def __repr__(self):
        return f'CredsDomainUsers({self.cred_id}, {self.domainuser_id})'

    def __str__(self):
        return self.cred_id
# ---------fin class CredsDomainUsers----------------

# Class Machines
class Machines(db.Base):
    __tablename__ = 'machines'

    id = Column(Integer, primary_key=True)
    hostname = Column(String, nullable=True)
    domain = Column(String, nullable=True)
    sid = Column(String, nullable=True)
    sam_key = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    ntlm = Column(String, nullable=True)
    aes128 = Column(String, nullable=True)
    aes256 = Column(String, nullable=True)
    des = Column(String, nullable=True)
    rc4 = Column(String, nullable=True)
    plain = Column(String, nullable=True)
    date = Column(String, nullable=True)
    owned = Column(Boolean, default=False)

    def __init__(self, hostname=None, domain=None, sid=None, sam_key=None, ip=None, ntlm=None, aes128=None, aes256=None, des=None, rc4=None, plain=None, date=None):
        self.hostname = hostname
        self.domain = domain
        self.sid = sid
        self.sam_key = sam_key
        self.ip = ip
        self.ntlm = ntlm
        self.aes128 = aes128
        self.aes256 = aes256
        self.des = des
        self.rc4 = rc4
        self.plain = plain
        self.date = date

    def update(self,hostname=None,domain=None,sid=None,sam_key=None,ip=None,ntlm=None,aes128=None,aes256=None,des=None,rc4=None,plain=None,date=None):
        self.hostname = hostname if hostname else self.hostname
        self.domain = domain if domain else self.domain
        self.sid = sid if sid else self.sid
        self.sam_key = sam_key if sam_key else self.sam_key
        self.ip = ip if ip else self.ip
        self.ntlm = ntlm if ntlm else self.ntlm
        self.aes128 = aes128 if aes128 else self.aes128
        self.aes256 = aes256 if aes256 else self.aes256
        self.des = des if des else self.des
        self.rc4 = rc4 if rc4 else self.rc4
        self.plain = plain if plain else self.plain
        self.date = date if date else self.date
        db.session.commit()

    def get(hostname):
        return db.session.query(Machines).filter_by(hostname=hostname).first()
    
    # Devuelve la info de una maquina y sus usuarios locales
    def getById(id):
        data=[]
        query=db.session.query(Machines).filter_by(id=id).first()
        data.append(query)
        data.append(LocalUsers.getUsersById(id))

        return data


    def getByDomain(domain):
        return db.session.query(Machines).filter_by(domain=domain).all()
    
    def get_all():
        a= db.session.query(Machines).all()
        return a  # Movido fuera del bucle for
    
    def count():
        return db.session.query(func.count()).select_from(Machines).scalar()
    
    def count_owned():
        return db.session.query(func.count()).select_from(Machines) \
            .filter(Machines.owned == True) \
            .scalar()

    def getHeaders():
        return Machines.__table__.columns.keys()
    
    def __repr__(self):
        return f'Machines({self.hostname, self.domain})'

    def __str__(self):
        return self.hostname
# ---------fin class Machines----------------

# Class LocalUsers
class LocalUsers(db.Base):
    __tablename__ = 'localusers'

    id = Column(Integer, primary_key=True)
    user = Column(String, nullable=True)
    sid = Column(String, nullable=True)
    logon_server = Column(String, nullable=True)
    logon_time = Column(String, nullable=True)
    enabled = Column(Boolean, default=False)
    machine_id = Column(Integer, ForeignKey(Machines.id))
    date = Column(String, nullable=True)

    def __init__(self, user=None, sid=None, logon_server=None, logon_time=None, enabled=None, machine_id=None, date=None):
        self.user = user
        self.sid = sid
        self.logon_server = logon_server
        self.logon_time = logon_time
        self.enabled = enabled
        self.machine_id = machine_id
        self.date = date     

    def update(self,user=None,sid=None,logon_server=None,logon_time=None,enabled=None,machine_id=None,date=None):
        self.user = user if user else self.user
        self.sid = sid if sid else self.sid
        self.logon_server = logon_server if logon_server else self.logon_server
        self.logon_time = logon_time if logon_time else self.logon_time
        self.enabled = enabled if enabled else self.enabled
        self.machine_id = machine_id if machine_id else self.machine_id
        self.date = date if date else self.date
        db.session.commit()

    def get(user, machine_id):
        return db.session.query(LocalUsers).filter_by(user=user, machine_id=machine_id).first()
    
    def getById(_id):
        data=[]
        #INFO BASICA
        query= db.session.query(LocalUsers.user, LocalUsers.sid, LocalUsers.logon_server, LocalUsers.logon_time, Machines.hostname)
        query = query.join(Machines, Machines.id == LocalUsers.machine_id)
        query = query.filter(LocalUsers.id == _id).first()
        data.append(query)
        #INFO CREDENCIALES
        query2= db.session.query(Credentials.plain, Credentials.ntlm, Credentials.id)
        query2 = query2.select_from(LocalUsers).join(CredsLocalUsers, LocalUsers.id == CredsLocalUsers.localuser_id)
        query2 = query2.join(Credentials, Credentials.id == CredsLocalUsers.cred_id)
        query2 = query2.filter(LocalUsers.id == _id).all()
        data.append(query2)
        #INFO MAQUINA
        query3= db.session.query(Machines)
        query3 = query3.select_from(LocalUsers).join(Machines, Machines.id == LocalUsers.machine_id)
        query3 = query3.filter(LocalUsers.id == _id).first()
        data.append(query3)

        return data

    # Devuelve la info de un usuario local
    def getById2(_id):
        data=[]
        #INFO BASICA
        query= db.session.query(LocalUsers)
        query = query.join(Machines, Machines.id == LocalUsers.machine_id)
        query = query.filter(LocalUsers.id == _id).first()
        data.append(query)
        #INFO CREDENCIALES
        query2= db.session.query(Credentials.plain, Credentials.ntlm)
        query2 = query2.select_from(LocalUsers).join(CredsLocalUsers, LocalUsers.id == CredsLocalUsers.localuser_id)
        query2 = query2.join(Credentials, Credentials.id == CredsLocalUsers.cred_id)
        query2 = query2.filter(LocalUsers.id == _id).all()
        data.append(query2)
        #INFO MAQUINA
        query3= db.session.query(Machines.hostname, Machines.domain, Machines.sid, Machines.sam_key, Machines.ntlm, Machines.aes128, Machines.aes256, Machines.des)
        query3 = query3.select_from(LocalUsers).join(Machines, Machines.id == LocalUsers.machine_id)
        query3 = query3.filter(LocalUsers.id == _id).first()
        data.append(query3)


        return data
    def getUsersById(_id):
        query=db.session.query(LocalUsers.user, LocalUsers.sid, LocalUsers.id).filter_by(machine_id=_id).all()
        return query
    
    # Devuelve todos los usuarios locales de una maquina
    def getUsersById2(_id):
        query=db.session.query(LocalUsers).filter_by(machine_id=_id).all()
        return query
    
    def get_all():
        # Return data but instead machine_id return machine hostname
        # results=db.session.query(DomainUsers, Credentials.plain).all()
        results = db.session.query(LocalUsers, Machines, Credentials).\
        join(Machines, Machines.id == LocalUsers.machine_id).\
        join(CredsLocalUsers, LocalUsers.id == CredsLocalUsers.localuser_id).\
        join(Credentials, CredsLocalUsers.cred_id == Credentials.id).\
        filter(CredsLocalUsers.historical == 0).\
        all()

            
        return results
    # Devuelve la ionformación de todos los usuarios con el nombre de la maquina

    def count():
        return db.session.query(func.count()).select_from(LocalUsers).scalar()
    
    
        
    def __repr__(self):
        return f'LocalUsers({self.user})'

    def __str__(self):
        return self.user
# ---------fin class LocalUsers----------------

# Class CredsLocalUsers
class CredsLocalUsers(db.Base):
    __tablename__ = 'credslocalusers'

    cred_id = Column(Integer, ForeignKey(Credentials.id), primary_key=True)
    localuser_id = Column(Integer, ForeignKey(LocalUsers.id), primary_key=True)
    date = Column(String, nullable=True)
    historical = Column(Boolean, default=False)

    def __init__(self, cred_id=None, localuser_id=None, date=None, historical=False):
        self.cred_id = cred_id
        self.localuser_id = localuser_id
        self.date = date
        self.historical = historical

    def get(cred_id, localuser_id):
        return db.session.query(CredsLocalUsers).filter_by(cred_id=cred_id, localuser_id=localuser_id).first()
    
    def getCredsByUserId(localuser_id):
        return db.session.query(CredsLocalUsers.cred_id,Credentials.plain,Credentials.ntlm).filter_by(localuser_id=localuser_id, cred_id=Credentials.id).join(Credentials).all()

    def get_users_by_cred_id(cred_id):
        results = db.session.query(LocalUsers, Machines).\
            join(CredsLocalUsers, LocalUsers.id == CredsLocalUsers.localuser_id).\
            join(Machines, Machines.id == LocalUsers.machine_id).\
            filter(CredsLocalUsers.historical == 0).\
            filter(CredsLocalUsers.cred_id == cred_id).\
            all()
        return results

    def __repr__(self):
        return f'CredsLocalUsers({self.cred_id}, {self.localuser_id})'

    def __str__(self):
        return self.cred_id
# ---------fin class CredsLocalUsers----------------

# Class Tickets
class Tickets(db.Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    domainuser_id = Column(Integer, ForeignKey(DomainUsers.id))
    ticket_type = Column(String, nullable=True)
    ticket_name = Column(String, nullable=True)
    ticket_data = Column(String, nullable=True)
    service_name = Column(String, nullable=True)
    target_name = Column(String, nullable=True)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    renew_time = Column(String, nullable=True)
    date = Column(String, nullable=True)

    def __init__(self, service=None, domainuser_id=None, ticket_type=None, ticket_name=None, ticket_data=None, service_name=None, target_name=None, start_time=None, end_time=None, renew_time=None, date=None):
        self.service = service
        self.domainuser_id = domainuser_id
        self.ticket_type = ticket_type
        self.ticket_name = ticket_name
        self.ticket_data = ticket_data
        self.service_name = service_name
        self.target_name = target_name
        self.start_time = start_time
        self.end_time = end_time
        self.renew_time = renew_time
        self.date = date 

    def update(self, service=None, domainuser_id=None, ticket_type=None, ticket_name=None, ticket_data=None, service_name=None, target_name=None, start_time=None, end_time=None, renew_time=None, date=None):
        self.service = service if service else self.service
        self.domainuser_id = domainuser_id if domainuser_id else self.domainuser_id
        self.ticket_type = ticket_type if ticket_type else self.ticket_type
        self.ticket_name = ticket_name if ticket_name else self.ticket_name
        self.ticket_data = ticket_data if ticket_data else self.ticket_data
        self.service_name = service_name if service_name else self.service_name
        self.target_name = target_name if target_name else self.target_name
        self.start_time = start_time if start_time else self.start_time
        self.end_time = end_time if end_time else self.end_time
        self.renew_time = renew_time if renew_time else self.renew_time
        self.date = date if date else self.date

    def get(ticket_name, user_id):
        return db.session.query(Tickets).filter_by(ticket_name=ticket_name, domainuser_id=user_id).first()
    
    def get_by_name(ticket_name):
        return db.session.query(Tickets).filter_by(ticket_name=ticket_name).first()
    
    # Devuelve la info de un ticket
    def getById(_id):
        return db.session.query(Tickets).filter_by(id=_id).first()
    
    # Devuelve tickets de un usuario
    def getByUserId(_id):
        return db.session.query(Tickets).filter_by(domainuser_id=_id).all()

    def get_all():
        # Return data but instead machine_id return machine hostname
        results=db.session.query(Tickets, DomainUsers).join(DomainUsers).all()
        
        # return db.session.query(LocalUsers).all()
        return results

    def count():
        return db.session.query(func.count()).select_from(Tickets).scalar()

    def __repr__(self):
        return f'Tickets({self.ticket_type}, {self.ticket_name})'

    def __str__(self):
        return self.service
# ---------fin class Tickets----------------

