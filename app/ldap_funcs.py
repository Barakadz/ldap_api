import ldap
from ldap.controls import SimplePagedResultsControl
import ldap.modlist as modlist
import base64
import socket
import os
import unicodedata


def getReachableLDAP():
    LDAP_Servers = ["10.20.10.11", "10.20.10.10", "10.10.10.10", "10.30.10.10"]

    for server in LDAP_Servers:
        try:
            # HOST_UP  = True if os.system(f"ping {server}") is 0 else False
            socket.create_connection((server, 389))
            # print(server)
            return server

        except socket.error:
            continue


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
        # searchFilter = "(sAMAccountName="+ad2000+")"
        retrieveAttributes = ["name", "ou",
                              "description", "displayName", "street"]
        searchFilter = "(&(objectCategory=organizationalUnit)(objectClass=organizationalUnit)(ou=*))"
        # searchFilter = "((objectCategory=CN=Computer,CN=Schema,CN=Configuration,DC=groupe-hasnaoui,DC=local))"
        # ldap.result()

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        # print("before ldap_result_id")
        ldap_result_id = connection.search(
            baseDN, searchScope, searchFilter, retrieveAttributes)
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

        BranchesNotInitializedYet = ["STON", "HTTV", "IPDZ", "IPTV",
                                     "RPSO", "RYML", "HPSS", "HFND", "DRNA", "HTRM", "GSHR"]
        results = []
        count = 0
        # print("result_set",result_set)
        for entry in result_set:
            print("entry[0][0]", entry[0][0])
            print("entry[0][1]", entry[0][1])
            if entry[0][0] is not None:
                if len(entry[0][1]['ou'][0].decode()) <= 4 and entry[0][1]['ou'][0].decode() not in BranchesNotInitializedYet:
                    # print(entry[0][1]['ou'][0].decode()+" - "+entry[0][1]['description'][0].decode())
                    count += 1
                    entries = {"Name": entry[0][1]['name'][0].decode(),                                                                                                 "OU": entry[0][1]['ou'][0].decode(),
                               "Description": "non renseigne" if entry[0][1].get('description') == None else entry[0][1]['description'][0].decode(),
                               "DisplayName": "non renseigne" if entry[0][1].get('displayName') == None else entry[0][1]['displayName'][0].decode(),
                               "Pole": "non renseigne" if entry[0][1].get('street') == None else entry[0][1]['street'][0].decode()}
                    results.append(entries)
        # print("Count OU: "+str(count))

        connection.unbind_s()

        return results

    except Exception as error:
        print("Error: "+str(error))


def getTownsbyCompany(companyname):

    try:
        baseDN = f"OU={companyname},DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_ONELEVEL
        # You can add mooooore ...
        retrieveAttributes = ["name", "ou", "description"]
        # searchFilter = "(sAMAccountName="+ad2000+")"
        searchFilter = "(&(objectCategory=organizationalUnit)(objectClass=organizationalUnit)(ou=*))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        # print("before ldap_result_id")
        ldap_result_id = connection.search(
            baseDN, searchScope, searchFilter, retrieveAttributes)
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

        BranchesNotInitializedYet = ["STON", "CLIN", "HTTV", "IPDZ", "IPTV",
                                      "RPSO", "RYML", "HPSS", "HFND", "DRNA", "HTRM", "GSHR"]
        results = []
        count = 0

        for entry in result_set:
            if entry[0][0] is not None:
                if len(entry[0][1]['ou'][0].decode()) <= 4 and entry[0][1]['ou'][0].decode() not in BranchesNotInitializedYet:
                    # print(entry[0][1]['ou'][0].decode()+" - "+entry[0][1]['description'][0].decode())
                    count += 1
                    results.append({"Name": entry[0][1]['name'][0].decode(), "OU": entry[0][1]['ou'][0].decode(
                    ), "Description": entry[0][1]['description'][0].decode()})
        # print("Count OU: "+str(count))

        connection.unbind_s()

        return results

    except Exception as error:
        print("Error: "+str(error))


