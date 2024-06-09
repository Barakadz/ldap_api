import ldap
from ldap.controls import SimplePagedResultsControl
import base64, socket, os


def getReachableLDAP():
    LDAP_Servers = ["10.10.10.10", "10.10.10.11", "10.30.10.10", "10.31.10.10"]
    
    for server in LDAP_Servers:
        try:
            #HOST_UP  = True if os.system(f"ping {server}") is 0 else False
            socket.create_connection((server, 389))
            return server
                
        except socket.error:
	        continue

    return "10.10.10.10"


def initializeLDAPConnection(baseDN, searchScope, retrieveAttributes, searchFilter):
    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    username = "CN=CT_TEST,OU=Users,OU=GSHR,DC=groupe-hasnaoui,DC=local"
    password = "123456"

    connection.protocol_version = ldap.VERSION3
    connection.set_option(ldap.OPT_REFERRALS, 0)
    connection.simple_bind_s(username, password)

    return connection


def getCompanies():

    try:
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_ONELEVEL
        # retrieveAttributes = ["cn","objectCategory","distinguishedName"]
        retrieveAttributes = ["name", "ou", "description", "displayName", "street"] # You can add mooooore ...
        # searchFilter = "(sAMAccountName="+ad2000+")"
        searchFilter = "(&(objectCategory=organizationalUnit)(objectClass=organizationalUnit)(ou=*))"
        # searchFilter = "((objectCategory=CN=Computer,CN=Schema,CN=Configuration,DC=groupe-hasnaoui,DC=local))"
        # ldap.result()
        

        connection = initializeLDAPConnection(baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

       
        # print("before ldap_result_id")
        ldap_result_id = connection.search(baseDN, searchScope, searchFilter, retrieveAttributes)
        # print("after ldap_result_id")


        result_set = []
        
        while True:
            result_type, result_data = connection.result(ldap_result_id, 0)
            if (result_data == []):
                break
            else:
                if result_type == ldap.RES_SEARCH_ENTRY:
                    try:
                        result_set.append(result_data)
                    except:
                        pass

        BranchesNotInitializedYet = ["STON", "CLIN", "HTTV", "IPDZ", "IPTV", "MDCR", "RPSO", "RYML", "HPSS", "HFND", "DRNA", "HTRM", "GSHR"]
        results = []
        count = 0
        for entry in result_set:
            if entry[0][0] is not None:
                if len(entry[0][1]['ou'][0].decode()) <= 4 and entry[0][1]['ou'][0].decode() not in BranchesNotInitializedYet:
                    #print(entry[0][1]['ou'][0].decode()+" - "+entry[0][1]['description'][0].decode())
                    count += 1
                    results.append({"Name": entry[0][1]['name'][0].decode(), "OU": entry[0][1]['ou'][0].decode(), "Description": entry[0][1]['description'][0].decode(), "DisplayName": entry[0][1]['displayName'][0].decode(), "Pole": entry[0][1]['street'][0].decode()})
        #print("Count OU: "+str(count))
        
        connection.unbind_s()
        
        return results

    except Exception as error:
        print("Error: "+str(error))


def getActiveUsersbyCompany(companyname):

    companies = []
    for company in getCompanies():
        companies.append(company["OU"])

    if companyname not in companies:
        return {"Error": "Branch doesn't exist"}

    try:
        baseDN = f"OU={companyname},DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail", "company", "department", "telephoneNumber", "title"] # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
        
        connection = initializeLDAPConnection(baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(criticality=True, size=page_size, cookie='')
        
        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True: # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)
        
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie: # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break   

        results = []
        count = 0
        for entry in result_set:
            if entry[0] is not None:
                count += 1

                results.append({"fullname": entry[1]['cn'][0].decode(),  
                                "structure" : f"{entry[1]['company'][0].decode()}/{entry[1]['department'][0].decode()}",
                                "title": entry[1]['title'][0].decode(),  
                                "mail": entry[1]['mail'][0].decode(),
                                "phonenumber": entry[1]['telephoneNumber'][0].decode()})
        
        #print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def getDepartmentsbyCompany(companyname):

    companies = []
    for company in getCompanies():
        companies.append(company["OU"])

    if companyname not in companies:
        return {"Error": "Branch doesn't exist"}

    department = []
    
    try:
    
        baseDN = f"OU={companyname},DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail", "company", "department", "telephoneNumber", "title"] # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)


        page_size = 500
        req_ctrl = SimplePagedResultsControl(criticality=True, size=page_size, cookie='')
        
        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True: # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)
        
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie: # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break   

        count = 0
        for entry in result_set:
            if entry[0] is not None:
                
                if entry[1]['department'][0].decode() not in department:
                    department.append(entry[1]['department'][0].decode())

        
        #print(count)
        connection.unbind_s()
        return {"departments": department}

    except Exception as error:
        print("Error: "+str(error))


