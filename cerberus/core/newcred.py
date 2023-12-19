def insert_new_cred(ntlm, plain, session):
    from cerberus import models as m
    # import db
    from cerberus.utils import current_datetime
    if plain is None: # Si no hay password, solo se inserta el hash NTLM
        cred=m.Credentials.get(ntlm=ntlm)
        if cred is None:
            cred=m.Credentials(ntlm=ntlm, date=current_datetime())
            session.add(cred)
            session.commit()
            print(f'[+] Hash NTLM {ntlm} sussefully added')
            return(f'Hash NTLM {ntlm} sussefully added', 'success')
        else:
            print(f'[!] Hash NTLM {ntlm} already exists')
            return(f'Hash NTLM {ntlm} already exists', 'warning')
    else: # Si hay password, se inserta el hash NTLM y la password
        cred=m.Credentials.get(ntlm=ntlm)
        if cred is None:
            cred=m.Credentials(ntlm=ntlm, plain=plain, date=current_datetime())
            session.add(cred)
            session.commit()
            print(f'[+] Password {plain} with NTLM {ntlm} sussefully added')
            return(f'Password {plain} with NTLM {ntlm} sussefully added', 'success')
        else:
            if cred.plain is None:
                cred.plain=plain
                session.commit()
                print(f'[+] Password {plain} with NTLM {ntlm} sussefully updated')
                return(f'Password {plain} with NTLM {ntlm} sussefully updated', 'success')
            else:    
                print(f'[!] Password {plain} with NTLM {ntlm} already exists')
                return(f'Password {plain} with NTLM {ntlm} already exists', 'warning')