def getDisabledUsers():

    try:
        baseDN = f"DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail",
                              "company", "whenChanged", "whenCreated"]  # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(userAccountControl:1.2.840.113556.1.4.803:=2))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
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
                                "fname": entry[1]['givenName'][0].decode(),
                                "lname": entry[1]['sn'][0].decode(),
                                "company": entry[1]['company'][0].decode(),
                                "whenChanged": entry[1]['whenChanged'][0].decode(),
                                "whenCreated": entry[1]['whenCreated'][0].decode()})

        # print(count)
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
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail",
                              "company", "department", "telephoneNumber", "title"]  # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
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
                                "lname": entry[1]['sn'][0].decode(),
                                "fname": entry[1]['givenName'][0].decode(),
                                "structure": f"{entry[1]['company'][0].decode()}/{entry[1]['department'][0].decode()}",
                                "title": entry[1]['title'][0].decode(),
                                "mail": entry[1]['mail'][0].decode(),
                                "phonenumber": entry[1]['telephoneNumber'][0].decode()})

        # print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def getActiveUsersbyCompanyAndTown(companyname, townname):

    companies = []
    for company in getCompanies():
        companies.append(company["OU"])
    if companyname not in companies:
        return {"Error": f"Company {companyname} doesn't exist"}

    towns = []
    for town in getTownsbyCompany(companyname):
        towns.append(town["OU"])
    if townname not in towns:
        return {"Error": f"Town {townname} doesn't exist for {companyname} company"}

    try:
        baseDN = f"OU={townname},OU={companyname},DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail",
                              "company", "department", "telephoneNumber", "title"]  # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
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
                                "fname": entry[1]['givenName'][0].decode(),
                                "lname": entry[1]['sn'][0].decode(),
                                "company": entry[1]['company'][0].decode(),
                                "department": entry[1]['department'][0].decode(),
                                "title": entry[1]['title'][0].decode(),
                                "mail": entry[1]['mail'][0].decode(),
                                "phonenumber": entry[1]['telephoneNumber'][0].decode()})

        # print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def getALlDepartments():

    department = []

    try:

        baseDN = f"DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail",
                              "company", "department", "telephoneNumber", "title"]  # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        count = 0
        for entry in result_set:
            if entry[0] is not None:

                if entry[1]['department'][0].decode() not in department:
                    department.append(entry[1]['department'][0].decode())

        # print(count)
        connection.unbind_s()
        return {"departments": department}

    except Exception as error:
        print("Error: "+str(error))


def getDepartmentDescription(department):

    departments = {"TRS": "Transport",
                   "GDS": "Gestion Des Stocks",
                   "EXP": "Exploitation",
                   "DAG": "Direction Administration Générale",
                   "DFC": "Direction Finance et Comptabilité",
                   "DTQ": "Direction Technique",
                   "DCO": "Direction Commerciale",
                   "DRH": "Direction Ressources Humaines",
                   "PRM": "Production et Maintenance",
                   "DQH": "Direction Qualité & Hygiène",
                   "LOG": "Logistique",
                   "RHB": "Restauration et Hébergement",
                   "DQC": "Direction Contrôle Qualité",
                   "LAB": "Laboratoire",
                   "DAA": "Direction Achats et Approvisionnement",
                   "DGR": "Direction Générale",
                   "HSE": "Hygiène, Santé et Environnement",
                   "PRO": "Production",
                   "CPO": "Cellule Projet Odoo",
                   "MNT": "Maintenance",
                   "DSI": "Direction Système d'Information",
                   "DCG": "Direction Contrôle de Gestion",
                   "GAR": "Gardiennage",
                   "DAJ": "Département des Affaires Juridiques ",
                   "MDC": "Montage Des Cuisines",
                   "MGT": "Management",
                   "DMK": "Direction Marketing",
                   "CCS": "Cellule Contrôle Système",
                   "DCE": "Direction Commerce Extérieur",
                   "CCF": "Cellule Comptabilité et Facturation",
                   "DPJ": "Direction Projets",
                   "CBI": "Cellule Business Intelligence",
                   "SMQ": "Système Management Qualité",
                   "DAT": "Direction Assistance Technique",
                   "DRE": "Direction de Réalisation",
                   "BDM": "Business Development Management",
                   "POS": "Equipe de Pose",
                   "FOR": "Formation"}

    if str(department).islower():
        department = str(department).upper()

    if department in departments.keys():
        return {department: departments[department]}

    else:
        return {"exception": "Please contact Bachir to update this department's description !!"}


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
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail",
                              "company", "department", "telephoneNumber", "title"]  # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        count = 0
        for entry in result_set:
            if entry[0] is not None:

                if entry[1]['department'][0].decode() not in department:
                    department.append(entry[1]['department'][0].decode())

        # print(count)
        connection.unbind_s()
        return {"departments": department}

    except Exception as error:
        print("Error: "+str(error))