def getActiveUsers():

    try:
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail", "company", "department", "telephoneNumber", "title"] # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
        
        connection = initializeLDAPConnection(baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(criticality=True, size=page_size, cookie='')
        
        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True: # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)
        
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie: # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break   

        results = []
        count = 0
        for entry in result_set:
            if entry[0] is not None:
                count += 1

                try:
                    title = entry[1]['title'][0].decode()
                except:
                    title = "NA"

                try:
                    company = entry[1]['company'][0].decode()
                except:
                    company = "NA"

                try:
                    department = entry[1]['department'][0].decode()
                except:
                    department = "NA"

                try:
                    mail = entry[1]['mail'][0].decode()
                except:
                    mail = "NA"

                try:
                    phone = entry[1]['telephoneNumber'][0].decode()
                except:
                    phone = "NA"



                results.append({"fullname": entry[1]['cn'][0].decode(), 
                                "name":  entry[1]['sn'][0].decode(),
                                "company": company,
                                "department": department, 
                                "title": title,  
                                "mail": mail,
                                "phonenumber": phone})
        
        #print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def getUserInfo(usermail):
    
    try:
        
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "mail", "company", "department", "title", "thumbnailPhoto", "telephoneNumber"] # You can add mooooore ...
        searchFilter = f"(mail={usermail})"

        connection = initializeLDAPConnection(baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        
        page_size = 500
        req_ctrl = SimplePagedResultsControl(criticality=True, size=page_size, cookie='')
        
        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True: # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)
        
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie: # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break   

        results = []

        for entry in result_set:
            
            if entry[0] is not None:

                try:
                    title = entry[1]['title'][0].decode()
                except:
                    title = "NA"

                try:
                    company = entry[1]['company'][0].decode()
                except:
                    company = "NA"

                try:
                    department = entry[1]['department'][0].decode()
                except:
                    department = "NA"

                try:
                    mail = entry[1]['mail'][0].decode()
                except:
                    mail = "NA"

                try:
                    phone = entry[1]['telephoneNumber'][0].decode()
                except:
                    phone = "NA"

                try:
                    photo = base64.encodebytes(entry[1]['thumbnailPhoto'][0]).decode()
                except:
                    photo = "NA"

                results.append({"fullname": entry[1]['cn'][0].decode(), 
                                "name":  entry[1]['sn'][0].decode(),
                                "company": company,
                                "department": department, 
                                "title": title,  
                                "mail": mail,
                                "phonenumber": phone,
                                "photo": photo})

        connection.unbind_s()

        return results[0]

    except Exception as error:
        print("Error: "+str(error))


def getManagerInfo(DN):

    try:
        
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["company", "department", "title", "cn", "sn", "mail", "telephoneNumber", "sAMAccountName"] # You can add mooooore ...
        searchFilter = f"(distinguishedName={DN})"

        connection = initializeLDAPConnection(baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        
        page_size = 500
        req_ctrl = SimplePagedResultsControl(criticality=True, size=page_size, cookie='')
        
        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True: # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)
        
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie: # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break   

        results = []

        for entry in result_set:
            
            if entry[0] is not None:

                try:
                    title = entry[1]['title'][0].decode()
                except:
                    title = "NA"

                try:
                    company = entry[1]['company'][0].decode()
                except:
                    company = "NA"

                try:
                    department = entry[1]['department'][0].decode()
                except:
                    department = "NA"

                try:
                    mail = entry[1]['mail'][0].decode()
                except:
                    mail = "NA"

                try:
                    phone = entry[1]['telephoneNumber'][0].decode()
                except:
                    phone = "NA"


                results.append({
                                "company": company,
                                "department": department,
                                "title": title,  
                                "fullname": entry[1]['cn'][0].decode(), 
                                "name":  entry[1]['sn'][0].decode(),
                                "mail": mail,
                                "phonenumber": phone,
                                "samAccount": entry[1]['sAMAccountName'][0].decode()
                                })

        connection.unbind_s()

        return results[0]

    except Exception as error:
        print("Error: "+str(error))


def getUserInfoHPM(usermail):
    
    try:
        
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["company", "department", "title", "cn", "givenName", "mail", "sn", "telephoneNumber", "sAMAccountName", "thumbnailPhoto", "manager"] # You can add mooooore ...
        searchFilter = f"(mail={usermail})"

        connection = initializeLDAPConnection(baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        
        page_size = 500
        req_ctrl = SimplePagedResultsControl(criticality=True, size=page_size, cookie='')
        
        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True: # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)
        
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie: # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break   

        results = []

        for entry in result_set:
            
            if entry[0] is not None:

                retrieveAttributes = ["", "", "manager"] # You can add mooooore ...

                try:
                    title = entry[1]['title'][0].decode()
                except:
                    title = "NA"

                try:
                    company = entry[1]['company'][0].decode()
                except:
                    company = "NA"

                try:
                    department = entry[1]['department'][0].decode()
                except:
                    department = "NA"

                try:
                    mail = entry[1]['mail'][0].decode()
                except:
                    mail = "NA"

                try:
                    phone = entry[1]['telephoneNumber'][0].decode()
                except:
                    phone = "NA"

                try:
                    photo = base64.encodebytes(entry[1]['thumbnailPhoto'][0]).decode()
                except:
                    photo = "NA"

                try:
                    manager = entry[1]['manager'][0].decode()
                except:
                    manager = False

                if manager:

                    results.append({
                                "company": company,
                                "department": department,
                                "title": title,  
                                "fullname": entry[1]['cn'][0].decode(), 
                                "name":  entry[1]['sn'][0].decode(),
                                "mail": mail,
                                "phonenumber": phone,
                                "photo": photo, 
                                "samAccount": entry[1]['sAMAccountName'][0].decode(),
                                "manager_exists": True,
                                "manager": getManagerInfo(manager)
                                })

                
                else:
                    results.append({
                                "company": company,
                                "department": department,
                                "title": title,  
                                "fullname": entry[1]['cn'][0].decode(), 
                                "name":  entry[1]['sn'][0].decode(),
                                "mail": mail,
                                "phonenumber": phone,
                                "photo": photo, 
                                "samAccount": entry[1]['sAMAccountName'][0].decode(),
                                "manager_exists": False
                                })


        connection.unbind_s()

        return results[0]

    except Exception as error:
        print("Error: "+str(error))


def memberOf(username, groupname):

    ldapserver = getReachableLDAP()
    connect = ldap.initialize(f'ldap://{ldapserver}')

    connect.protocol_version = 3
    connect.set_option(ldap.OPT_REFERRALS, 0)
    connect.simple_bind_s('CN=CT_TEST,OU=Users,OU=GSHR,DC=groupe-hasnaoui,DC=local', '123456')
    result = connect.search_s('dc=groupe-hasnaoui,dc=local', ldap.SCOPE_SUBTREE, f'mail={username}', ['memberOf'])
    
    try:
        for group in result[0][1]["memberOf"]:
            if groupname == group.decode().strip("CN=").split(",")[0]:
                return True
                break
        
        return False
    except:
        return False


def isAuthenticatedCheckUp(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    if not username or not password:
        {"response": False, "exception": "username or password not provided"}

    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)

            if memberOf(username=username, groupname="GSHR-CHECKUP-R"):
                if memberOf(username=username, groupname="GSHR-CHECKUP-W"):
                    return {"authenticated": True, "userinfo": userinfo, "write": True}
                return {"authenticated": True, "userinfo": userinfo, "write": False}            
            return  {"authenticated": False, "exception": "Accès refusé"} 

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedRyadcom(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    if not username or not password:
        {"response": False, "exception": "username or password not provided"}

    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)

            if memberOf(username=username, groupname="GSHR-RYADCOM"):
                    return {"authenticated": True, "userinfo": userinfo}            
            return  {"authenticated": False, "exception": "Accès refusé"} 

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedGSHDocs(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    if not username or not password:
        {"response": False, "exception": "username or password not provided"}

    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            return {"authenticated": True, "userinfo": getUserInfo(username)}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedMyCard(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    if not username or not password:
        {"response": False, "exception": "username or password not provided"}

    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)

            if memberOf(username=username, groupname="GSHR-MYCARD"):
                return {"authenticated": True, "userinfo": userinfo}            
            return  {"authenticated": False, "exception": "Accès refusé"} 

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedHPM(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    if not username or not password:
        {"response": False, "exception": "username or password not provided"}

    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            return {"authenticated": True, "userinfo": getUserInfoHPM(username)}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def getAllManagers():
    try:
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail", "company", "department", "telephoneNumber", "title", "manager", "directReports"] # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"
        
        connection = initializeLDAPConnection(baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(criticality=True, size=page_size, cookie='')
        
        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True: # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)
        
            pctrls = [c for c in serverctrls if c.controlType == SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie: # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break   

        results = []
        count = 0
        for entry in result_set:
            if entry[0] is not None:
                count += 1

                try:
                    title = entry[1]['title'][0].decode()
                except:
                    title = "NA"

                try:
                    company = entry[1]['company'][0].decode()
                except:
                    company = "NA"

                try:
                    department = entry[1]['department'][0].decode()
                except:
                    department = "NA"

                try:
                    mail = entry[1]['mail'][0].decode()
                except:
                    mail = "NA"

                try:
                    phone = entry[1]['telephoneNumber'][0].decode()
                except:
                    phone = "NA"

                try:
                    manager = entry[1]['manager'][0].decode()
                except:
                    manager = "NA"

                try:
                    directReports = entry[1]['directReports'][0].decode()
                except:
                    directReports = "NA"


                results.append({"fullname": entry[1]['cn'][0].decode(), 
                                "name":  entry[1]['sn'][0].decode(),
                                "company": company,
                                "department": department, 
                                "title": title,  
                                "mail": mail,
                                "phonenumber": phone,
                                "manager": manager,
                                "sAMAccountName": entry[1]['sAMAccountName'][0].decode(),
                                "directReports": directReports})
        
        #print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def realManagers():
    result = getAllManagers()
    count = 0
    list = []
    for entry in result:
        if entry["manager"] == "NA" and entry["directReports"] != "NA":
            count += 1
            list.append({"name": entry["fullname"], "company": entry["company"], "title": entry["title"], "sAMAccountName": entry["sAMAccountName"]})

    return {"users": list, "count": count}


def fakeManagers():
    result = getAllManagers()
    count = 0
    list = []
    for entry in result:
        if entry["manager"] == "NA" and entry["directReports"] == "NA":
            count += 1
            list.append({"name": entry["fullname"], "company": entry["company"], "title": entry["title"], "sAMAccountName": entry["sAMAccountName"]})

    return {"users": list, "count": count}


if __name__ == "__main__":
    #print(getCompanies())
    #print(getActiveUsersbyCompany("GSHA"))
    #print(getDepartmentsbyCompany("GSHA"))
    #print(getActiveUsers())
    #print(isAuthenticatedCheckUp("nacereddine.boulerial@groupe-hasnaoui.com", "Azerty1234"))
    #print(isAuthenticatedGSHDocs("nacereddine.boulerial@groupe-hasnaoui.com", "Azerty1234"))
    #print(isAuthenticatedCheckUp("ct.test@groupe-hasnaoui.com", "123456"))
    #print(isAuthenticatedGSHDocs("ct.test@groupe-hasnaoui.com", "123456"))
    #print(isAuthenticatedHPM("nacereddine.boulerial@groupe-hasnaoui.com", "Azerty1234"))
    #print(isAuthenticatedHPM("ct.test@groupe-hasnaoui.com", "123456"))
    #print(isAuthenticatedHPM("bachir.belkhiri@groupe-hasnaoui.com", "Bibiche2061994"))
    pass