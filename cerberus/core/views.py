import functools
import json
from flask import (
    flash, g, redirect, render_template, request, session, url_for, make_response, current_app
)
from cerberus.auth import check_conn, login_required
from cerberus.utils import checkneo4j,neo4jGraphDashBoard
from cerberus.db import get_db, close_db

from . import core
from cerberus import projects

# -----------------------------------------
#   Coger de la carpeta de proyectos los
#         los que existan
# -----------------------------------------

# Check project en otras vistas
def check_project(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        p=request.cookies.get('project')
        if p not in projects:
            return render_template('core/empty.html',
                                   projects=projects)
        return view(**kwargs)

    return wrapped_view

# -------------------------------------------------------------------------------------------
# Check conexion de neo4j
def check_neo4j(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user["neo4j_user"] is None or g.user["neo4j_password"] is None or g.user["neo4j_url"] is None:
            flash("Neo4j connection not set. Please, go to settings and set it.", "warning")
            return redirect(request.referrer)
        from neo4j import GraphDatabase
        # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
        try:
            with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
                driver.verify_connectivity() 
        except Exception as e:
            exception_type = type(e)
            if exception_type.__name__ == "ServiceUnavailable":
                flash('Error in neo4j database connection (ServiceUnavailable)', 'danger')
            elif exception_type.__name__ == "AuthError":
                flash('Error in neo4j database connection (AuthError)', 'danger')
                return redirect(url_for('core.dashboard'))

            return redirect(request.referrer)
        
        return view(**kwargs)

    return wrapped_view

# -------------------------------------------------------------------------------------------
# DASHBOARD
@core.route('/', methods=['GET'])
@login_required
@check_project
def dashboard():
    data=dict()
    # Inicializamos la conexión con la DB
    from cerberus import db2 as db
    db.db_link(request.cookies.get('project'))
    db.db_connect()

    from cerberus import models as m
    # Registros de la tabla de DomainUsers
    data['domainusers']=m.DomainUsers.count()

    # Registros de la tabla de DomainUsers con el campo owned a 1
    data['owned_domainusers']=m.DomainUsers.count_owned()
 
    # Registros de la tabla de LocalUsers
    data['localusers']=m.LocalUsers.count()

    # Registros de la tabla de Credentials con contraseñas en texto claro
    data['cleartextpass']=m.Credentials.count_clear_passwords()

    # Registros de la tabla de Credentials con contraseñas solo hasheadas
    data['hashpass']=m.Credentials.count_hashed_passwords()

    # Registros de la tabla de Tickets
    data['tickets']=m.Tickets.count()

    # Registros de la tabala de maquinas
    data['machines']=m.Machines.count()


    # Registros de Neo4j
    if checkneo4j():
        resultNeo4j=neo4jGraphDashBoard()
        if(resultNeo4j[0]=="success"):
            data.update(resultNeo4j[1])
            data.update({'resultNeo4j':1})
        else:
            data.update({'resultNeo4j':-1})
    else:
        data.update({'resultNeo4j':-1})

    db.db_disconnect()
    return render_template('core/dashboard.html',
                           projects=projects,
                           title='Dashboard',
                           data=data)

# IMPORT DATA
@core.route('/import', methods=['GET'])
@login_required
@check_project
def import_data():
    return render_template('core/import.html',
                           projects=projects,
                           title='Import data',
                           data_types=[
                               "logonpasswords",
                               "lsadump",
                               "tickets",
                               "secretsdump"
                           ],
                           file_types=[
                               ".zip / .json",
                               ".dat"
                           ]
                           )

# Upload data to import
@core.route('/import/upload', methods=['POST'])
@login_required
@check_project
def import_upload_data():
    from cerberus import utils
    from .logonpasswords import parse_logonpasswords, insert_longonpasswords
    from .lsadump import parse_lsadump, insert_lsadump
    from .tickets import parse_tickets, insert_tickets
    from .secretsdump import parse_secretsdump


    # Importado de bibliotecas
    from io import BytesIO

    # Parámetros del formulario
    dataType = request.form["dataType"]
    # dataFile = request.files.getlist('dataFileModules')
    dataFile = request.files["dataFileModules"]

    # Comprobamos que el usuario haya introducido un fichero
    if not dataFile:
        flash("Not file provided", "danger")
        return redirect(url_for("core.import_data"))
    
    # Inicializamos la conexión con la DB
    from cerberus import db2 as db
    db.db_link(request.cookies.get('project'))
    db.db_connect()
    
    # Importamos la información del fichero
    try:
        # Guarda los datos del archivo en un flujo de bytes en memoria
        stream = BytesIO(dataFile.read())

        # Lee los datos directamente desde el flujo
        data = utils.readFile2(stream, dataType)

        if dataType=='logonpasswords':
            d=parse_logonpasswords(data)
            for i in d:
                insert_longonpasswords(i, db.session)
        elif dataType=='lsadump':
            d=parse_lsadump(data)
            insert_lsadump(d, db.session)
        elif dataType=='tickets':

            d=parse_tickets(data)

            insert_tickets(d, db.session)

        elif dataType=='secretsdump':
            parse_secretsdump(data, db.session)
                # insert_secretsdump(d)

        db.db_disconnect()

        flash(u'File successfully uploaded', 'success')
        return redirect(url_for('core.import_data'))
    except Exception as e:
        print(e)
        flash(u'Error uploading file', 'danger')
        return redirect(url_for('core.import_data'))

@core.route('/import/tickets', methods=['POST'])
@login_required
@check_project
def uploads_tickets_file():
    import os
    from cerberus.core.tickets import upload_ticket
    from cerberus import db2 as db
    from werkzeug.utils import secure_filename

    def allowed_file(filename):
        allowed_extensions = {'ccache', 'kirbi'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    try:
        db.db_link(request.cookies.get('project'))
        db.db_connect()

        tmpfiles=[]

        files = request.files.getlist('dataFileTickets')

        if not os.path.isdir(f"{current_app.root_path}/static/uploads"):
            os.mkdir(f"{current_app.root_path}/static/uploads")

        if not os.path.isdir(f"{current_app.root_path}/static/uploads/tickets"):    
            os.mkdir(f"{current_app.root_path}/static/uploads/tickets")


        #if files are empty then raise error
        if not files[0].filename:
            flash(u'No files selected', 'warning')
            return redirect(url_for('core.import_data'))
        for file in files:
            filename = secure_filename(file.filename)
            if(allowed_file(filename)):
                file.save(f"{current_app.root_path}/static/uploads/tickets/{file.filename}")
                #Ruta del ticket, nombre del archivo y session en la base de datos
                upload_ticket(f"{current_app.root_path}/static/uploads/tickets/", file.filename ,db.session)
                os.remove(f"{current_app.root_path}/static/uploads/tickets/{file.filename}")
            else:
                flash(u'Something went wrong: Wrong Extension only ccache and kirbi: ' + filename, 'danger')
                print(f"\n\nERROR {filename}\n\n")
                return redirect(url_for('core.import_data'))
        
        db.db_disconnect()
        flash(u'Tickets successfully uploaded', 'success')
        return redirect(url_for('core.import_data'))
    except Exception as e:
        print(f"\n\n{e}\n\n")
        flash(u'Something went wrong', 'danger')
        return redirect(url_for('core.import_data'))

@core.route('/import/nmapxml', methods=['POST'])
@login_required
@check_project
@check_neo4j
def uploads_nmapxml_file():
    import os
    from cerberus.core.nmapxml import parseXML,uploadDataNmap
    from cerberus import db2 as db
    from werkzeug.utils import secure_filename
    def allowed_file(filename):
        allowed_extensions = {'xml'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


    try:
        db.db_link(request.cookies.get('project'))
        db.db_connect()

    
        files = request.files.getlist('dataFileNmaps')

        #if files are empty then raise error
        if not files[0].filename:
            flash(u'No files selected', 'warning')
            return redirect(url_for('core.import_data'))
        for file in files:
            
            filename = secure_filename(file.filename)
            if(allowed_file(filename)):
                file.save(f"{current_app.root_path}/static/.tmp/{file.filename}")
                data = parseXML(f"{current_app.root_path}/static/.tmp/{file.filename}")
                uploadDataNmap(data,db.session,file.filename)
                os.remove(f"{current_app.root_path}/static/.tmp/{file.filename}")
            else:
                flash(u'Something went wrong: Wrong Extension only XML:' + filename, 'danger')
                return redirect(url_for('core.import_data'))

        db.db_disconnect()
        flash(u'Nmap successfully uploaded', 'success')
        return redirect(url_for('core.import_data'))
    except Exception as e:
        print(e)
        flash(u'Something went wrong: ' + str(e), 'danger')
        return redirect(url_for('core.import_data'))



@core.route('/import/graph', methods=['POST'])
@login_required
@check_project
@check_neo4j
def import_ad_file():
    from cerberus import utils
    import asyncio
    from cerberus.static.external_modules.importer import parse_file, add_constraints
    from cerberus.static.external_modules import database
    from neo4j.exceptions import ClientError
    from io import BytesIO
    import subprocess
    from cerberus.static.external_modules.adexplorersnapshot.importDatFile import importDatFile
    from werkzeug.utils import secure_filename

    def allowed_file(filename):
        allowed_extensions = {'zip', 'json', 'dat'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    async def parse_files(files):
        driver = database.init_driver(g.user["neo4j_url"], g.user["neo4j_user"], g.user["neo4j_password"])
        try:
            try:
                async with driver.session() as session:
                    print("Adding constraints to the neo4j database")
                    await session.write_transaction(add_constraints)

            except ClientError:
                pass

            print(f"Parsing {len(files)} files")

            for filename in files:
                try:
                    await parse_file(filename, driver)
                except Exception as e:
                    print(f'Error parsing file: {filename.split("/")[-1]}')
                    flash(f'Error parsing file: {filename.split("/")[-1]}', 'danger')
            print("Done")

        finally:
            await driver.close()

    # Get files
    files = request.files.getlist('dataFileDump')
    fileType = request.form["fileType"]
    files_names=[]

    # Check if files are empty
    if not files[0].filename:
        flash(u'No files selected', 'warning')
        return redirect(url_for('core.import_data'))
    
    if ".dat" in fileType:
        filename = secure_filename(files[0].filename)
        if(allowed_file(filename)):
            upload_path = f"cerberus/static/.tmp/{filename}"
            stream = BytesIO(files[0].read())
            utils.saveFile(stream, upload_path)
            # Parseamos el .dat a formato interpretable
            zip_path = f"cerberus/static/.tmp/{files[0].filename.split('.')[0]}.zip"
            importDatFile(upload_path, zip_path)
            # Importamos el zip generado
            try:
                asyncio.run(parse_files([zip_path]))
            except Exception as e:
                try:
                    subprocess.Popen(['rm', upload_path])
                    subprocess.Popen(['rm', zip_path])
                except:
                    pass
                print(e)
                flash(u'Error loading file', 'danger')
                return redirect(url_for('core.import_data'))
            try:
                subprocess.Popen(['rm', upload_path])
                subprocess.Popen(['rm', zip_path])
            except:
                pass
        else:     
            flash(u'Something went wrong: Wrong Extension only .dat:' + filename, 'danger')
            return redirect(url_for('core.import_data'))
    else:
        # Save files
        for i in files:
            filename = secure_filename(i.filename)
            if(allowed_file(filename)):
                upload_path = f"cerberus/static/.tmp/{filename}"
                stream = BytesIO(i.read())
                utils.saveFile(stream, upload_path)
                files_names.append(upload_path)
            else:
                flash(u'Something went wrong: Wrong Extension only json or zip:' + filename, 'danger')
                return redirect(url_for('core.import_data'))

        # Parse files
        #try:
        asyncio.run(parse_files(files_names))
        #except Exception as e:
         #   print(e)
         #   flash(u'Error loading file', 'danger')
          #  return redirect(url_for('core.import_data'))
        for i in files_names:
            try:
                subprocess.Popen(['rm', i])
            except:
                pass

    flash(u'File parsing completed', 'success')
    return redirect(url_for("core.import_data"))



@core.route('/import/hashcat', methods=['POST'])
@login_required
@check_project
def hashcat_page():
    from cerberus import db2 as db
    from cerberus.utils import readFileHashcat
    db.db_link(request.cookies.get('project'))
    db.db_connect()
    from cerberus import models as m
    # file = request.files['dataFile']
    files = request.files.getlist('dataFile')

    if not files[0]:
        flash(u'No file provided', 'warning')
        # cerrar la conexión a la bbdd
        db.db_disconnect()
        return redirect(request.referrer)
    
    from io import BytesIO
    try:
        # Guarda los datos del archivo en un flujo de bytes en memoria
        stream = BytesIO(files[0].read())

        # Lee los datos directamente desde el flujo
        data = readFileHashcat(stream)
        for i in data:
            cred=m.Credentials.get(i[0])
            if cred is not None:
                cred.update(plain=i[1])
        
        flash(u'File successfully uploaded', 'success')
        # cerrar la conexión a la bbdd
        db.db_disconnect()
        return redirect(request.referrer)
    except:
        flash(u'Error reading file', 'danger')
        # cerrar la conexión a la bbdd
        db.db_disconnect()
        return redirect(request.referrer)
    

@core.route('/import/machines', methods=['POST'])
@login_required
@check_project
def machines_dnsresolver():
    from cerberus import db2 as db
    from cerberus.utils import readFileDNSResolver
    db.db_link(request.cookies.get('project'))
    db.db_connect()
    from cerberus import models as m

    files = request.files.getlist('dataFileDNSrsv')

    if not files[0]:
        flash(u'No file provided', 'warning')
        # cerrar la conexión a la bbdd
        db.db_disconnect()
        flash(u'No files selected', 'warning')
        return redirect(request.referrer)
    
    from io import BytesIO

    try:
        # Guarda los datos del archivo en un flujo de bytes en memoria
        stream = BytesIO(files[0].read())

        # Lee los datos directamente desde el flujo
        data = readFileDNSResolver(stream)
        # print(data)
        for i in data:
            hostname, dominio = i[0].split('.', 1)
            # hostname=i[0].split(".")[0].lower()+"$"
            # domain=i[0].split(".")[1].lower()
            hostname=hostname.lower()+"$"
            dominio=dominio.lower()
            print(hostname)
            print(dominio)
            ip = i[1] if i[1] != "Not resolved" else None 

            machine=m.Machines.get(hostname)
            if machine is not None:
                machine.update(ip=ip) if ip is not None else None
                machine.update(domain=dominio) if dominio is not None else None
            else:
                new_machine=m.Machines(hostname=hostname, ip=ip, domain=dominio)
                db.session.add(new_machine)
                db.session.commit()

        
        flash(u'File successfully uploaded', 'success')
        # cerrar la conexión a la bbdd
        db.db_disconnect()
        return redirect(request.referrer)
    except:
        flash(u'Error reading file', 'danger')
        # cerrar la conexión a la bbdd
        db.db_disconnect()
        return redirect(request.referrer)


# EXPORTAR CONTRASEÑAS PARA CRACKEAR EN HASHCAT
@core.route('/export/credentials/hashcat', methods=['GET'])
@login_required
@check_project
def export_credentials_to_hashcat():

    from cerberus import db2 as db
    from functools import reduce
    from flask import send_file
    import io

    db.db_link(request.cookies.get('project'))
    db.db_connect()
    from cerberus import models as m

    credsToCrack = m.Credentials.getCredentialsToCrack()
    credsList = reduce(lambda x,y: f"{x}\n{y}", list(map(lambda x: x[0], credsToCrack)))
    credsList += "\n"

    credsFile = io.BytesIO(credsList.encode("utf-8"))
    
    return send_file(
        credsFile,
        as_attachment=True,
        download_name="hashes.txt",
        mimetype="text/plain"
    )

    """ return redirect(request.referrer) """

# TABLAS
@core.route('/info', methods=['GET'])
@login_required
@check_project
def table_data():
    tables=["credentials", "machines", "domainusers", "localusers", "tickets", "domain"]

    tabla=request.args.get('t')
    id=request.args.get('id')
    
    if tabla is None or tabla not in tables:
        flash("Table not found", "danger")
        return redirect(url_for("core.dashboard"))
    
    from cerberus import db2 as db
    db.db_link(request.cookies.get('project'))
    db.db_connect()
    # Operaciones de BBDD
    from cerberus import models as m
    if id is not None:
        if tabla == "localusers":
            data=m.LocalUsers.getById(id)
            template=f'localusers.html'
        elif tabla == "machines":
            data=m.Machines.getById(id)
            template=f'machines.html'
        elif tabla == "domainusers":
            data=m.DomainUsers.get_data(id)
            template=f'domainusers.html'
        elif tabla == "domain":
            data=[]
            data.append(m.DomainUsers.getByDomain(id))
            data.append(m.Machines.getByDomain(id))
            template=f'domain.html'
        elif tabla == "credentials":
            data=[]
            data.append(m.Credentials.getById(id))
            data.append(m.CredsDomainUsers.get_users_by_cred_id(id))
            data.append(m.CredsLocalUsers.get_users_by_cred_id(id))
            print(data)
            template=f'credentials.html'
        else:
            pass
        # cerrar la conexión a la bbdd
        db.db_disconnect()
        return render_template(f'core/tables/intermediate/{template}',
                            data=data,
                            projects=projects)
    else:
    

        if tabla=="credentials":
            _=m.Credentials.getHeaders()
            headers=[_[1],_[3],"Domain count","Local count",_[4]]
            rows=m.Credentials.get_all()
            template='core/tables/credentials.html'
            title='Credentials'
        elif tabla=="machines":
            _=m.Machines.getHeaders()
            headers=[_[1],_[2],_[5],_[6],_[8],_[12]]
            rows=m.Machines.get_all()
            template='core/tables/machines.html'
            title='Machines'
        elif tabla=="domainusers":
            headers=["Username","Domain","Credential Type", "Credential", "Date"]
            rows=m.DomainUsers.get_all()
            template='core/tables/domainusers.html'
            title='Domain Users'
        elif tabla=="localusers":
            headers=["Username","Machine","Credential Type", "Credential", "Date"]
            rows=m.LocalUsers.get_all()
            template='core/tables/localusers.html'
            title='Local Users'
        elif tabla=="tickets":
            headers=["Username","Type","Ticket name", "Data", "Start time", "End time", "Renew time"]
            rows=m.Tickets.get_all()
            template='core/tables/tickets.html'
            title='Tickets'
        else:
            db.db_disconnect()
            flash("Table not found", "danger")
            return redirect(url_for("core.dashboard"))
        db.db_disconnect()
    # FIN operaciones de BBDD
    return render_template(template,
                           projects=projects,
                           headers=headers,
                           rows=rows,
                           title=title)

# New credential
@core.route('/info/newcred', methods=['GET', 'POST'])
@login_required
@check_project
def new_cred():
    from cerberus.utils import calculate_ntlm
    from .newcred import insert_new_cred
    from cerberus import db2 as db
    db.db_link(request.cookies.get('project'))
    db.db_connect()

    plain_value = request.form['password']

    if plain_value.strip()=='':
        plain_value=None
        
    if plain_value is not None: # Hay password
        ntlm_crafted=calculate_ntlm(plain_value)

        a=insert_new_cred(ntlm=ntlm_crafted, plain=plain_value, session=db.session)
        flash(a[0],a[1])
        db.db_disconnect()
                                
    else: # No hay password
        flash(u'No value provided', 'warning')
        # cerrar la conexión a la bbdd
        db.db_disconnect()
    return redirect(request.referrer)

@core.route('/info/newtgs', methods=['GET', 'POST'])
@login_required
@check_project
def new_tgs():
    import io
    from .tickets import create_ticket
    from cerberus import db2 as db
    db.db_link(request.cookies.get('project'))
    db.db_connect()

    spn = request.form['spn']
    domain = request.form['domain']
    domain_sid = request.form['domain-sid']
    nthash = request.form['nthash']
    target = request.form['target']

    # Aquí puedes realizar cualquier procesamiento adicional con los datos obtenidos
    a=create_ticket(spn=spn, domain=domain, domain_sid=domain_sid, nthash=nthash, target=target, session=db.session)

    flash(f'Ticket {a[1]} successfully created', 'success')
    return redirect(request.referrer)

@core.route('/info/newtgt', methods=['GET', 'POST'])
@login_required
@check_project
def new_tgt():
    import io
    from .tickets import create_ticket
    from cerberus import db2 as db
    db.db_link(request.cookies.get('project'))
    db.db_connect()

    domain = request.form['domain']
    domain_sid = request.form['domain-sid']
    nthash = request.form['nthash']
    target = request.form['target']
    duration = request.form['duration']

    # Aquí puedes realizar cualquier procesamiento adicional con los datos obtenidos
    a=create_ticket(domain=domain, domain_sid=domain_sid, nthash=nthash, target=target,duration=duration, session=db.session)

    flash(f'Ticket {a[1]} successfully created', 'success')
    return redirect(request.referrer)


# Set Project
@core.route('/projects/set/<project>', methods=['GET'])
@login_required
def set_project(project):
    response = make_response(redirect(request.referrer)) # We can also render new page with render_template
    response.set_cookie('project',project)
    return response

# New Project
@core.route('/projects/new/', methods=['POST'])
@login_required
def new_project():
    project=request.form['project']
    if project in projects:
        flash("Project already exists", "danger")
        return redirect(request.referrer)
    
    # Copiamos el template de la bbdd
    import shutil
    try:
        shutil.copyfile(f"{current_app.instance_path}/template.db", f"{current_app.root_path}/static/projects/{project}.db")
    except Exception as e:
        print(e)
        flash("Error creating project", "danger")
        return redirect(request.referrer)    

    projects.append(project)
    flash("Project successfully created", "success")
    response = make_response(redirect(url_for('core.import_data')))
    response.set_cookie('project',project)
    return response

# Set settings
@core.route('/settings', methods=['POST'])
@login_required
def settings():
    url = request.form['url']
    username = request.form['user']
    password = request.form['password']

    db = get_db()
    if not url: url = None
    if not username: username = None
    if not password: password = None

    db.execute(
        "UPDATE user SET neo4j_url = ?, neo4j_user = ?, neo4j_password = ? WHERE id = ?",
        (url, username, password, g.user['id']),
    )
    db.commit()
    close_db()
    flash("Settings updated", "success")
    return redirect(request.referrer)

#Download file
@core.route('/download_file/<tipo>/<id>', methods=['GET'])
@login_required
@check_project
def download_file(tipo, id):
    # return download_tickets(tipo, id)
    import base64
    import io
    from flask import send_file
    # ------------------cookie + db_connection----------------
    project=request.cookies.get('project')

    # Conectamos a la bbdd
    from cerberus import db2 as db
    db.db_link(project)
    db.db_connect()
    # conn,session=db_connection_multiple(project)

    # ------------------fin cookie + db_connection----------------
    # import db
    from cerberus import models as m
    # from tickets import transform_kirbi_ccache
    from .tickets import transform_kirbi_ccache
    ticket=m.Tickets.getById(id)
    #cerrar la conexión a la bbdd
    db.db_disconnect()
    ticket_name=ticket.ticket_name.rstrip(".kirbi").rstrip(".ccache")
    # Decodificar la cadena base64 a bytes
    if tipo == 'kirbi':
        decoded_data = base64.b64decode(ticket.ticket_data)
        ticket_name=f'{ticket_name}.kirbi'
    elif tipo == 'ccache':
        decoded_data=base64.b64decode(transform_kirbi_ccache(ticket.ticket_data, ticket_name))
        ticket_name=f'{ticket_name}.ccache'
    else:
        pass
    # Crear un objeto BytesIO y escribir los datos decodificados en él
    file_obj = io.BytesIO()
    file_obj.write(decoded_data)
    file_obj.seek(0)

    # Enviar el archivo como una respuesta para su descarga
    return send_file(file_obj, mimetype='application/octet-stream', download_name=f'{ticket_name}', as_attachment=True)

# -------------------------------------------------------------------------------------------
# GRAPH
@core.route('/graph', methods=['GET'])
@login_required
@check_conn
@check_neo4j
def graph():
    return redirect(url_for('core.get_graph', query='kerberoast'))

@core.route("/graph/markowned", methods=['POST'])
@login_required
@check_neo4j
def graph_mark_owned():

    from cerberus.utils import neo4jNodeAsOwned

    # Obtenemos el usuario y dominio a marcar
    nodeIDToMark = request.form["nodeID"]
    ownedStatus = request.form["owned"]

    statusToMark = "true" if ownedStatus == "false" else "false"
    neo4jNodeAsOwned(nodeID=nodeIDToMark, value=statusToMark)
    
    print(f"NODE TO MARK: {nodeIDToMark}")
    print(f"OWNED: {ownedStatus}")

    return redirect(request.referrer)

@core.route("/graph/markhighvalue", methods=['POST'])
@login_required
@check_neo4j
def graph_mark_high_value():

    from cerberus.utils import nodeAsHighValue

    # Obtenemos el usuario y dominio a marcar
    nodeIDToMark = request.form["nodeID"]
    highValueStatus = request.form["highvalue"]

    statusToMark = "true" if highValueStatus == "false" else "false"
    nodeAsHighValue(nodeID=nodeIDToMark, value=statusToMark)
    
    print(f"NODE TO MARK: {nodeIDToMark}")
    print(f"OWNED: {highValueStatus}")
        
    return redirect(request.referrer)

@core.route('/graph/<query>', methods=['GET'])
@login_required
@check_neo4j
def get_graph(query):
    from neo4j import GraphDatabase
    from cerberus.static.external_modules.neo4jvis.model.styled_graph import StyledGraph

    # project=request.cookies.get('project')
    def get_domains():
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:

            cql= "MATCH (n:Domain) RETURN n.name"
            # Execute the CQL query

            with driver.session() as graphDB_Session:
                nodes = graphDB_Session.run(cql)
                domains = []
                for node in nodes:domains.append(node["n.name"])
                return(domains)
            
    def get_nmapFiles():
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:

            cql= "MATCH (f:File) RETURN f.fileName"
            # Execute the CQL query

            with driver.session() as graphDB_Session:
                nodes = graphDB_Session.run(cql)
                nmapFile = []
                for node in nodes:nmapFile.append(node["f.fileName"])
                
                return(nmapFile)
            
    def get_da_group():
        with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:

            cql= "MATCH (g:Group) WHERE g.objectid ENDS WITH '-512' RETURN g.name"
            # Execute the CQL query

            with driver.session() as graphDB_Session:
                nodes = graphDB_Session.run(cql)
                ad_groups = []
                for node in nodes:ad_groups.append(node["g.name"])
                return(ad_groups)
    def draw(query):
            
            from datetime import datetime

            with GraphDatabase.driver(uri=g.user[3], auth=(g.user[4], g.user[5])) as driver:
                graph = StyledGraph(driver)
                graph.options={
                            'nodes':
                            {
                                'color':
                                {
                                    'border': '#FFFFFF',
                                    'background': '#F9A6C1'
                                },
                                'borderWidth': 2,
                                'borderWidthSelected': 2,
                                'shape': 'dot',
                                'fixed':{
                                    'x':'false',
                                    'y':'false',
                                },
                                
                            },
                            'edges': {
                                # 'length':100,
                                'arrows': {
                                    'to': {
                                        'enabled': 'false',
                                        'type':'arrow',
                                        'scaleFactor':0.5
                                        }
                                },
                                'color': {
                                    'inherit': 'false'
                                },
                                'font': {
                                    'size': 14,
                                    'align': 'middle'
                                },
                                'smooth': {
                                    'enabled': 'false',
                                    'type': 'continuous',
                                    'roundness': 0.15
                                },
                                'length': 200,
                                'shadow':'true'
                            },
                            'interaction': {
                                'dragNodes': 'true',
                                'dragView': 'true',
                                'hideEdgesOnDrag': 'false',
                                'hideNodesOnDrag': 'false'
                            },
                            'physics': {
                                'enabled':'true',
                                'repulsion': {
                                    # 'nodeDistance': 2,
                                },
                                'barnesHut': {
                                    # 'gravitationalConstant':-10000,
                                    # 'avoidOverlap':0
                                    
                                },
                                'hierarchicalRepulsion': {
                                    # 'nodeDistance':90,
                                    # 'centralGravity':0.0,
                                    # 'springLength':3500,
                                    # 'springConstant':0,
                                    
                                },
                                'solver': 'barnesHut',
  

                            },
                            'layout': {
                                'improvedLayout': 'true',
                                # 'randomSeed': 420,
                                'hierarchical': {
                                    'enabled': 'false',
                                    'levelSeparation':1000,
                                    'direction': 'RL',
                                    'sortMethod': 'directed',
                                    'parentCentralization':'true',
                                    'blockShifting':'true',
                                    # 'shakeTowards':'default'
                                    # 'nodeSpacing': 500,
                                    # 'treeSpacing': 50,
                                    # 'levelSeparation': 1000,
                                }
                            }


                }
                # input()
                graph.add_from_query(query)

                allNodes = [n.to_dict() for n in graph.nodes.values()]
                nodes = []

                for node in allNodes:
                    # print(node)
                    # input()
                    nodes.append({
                        "id": node["id"],
                        "label": node["label"],
                        "name": node["name"] if "name" in node else node["objectid"],
                        "owned": node["owned"] if "owned" in node else False,
                        "highvalue": node["highvalue"] if "highvalue" in node else False,
                    })

                # Ordenamos la información y la detallamos
                detailStructure = {
                    "nodeProperties": {
                        "display": "Node properties",
                        "elements": [
                            {
                                "name": "displayname",
                                "display": "Display name",
                                "isEpoch": False
                            },
                            {
                                "name": "objectid",
                                "display": "Object ID",
                                "isEpoch": False
                            },
                            {
                                "name": "email",
                                "display": "Email",
                                "isEpoch": False
                            },
                            {
                                "name": "description",
                                "display": "Description",
                                "isEpoch": False
                            },
                            {
                                "name": "pwdlastset",
                                "display": "Password last changed",
                                "isEpoch": True
                            },
                            {
                                "name": "lastlogon",
                                "display": "Last logon",
                                "isEpoch": True
                            },
                            {
                                "name": "admincount",
                                "display": "AdminCount",
                                "isEpoch": False
                            },
                            {
                                "name": "enabled",
                                "display": "Enabled",
                                "isEpoch": False
                            },
                            {
                                "name": "pwdneverexpires",
                                "display": "Password never expires",
                                "isEpoch": False
                            },
                            {
                                "name": "serviceprincipalnames",
                                "display": "Service principal names",
                                "isEpoch": False
                            }
                        ]
                    },
                    "extraProperties": {
                        "display": "Extra properties",
                        "elements": [
                            {
                                "name": "distinguishedname",
                                "display": "Distinguished name",
                                "isEpoch": False
                            },
                            {
                                "name": "domain",
                                "display": "Domain",
                                "isEpoch": False
                            },
                            {
                                "name": "domainsid",
                                "display": "Domain SID",
                                "isEpoch": False
                            },
                            {
                                "name": "passwordnotreqd",
                                "display": "Password not required",
                                "isEpoch": False
                            },
                            {
                                "name": "samaccountname",
                                "display": "SAM account name",
                                "isEpoch": False
                            },
                            {
                                "name": "source",
                                "display": "Source",
                                "isEpoch": False
                            },
                            {
                                "name": "trustedoauth",
                                "display": "Trusted OAuth",
                                "isEpoch": False
                            },
                            {
                                "name": "unconstraineddelegation",
                                "display": "Unconstrained delegation",
                                "isEpoch": False
                            },
                            {
                                "name": "whencreated",
                                "display": "When created",
                                "isEpoch": True
                            }
                        ]
                    }
                }
                detailedNodes = []

                for node in allNodes:

                    # Inicializamos el nuevo nodo detallado
                    newDetailedNode = dict()
                    newDetailedNode["nodeID"] = node["id"]
                    
                    #newDetailedNode["user"] = node["samaccountname"]
                    #newDetailedNode["domain"] = node["domain"]
                    newDetailedNode["owned"] = "true" if "owned" in node and node["owned"] else "false"
                    newDetailedNode["highvalue"] = "true" if "highvalue" in node and node["highvalue"] else "false"

                    # Inicializamos los apartados del nodo
                    for key in detailStructure:
                        newDetailedNode[key] = dict()

                        # Introducimos el título del apartado
                        newDetailedNode[key]["display"] = detailStructure[key]["display"]
                    
                        # Introducimos cada clave en su lugar
                        newDetailedNode[key]["elements"] = []
                        for element in detailStructure[key]["elements"]:
                            if element["name"] in node:
                                newDetailedNode[key]["elements"].append({
                                    "display": element["display"],
                                    "value": node[element["name"]],
                                    "isEpoch": element["isEpoch"]
                                })
                    
                    # Agregamos el nodo a la lista de nodos detallados
                    detailedNodes.append(newDetailedNode)
                
                edges = [e.to_dict() for e in graph.edges]
                
        
                if edges != []:
                    graph.options["layout"]["hierarchical"]["enabled"]='true'

                for e in edges:
                    e["label"]=e["type"]
                    e["title"]=e["type"]
                    e["group"]="community"
                    e["color"] = {
                        "color": "#FFFFFF",
                        "highlight": "green",
                    }
                    e["font"]= {
                        "align": "top",
                        "strokeWidth":0,
                        "color":"#FFFFFF",
                        "size":12
                    }

         
                for n in nodes:
                    
                    # input()
                    n["type"]=n["label"]
                    n["label"]=n["name"]
                    n["title"]=n["name"]
                    n["font"]= {
                        "color":"#FFFFFF",
                        "size":12
                    }
                    # n["mass"]=1

                    if "Group" in n["type"]:
                        n["shape"]="image"
                        if "owned" in n and n["owned"] is True:
                            if "highvalue" in n and n["highvalue"] is True:
                                n["image"]=url_for('static', filename='img/graph_icons/group-ht-owned.png')
                            else:
                                n["image"]=url_for('static', filename='img/graph_icons/group-owned.png')
                        else:
                            if "highvalue" in n and n["highvalue"] is True:
                                    n["image"]=url_for('static', filename='img/graph_icons/group-ht.png')
                            else:
                                n["image"]=url_for('static', filename='img/graph_icons/group.png')
                    elif "User" in n["type"]:
                        n["shape"] = "image"
                        if "owned" in n and n["owned"] is True:
                            if "highvalue" in n and n["highvalue"] is True:
                                n["image"] = url_for('static', filename='img/graph_icons/user-ht-owned.png')
                            else:
                                n["image"] = url_for('static', filename='img/graph_icons/user-owned.png')
                        else:
                            if "highvalue" in n and n["highvalue"] is True:
                                n["image"] = url_for('static', filename='img/graph_icons/user-ht.png')
                            else:
                                n["image"] = url_for('static', filename='img/graph_icons/user.png')
                    elif "Computer" in n["type"]:
                        n["shape"] = "image"
                        if "owned" in n and n["owned"] is True:
                            if "highvalue" in n and n["highvalue"] is True:
                                n["image"] = url_for('static', filename='img/graph_icons/pc-ht-owned.png')
                            else:
                                n["image"] = url_for('static', filename='img/graph_icons/pc-owned.png')
                        else:
                            if "highvalue" in n and n["highvalue"] is True:
                                n["image"] = url_for('static', filename='img/graph_icons/pc-ht.png')
                            else:
                                n["image"] = url_for('static', filename='img/graph_icons/pc.png')
                    elif "GPO" in n["type"]:
                        n["shape"] = "image"
                        n["image"] = url_for('static', filename='img/graph_icons/gpo.png')
                    elif "Domain" in n["type"]:
                        n["shape"] = "image"
                        n["image"] = url_for('static', filename='img/graph_icons/domain.png')
                    else:
                        pass

                options = str(graph.options) \
                .replace("\'true\'", "true") \
                .replace("\'false'", "false")

                return nodes, edges, options, detailedNodes
    
    dag=request.args.get('da_group') # domain admins group 
    file=request.args.get('nmapFile')
    targetNode = request.args.get("targetnode")
    try:
        #domains=get_domains()
        da_group=get_da_group()
        nmapFile=get_nmapFiles()
        print("\n\n\n",nmapFile,"\n\n\n")
        if dag is None: dag=da_group[0]
        
        if targetNode is None: targetNode = ""

        my_dict = json.load(open('cerberus/static/queries.json'))
        hiddenQueries = json.load(open('cerberus/static/hiddenQueries.json'))

        allQueries = {}
        queryCategory = ""

        for category in list(set([*my_dict] + [*hiddenQueries])):
            allQueries[category] = {}
            if category in my_dict:
                allQueries[category].update(my_dict[category])
            if category in hiddenQueries:
                allQueries[category].update(hiddenQueries[category])
            
            if query in [*allQueries[category]]:
                queryCategory = category

        if queryCategory is not "":
            if file is not None:
                x=allQueries[queryCategory][query]["query"].replace("DOMAIN ADMINS GROUP", dag).replace("DOMAIN ADMINS@DOMAIN.GR", dag).replace("TARGET_ID", targetNode).replace("NMAPFILE",file)
                n,e,o,d=draw(x)
            else:
                x=allQueries[queryCategory][query]["query"].replace("DOMAIN ADMINS GROUP", dag).replace("DOMAIN ADMINS@DOMAIN.GR", dag).replace("TARGET_ID", targetNode)
                n,e,o,d=draw(x)
        else:

            if file is not None:
                x=allQueries[queryCategory][query]["query"].replace("DOMAIN ADMINS GROUP", dag).replace("DOMAIN ADMINS@DOMAIN.GR", dag).replace("TARGET_ID", targetNode).replace("NMAPFILE",file)
                n,e,o,d=draw(x)
            else:
                x=allQueries[queryCategory][query]["query"].replace("DOMAIN ADMINS GROUP", dag).replace("DOMAIN ADMINS@DOMAIN.GR", dag).replace("TARGET_ID", targetNode)
                n,e,o,d=draw(x)
        print (f"\n\n{x}\n\n")
        n,e,o,d=draw(x)
        return render_template('core/graph_template.html',
                                projects=projects,
                                title="Graph",
                                nodes=n,
                                edges=e,
                                options=o,
                                detailedNodes=d,
                                links=my_dict,
                                da_group=da_group,
                                nmapFile=nmapFile
                                    )
    except Exception as e:
        print(e)
        flash('Error in neo4j database connection', 'danger')
        return redirect(url_for('core.dashboard'))
    
@core.route('/graph/sync', methods=['GET'])
@login_required
@check_project
@check_neo4j
def sync_neo4j():
    from cerberus.utils import usersAsOwned
    from cerberus import db2 as db

    db.db_link(request.cookies.get('project'))
    db.db_connect()

    from cerberus import models as m
    users = m.DomainUsers.get_owned()
    db.db_disconnect()
    result = usersAsOwned(users)



    flash(result[1], result[0])
        
    return redirect(request.referrer)

@core.route('/graph/get_computers', methods=['GET'])
@login_required
@check_neo4j
def get_computers():
    from neo4j import GraphDatabase
    from flask import send_file
    import io
    def ejecutar_consulta_y_obtener_resultados(uri, username, password, consulta):
        # Conexión a la base de datos Neo4j
        with GraphDatabase.driver(uri, auth=(username, password)) as driver:
            with driver.session() as session:
                # Ejecutar la consulta Cypher
                resultado = session.run(consulta)

                # Crear un objeto io.BytesIO para almacenar los resultados en memoria
                contenido = io.BytesIO()

                for registro in resultado:
                    contenido.write(f"{registro['m.name']}\n".encode('utf-8'))

                # Devolver el contenido
                return contenido.getvalue()
    # Consulta Cypher
    consulta = "MATCH (m:Computer) RETURN m.name"

    # Obtener resultados como bytes
    resultados = ejecutar_consulta_y_obtener_resultados(uri=g.user[3], username=g.user[4], password=g.user[5], consulta=consulta)

    # Devolver los resultados como un archivo descargable
    return send_file(
        io.BytesIO(resultados),
        as_attachment=True,
        download_name="computers.txt",
        mimetype="text/plain"
    )

# -------------------------------------------------------------------------------------------