def getActiveUsers():

    try:
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "sAMAccountName", "mail",
                              "company", "department", "telephoneNumber", "title", "ipPhone", "manager"]  # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
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
                    sAMAccountName = entry[1]['sAMAccountName'][0].decode()
                except:
                    sAMAccountName = "NA"
                try:
                    manager = entry[1]['manager'][0].decode()
                except:
                    manager = "NA"
                try:
                    ipPhone = entry[1]['ipPhone'][0].decode()
                except:
                    ipPhone = "NA"

                results.append({"fullname": entry[1]['cn'][0].decode(),
                                "lname":  entry[1]['sn'][0].decode(),
                                "fname":  entry[1]['givenName'][0].decode(),
                                "company": company,
                                "department": department,
                                "title": title,
                                "mail": mail,
                                "phonenumber": phone,
                                "ipPhone": ipPhone,
                                "AD2000": sAMAccountName,
                                "manager": manager})

        # print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def getActiveUsersAD2000():

    try:
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["sAMAccountName"]  # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        results = []
        # count = 0
        for entry in result_set:
            if entry[0] is not None:
                # count += 1

                results.append(entry[1]['sAMAccountName'][0].decode())

        # print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def getUserInfo(usermail):

    try:

        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["cn", "sn", "givenName", "mail", "company", "department", "title",
                              "thumbnailPhoto", "telephoneNumber", "sAMAccountName"]  # You can add mooooore ...
        searchFilter = f"(mail={usermail})"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
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
                    print(entry[1]['thumbnailPhoto'][0])
                    print(type(entry[1]['thumbnailPhoto'][0]))
                    photo = base64.encodebytes(
                        entry[1]['thumbnailPhoto'][0]).decode()
                except:
                    photo = "NA"

                results.append({"fullname": entry[1]['cn'][0].decode(),
                                "name":  entry[1]['sn'][0].decode(),
                                "fname": entry[1]['givenName'][0].decode(),
                                "ad2000": entry[1]['sAMAccountName'][0].decode(),
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


def re(DN):

    try:

        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        # You can add mooooore ...
        retrieveAttributes = ["company", "department", "title",
                              "cn", "sn", "mail", "telephoneNumber", "sAMAccountName"]
        searchFilter = f"(distinguishedName={DN})"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
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


def lockedUsers():

    try:
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        # You can add mooooore ...
        retrieveAttributes = ["cn", "mail", "company",
                              "lockoutTime", "distinguishedName"]
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(lockoutTime>=1)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        # print(result_set)
        results = []
        count = 0
        for entry in result_set:
            if entry[0] is not None:
                count += 1

                try:
                    company = entry[1]['company'][0].decode()
                except:
                    company = "NA"

                try:
                    lockoutTime = entry[1]['lockoutTime'][0].decode()
                except:
                    lockoutTime = "NA"

                try:
                    mail = entry[1]['mail'][0].decode()
                except:
                    mail = "NA"

                try:
                    cn = entry[1]['cn'][0].decode()
                except:
                    cn = "NA"

                try:
                    BaseDN = entry[1]['distinguishedName'][0].decode()
                except:
                    cn = "NA"

                results.append({"fullname": cn,
                                "company": company,
                                "mail": mail,
                                "lockoutime": lockoutTime,
                                "BaseDN": BaseDN})

        # print(count)
        connection.unbind_s()
        if results:
            return {"locked": True, "results": results}

        return {"locked": False, "results": results}

    except Exception as error:
        exception = error.args[0]["desc"]
        return {"locked": False, "exception": exception}


def lockedUsersDNs():

    try:
        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        # You can add mooooore ...
        retrieveAttributes = ["cn", "mail", "company",
                              "lockoutTime", "distinguishedName"]
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(lockoutTime>=1)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        results = []

        for entry in result_set:
            if entry[0] is not None:

                try:
                    BaseDN = entry[1]['distinguishedName'][0].decode()
                except:
                    BaseDN = "NA"

                if BaseDN != "NA":
                    results.append(BaseDN)

        # print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def unlockUsers():

    l = ldap.initialize('ldap://10.10.10.10')

    username = "CN=CS Automation,OU=Users,OU=GSHR,DC=groupe-hasnaoui,DC=local"
    password = "@uToM@$ion_!$_3vryTh!ng"

    try:
        l.protocol_version = ldap.VERSION3
        l.set_option(ldap.OPT_REFERRALS, 0)
        l.simple_bind_s(username, password)

        # modlist = [(ldap.MOD_ADD, "employeeID", "0001".encode())] # Add any value to the employeeID attribute
        # modlist = [(ldap.MOD_DELETE, "employeeID", "0001".encode())] # You need to specify the same employeeID value in order to delete it
        # Replace the employeeID value with another one
        modlist = [(ldap.MOD_REPLACE, "lockoutTime", "0".encode())]

        BaseDNs = lockedUsersDNs()

        unlocked_list = []

        for BaseDN in BaseDNs:
            # Do the actual modification
            l.modify_s(BaseDN, modlist)
            unlocked_list.append(f"{BaseDN}: Unlocked")

        # Its nice to the server to disconnect and free resources when done
        l.unbind_s()

        return {"unlocked": True, "list": unlocked_list}

    except Exception as error:
        exception = error.args[0]["desc"]
        return {"unlocked": False, "exception": exception}


def getUserInfoHPM(usermail):

    try:

        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["company", "department", "title", "cn", "givenName", "mail", "sn",
                              "telephoneNumber", "sAMAccountName", "thumbnailPhoto", "manager"]  # You can add mooooore ...
        searchFilter = f"(mail={usermail})"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        results = []

        for entry in result_set:

            if entry[0] is not None:

                # You can add mooooore ...
                retrieveAttributes = ["", "", "manager"]

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
                    photo = base64.encodebytes(
                        entry[1]['thumbnailPhoto'][0]).decode()
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
                        "manager": re(manager)
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
    connect.simple_bind_s(
        'CN=CT_TEST,OU=Users,OU=GSHR,DC=groupe-hasnaoui,DC=local', '123456')
    result = connect.search_s('dc=groupe-hasnaoui,dc=local',
                              ldap.SCOPE_SUBTREE, f'mail={username}', ['memberOf'])

    try:
        for group in result[0][1]["memberOf"]:
            if groupname == group.decode().strip("CN=").split(",")[0]:
                return True
                break

        return False
    except:
        return False


def getDrivers():

    ldapserver = getReachableLDAP()
    connect = ldap.initialize(f'ldap://{ldapserver}')

    connect.protocol_version = 3
    connect.set_option(ldap.OPT_REFERRALS, 0)
    connect.simple_bind_s(
        'CN=CT_TEST,OU=Users,OU=GSHR,DC=groupe-hasnaoui,DC=local', '123456')
    result = connect.search_s('dc=groupe-hasnaoui,dc=local',
                              ldap.SCOPE_SUBTREE, f'cn=GSHR-DRIVERS', ['member'])

    list = []

    try:
        for driver in result[0][1]["member"]:
            list.append(driver.decode().split(",")[0][3:])

        return {"response": True, "data": list}

    except Exception as e:
        return {"response": False, "error": str(e)}


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
            return {"authenticated": False, "exception": "Accès refusé"}

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
            return {"authenticated": False, "exception": "Accès refusé"}

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


def isAuthenticatedHelpdesk(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    if not username or not password:
        {"response": False, "exception": "username or password not provided"}

    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            return {"authenticated": True, "userinfo": userinfo}

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
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedElmedina(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    if not username or not password:
        {"response": False, "exception": "username or password not provided"}

    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)

            if memberOf(username=username, groupname="GSHR-ELMEDINA"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedQRGenerator(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')

    if not username or not password:
        {"response": False, "exception": "username or password not provided"}

    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)

            if memberOf(username=username, groupname="GSHR-QRGENERATOR"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedHpsProd(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)

            if memberOf(username=username, groupname="GSHR-HPS-PROD"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedPumaPRD(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="PUMA-PRD"):
                return {"authenticated": True, "userinfo": userinfo}

            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedPumaTRN(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="PUMA-TRN"):
                return {"authenticated": True, "userinfo": userinfo}

            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedGshPST(username, password):
    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="GSH-PST"):
                return {"authenticated": True, "userinfo": userinfo}

            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedMdmCmrs(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="HMDM-CMRS"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isLastnameUpper():

    try:
        baseDN = f"DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["sn"]  # You can add mooooore ...
        searchFilter = "(&(objectCategory=Person)(objectClass=User)(telephoneNumber=*)(department=*)(mail=*)(givenName=*)(sn=*)(sAMAccountName=*)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        results = []
        count = 0
        for entry in result_set:
            if entry[0] is not None:
                count += 1

                name = entry[1]['sn'][0].decode()

                if name.isupper():
                    continue
                results.append(name)

        # print(count)
        connection.unbind_s()
        return results

    except Exception as error:
        print("Error: "+str(error))


def get_companyname_by_username(username):

    try:

        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["company", "department",
                              "cn", "mail", "sAMAccountName"]
        searchFilter = f"(sAMAccountName={username})"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        results = []

        for entry in result_set:

            if entry[0] is not None:

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

                results.append({
                    "company": company,
                    "department": department,
                    "fullname": entry[1]['cn'][0].decode(),
                    "mail": mail,
                    "sAMAccountName": entry[1]['sAMAccountName'][0].decode()
                })

        connection.unbind_s()

        return results[0]

    except Exception as error:
        print("Error: "+str(error))
        return None


def get_IT_by_companyname(companyname):

    try:

        baseDN = "DC=groupe-hasnaoui,DC=local"
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ["mail"]
        searchFilter = f"(&(company={companyname})(department=DSI)(telephoneNumber=*)(!(title=App*)))"

        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)

        page_size = 500
        req_ctrl = SimplePagedResultsControl(
            criticality=True, size=page_size, cookie='')

        msgid = connection.search_ext(base=baseDN, scope=ldap.SCOPE_SUBTREE,
                                      filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])

        result_set = []
        pages = 0
        while True:  # loop over all of the pages using the same cookie, otherwise the search will fail
            pages += 1
            rtype, rdata, rmsgid, serverctrls = connection.result3(msgid)
            for user in rdata:
                result_set.append(user)

            pctrls = [c for c in serverctrls if c.controlType ==
                      SimplePagedResultsControl.controlType]
            if pctrls:
                if pctrls[0].cookie:  # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = connection.search_ext(
                        base=baseDN, scope=ldap.SCOPE_SUBTREE, filterstr=searchFilter, attrlist=retrieveAttributes, serverctrls=[req_ctrl])
                else:
                    break
            else:
                break

        results = []

        for entry in result_set:

            if entry[0] is not None:

                try:
                    mail = entry[1]['mail'][0].decode()
                except:
                    mail = "NA"

                results.append(mail.lower())

        connection.unbind_s()

        return results

    except Exception as error:
        print("Error: "+str(error))
        return None


def get_company_IT_by_username(username):

    try:
        if get_companyname_by_username(username=username):
            companyname = get_companyname_by_username(
                username=username)['company']

        return {"response": True, "result": get_IT_by_companyname(companyname=companyname)}

    except Exception as e:
        return {"response": False, "result": "None"}


def remove_non_printable_chars(input_string):
    return ''.join(char for char in input_string if unicodedata.category(char)[0] != 'C')


def get_members_of_group(group):

    baseDN = "DC=groupe-hasnaoui,DC=local"
    searchScope = ldap.SCOPE_SUBTREE
    retrieveAttributes = ["member"]
    searchFilter = f"(&(cn={group}))"
    try:
        connection = initializeLDAPConnection(
            baseDN=baseDN, searchScope=searchScope, retrieveAttributes=retrieveAttributes, searchFilter=searchFilter)
        result = connection.search_s(
            baseDN, searchScope, searchFilter, retrieveAttributes)
        members = result[0][1]['member']
        member = [remove_non_printable_chars(mem.decode('utf8').replace("CN=", "").split(",")[0])
                  for mem in members]
        return {"members": member}
    except Exception as e:
        return {"exception : ": e}


def isAuthenticatedGSHR(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="GSHR"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


def isAuthenticatedPumaLabs(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="PUMA-LABS"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}





def isAuthenticatedHmdmFt(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="HMDM-FT"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}

def isAuthenticatedTask(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="GSHA"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}
    

def isAuthenticatedEHPHCL(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="EHPHCL"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}

def isAuthenticatedPumaImport(username, password):

    ldapserver = getReachableLDAP()
    connection = ldap.initialize(f'ldap://{ldapserver}')
    if not username or not password:
        {"response": False, "exception": "username or password not provided"}
    try:
        connection.protocol_version = ldap.VERSION3
        connection.set_option(ldap.OPT_REFERRALS, 0)
        if connection.simple_bind_s(username, password):
            userinfo = getUserInfo(username)
            if memberOf(username=username, groupname="PUMA-IMFD"):
                return {"authenticated": True, "userinfo": userinfo}
            return {"authenticated": False, "exception": "Accès refusé"}

    except Exception as error:
        if error.args[0]["desc"] == "Invalid credentials":
            exception = "Identifiants incorrects"
        elif error.args[0]["desc"] == "Can't contact LDAP server":
            exception = "Connexion au serveur AD impossible"
        else:
            exception = error.args[0]["desc"]
        return {"authenticated": False, "exception": exception}


if __name__ == "__main__":
    print(getCompanies())
    # print(getTownsbyCompany("GSHA"))
    # print(getActiveUsersbyCompany("GSHA"))
    # print(getActiveUsersbyCompanyAndTown("GSHA", "MOS"))
    # print(getDepartmentsbyCompany("GSHA"))
    # print(getActiveUsers())
    # print(isAuthenticatedCheckUp("nacereddine.boulerial@groupe-hasnaoui.com", "Azerty1234"))
    # print(isAuthenticatedGSHDocs("nacereddine.boulerial@groupe-hasnaoui.com", "Azerty1234"))
    # print(isAuthenticatedCheckUp("ct.test@groupe-hasnaoui.com", "123456"))
    # print(isAuthenticatedGSHDocs("ct.test@groupe-hasnaoui.com", "123456"))
    # print(isAuthenticatedHPM("nacereddine.boulerial@groupe-hasnaoui.com", "Azerty1234"))
    # print(isAuthenticatedHPM("ct.test@groupe-hasnaoui.com", "123456"))
    # print(isAuthenticatedHPM("bachir.belkhiri@groupe-hasnaoui.com", "Bibiche2061994"))
    # print(getDepartmentDescription("DSI"))
    # print(lockedUsers())
    # print(unlockUsers())
    # print(isLastnameUpper())
    # getUserInfo("bachir.belkhiri@groupe-hasnaoui.com")
    # getDrivers()
    # print(get_companyname_by_username("belkhiri_b"))
    # print(get_IT_by_companyname('GSHA'))
    # print(get_company_IT_by_username("benjedda_mg"))
    # print(get_members_of_group("PUMA-PRD"))
    # print(isAuthenticatedGSHDocs("Houari.DJEFFAL@grupopuma-dz.com", "AdvAdv-123"))
    # print(isAuthenticatedGSHDocs("imad.sebti@grupopuma-dz.com", "Azerty1234"))

    pass
