from app import *
from app import ldap_funcs_test
from app import ldap_funcs
from app import mongoRead


if os.name == "nt":
    USERNAME = "achour_ar"
    PASSWORD = "AdelAchourTokenPassWord"
else:
    USERNAME = os.environ["USERNAME"]
    PASSWORD = os.environ["PASSWORD"]

# token1 = jwt.encode({"Token": "For DSI", "Username": USERNAME}, PASSWORD)

# Logging Decorator


def logging(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        value = function(*args, **kwargs)
        with open("login.log", "a") as file:
            fname = function.__name__
            time = datetime.now()
            # print(f'Function: {fname}, returned a login from: {username}, with authentication equal to: {value["authenticated"]}, at: {time}')
            file.write(
                f'Function: {fname}, authentication equal to: {value["authenticated"]}, at: {time}\n')
        return value
    return wrapper


# Logging MongoDB Decorator
def logging_mongodb(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        value = function(*args, **kwargs)

        client = MongoClient(
            f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
        db = client[MONGO_DBNAME]
        collection = db[MONGO_COLLECTIONNAME]

        functions = {"authHelpdesk": "helpdesk", "authMyCheckup": "mycheckup", "authMyDocs": "mydocs", "authMyCard": "mycard","authNewTask":"newtask",
                     "authHPM": "hpm", "authRyadcom": "ryadcom", "authQRGenerator": "qrgenerator", "authElmedina": "elmedina", "authHpsProd": "HpsProd", "authPumaPrd": "pumaprd", "authMdmCmrs": "mdmcmrs", "authPumaTrn": "pumatrn", "authGshPst": "gshpst", "authPumaLabs": "pumalabs", "authPumaImport": "pumaimport", "authHmdmFt": "hmdmft", "authEHPHCL": "EHPHCL","authTask":"TASK"}
        fname = function.__name__
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        time = now.strftime("%H:%M:%S")
        fulldate = now.strftime("%m-%d-%Y %H:%M:%S")
        partialdate = now.strftime("%m-%d-%Y")
        username = request.authorization["username"]
        # password = request.authorization["password"]

        if username != "ct.test@groupe-hasnaoui.com":

            authenticated = value["authenticated"]

            if authenticated:
                exception = "/"
            else:
                exception = value["exception"]

            date = {"fulldate": now, "partialdate": partialdate,
                    "year": year, "month": month, "day": day, "time": time}
            post = {"application": functions[fname], "date": date, "login": username,
                    "authenticated": value["authenticated"], "exception": exception}
            collection.insert_one(post)

        return value
    return wrapper


# Check for Token Decorator
def check_for_token(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Missing Token'}), 403
        try:
            data = jwt.decode(token, PASSWORD)
            # print(data)
        except:
            return jsonify({'message': 'Invalid Token'}), 403
        return function(*args, **kwargs)
    return wrapped


@app.route("/", methods=["GET"])
def index():
    # return jsonify({"Message": "Welcome to GSH LDAP API v2"})
    return "everything works "


@app.route("/get/users/disabled", methods=["GET"])
@check_for_token
def getDisabledUsers():
    return jsonify({"users": ldap_funcs.getDisabledUsers()})


@app.route("/get/users", methods=["GET"])
@check_for_token
def getUsers():
    return jsonify({"users": ldap_funcs.getActiveUsers()})


@app.route("/get/users/ad2000", methods=["GET"])
@check_for_token
def getUsersAD2000():
    return jsonify({"users": ldap_funcs.getActiveUsersAD2000()})


@app.route('/get/users/group/<string:groupname>', methods=["GET"])
@check_for_token
def getUsersOfGroup(groupname):
    return jsonify(ldap_funcs.get_members_of_group(groupname))


@app.route("/get/companies", methods=["GET"])
@check_for_token
def getCompany():
    return jsonify(ldap_funcs.getCompanies())


@app.route("/get/<string:companyname>/towns", methods=["GET"])
@check_for_token
def getCompanyTowns(companyname):
    return jsonify(ldap_funcs.getTownsbyCompany(companyname))


@app.route("/get/<string:companyname>/users", methods=["GET"])
@check_for_token
def getUsersByCompany(companyname):
    return jsonify(ldap_funcs.getActiveUsersbyCompany(companyname))


@app.route("/get/<string:companyname>/<string:townname>/users", methods=["GET"])
@check_for_token
def getUsersByCompanyAndTown(companyname, townname):
    return jsonify(ldap_funcs.getActiveUsersbyCompanyAndTown(companyname, townname))


@app.route("/get/departments", methods=["GET"])
@check_for_token
def getDeparments():
    return jsonify(ldap_funcs.getALlDepartments())


@app.route("/get/<string:department>/description", methods=["GET"])
@check_for_token
def getDeparmentDesc(department):
    return jsonify(ldap_funcs.getDepartmentDescription(department))


@app.route("/get/<string:companyname>/departments", methods=["GET"])
@check_for_token
def getDepartmentsByCompany(companyname):
    return jsonify(ldap_funcs.getDepartmentsbyCompany(companyname))


@app.route("/get/drivers", methods=["GET"])
@check_for_token
def getDrivers():
    return ldap_funcs.getDrivers()


@app.route("/get/IT/<string:username>", methods=["GET"])
@check_for_token
def getITbyUsername(username):
    return ldap_funcs.get_company_IT_by_username(username)


@app.route("/mycheckup/auth", methods=["POST"])
@logging
@logging_mongodb
def authMyCheckup():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:

            return ldap_funcs.isAuthenticatedCheckUp(username, password)
        else:
            abort(401)


@app.route("/helpdesk/auth", methods=["POST"])
@logging
@logging_mongodb
def authHelpdesk():
    if request.method != "POST":
        abort(405)

    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:
            return ldap_funcs.isAuthenticatedHelpdesk(username, password)

        else:
            abort(401)


@app.route("/mydocs/auth", methods=["POST"])
@logging
@logging_mongodb
def authMyDocs():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:
            return ldap_funcs.isAuthenticatedGSHDocs(username, password)

        else:
            abort(401)


@app.route("/mycard/auth", methods=["POST"])
@logging
@logging_mongodb
def authMyCard():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:

            return ldap_funcs.isAuthenticatedMyCard(username, password)
        else:
            abort(401)

@app.route("/newtask/auth", methods=["POST"])
@logging
@logging_mongodb
def authNewTask():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:

            return ldap_funcs.isAuthenticatedNewTask(username, password)
        else:
            abort(401)


@app.route("/ryadcom/auth", methods=["POST"])
@logging
@logging_mongodb
def authRyadcom():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:

            return ldap_funcs.isAuthenticatedRyadcom(username, password)
        else:
            abort(401)


@app.route("/elmedina/auth", methods=["POST"])
@logging
@logging_mongodb
def authElmedina():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:

            return ldap_funcs.isAuthenticatedElmedina(username, password)
        else:
            abort(401)


@app.route("/hpm/auth", methods=["POST"])
@logging
@logging_mongodb
def authHPM():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:

            return ldap_funcs.isAuthenticatedHPM(username, password)
        else:
            abort(401)



@app.route("/pumaimport/auth", methods=["POST"])
@logging
@logging_mongodb
def authPumaImport():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedPumaImport(username, password)
        else:
            abort(401)


@app.route("/qrgenerator/auth", methods=["POST"])
@logging
@logging_mongodb
def authQRGenerator():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]

        if username and password:
            return ldap_funcs.isAuthenticatedQRGenerator(username, password)
        else:
            abort(401)


@app.route("/hpsprod/auth", methods=["POST"])
@logging
@logging_mongodb
def authHpsProd():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedHpsProd(username, password)
        else:
            abort(401)


@app.route("/pumaprd/auth", methods=["POST"])
@logging
@logging_mongodb
def authPumaPrd():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedPumaPRD(username, password)
        else:
            abort(401)


@app.route("/pumatrn/auth", methods=["POST"])
@logging
@logging_mongodb
def authPumaTrn():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedPumaTRN(username, password)
        else:
            abort(401)


@app.route("/gshpst/auth", methods=["POST"])
@logging
@logging_mongodb
def authGshPst():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedGshPST(username, password)
        else:
            abort(401)


@app.route("/mdmcmrs/auth", methods=["POST"])
@logging
@logging_mongodb
def authMdmCmrs():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedMdmCmrs(username, password)
        else:
            abort(401)


@app.route("/pumalabs/auth", methods=["POST"])
@logging
@logging_mongodb
def authPumaLabs():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedPumaLabs(username, password)
        else:
            abort(401)

@app.route("/hmdmft/auth", methods=["POST"])
@logging
@logging_mongodb
def authHmdmFt():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedHmdmFt(username, password)
        else:
            abort(401)

@app.route("/task/auth", methods=["POST"])
@logging
@logging_mongodb
def authTask():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedTask(username, password)
        else:
            abort(401)          
@app.route("/ehphcl/auth", methods=["POST"])
@logging
@logging_mongodb
def authEHPHCL():
    if request.method != "POST":
        abort(405)
    if request.authorization:
        username = request.authorization["username"]
        password = request.authorization["password"]
        if username and password:
            return ldap_funcs.isAuthenticatedEHPHCL(username, password)
        else:
            abort(401)

@app.route("/get/real/managers", methods=["GET"])
def realManagers():
    return jsonify(ldap_funcs_test.realManagers())


@app.route("/get/fake/managers", methods=["GET"])
def fakeManagers():
    return jsonify(ldap_funcs_test.fakeManagers())


@app.route("/get/locked", methods=["GET"])
def lockedUsers():
    return jsonify(ldap_funcs.lockedUsers())


@app.route("/unlock", methods=["PUT"])
@check_for_token
def unlockUsers():
    if request.method != "PUT":
        abort(405)
    return jsonify(ldap_funcs.unlockUsers())


@app.route("/logs", methods=["GET"])
@check_for_token
def getLogs():
    if request.method != "GET":
        abort(405)

    print(request.args)  # For debuging
    args = request.args
    if ("token" in list(args.keys())) and len(list(args.keys())) == 1:
        return mongoRead.getAllLogs()
    else:
        if ("year" in list(args.keys())) and ("month" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 3:
            year = args['year']
            month = args['month']
            return mongoRead.getAllLogsByYearAndMonth(year, month)
        elif ("year" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 2:
            year = args['year']
            return mongoRead.getAllLogsByYear(year)
        elif ("filter" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 2:
            filter = args['filter']
            if filter == "today":
                return mongoRead.getTodayAllLogs()
            elif filter == "yesterday":
                return mongoRead.getYesterdayAllLogs()
            elif filter == "thismonth":
                return mongoRead.getThisMonthAllLogs()
            elif filter == "lastmonth":
                return mongoRead.getLastMonthAllLogs()
            elif filter == "thisyear":
                return mongoRead.getThisYearAllLogs()
            elif filter == "lastyear":
                return mongoRead.getLastYearAllLogs()
            else:
                abort(404)
        elif ("date" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 2:
            date = args['date']
            return mongoRead.getAllLogsByPartialDate(date)
        else:
            abort(404)
        # Add filters byYear, byYearAndMonth, ByPartialDate, Yesterday, LastMonth LastYear


@app.route("/logs/<string:application>", methods=["GET"])
@check_for_token
def getLogsbyApp(application):
    if request.method != "GET":
        abort(405)
    # print(request.args) # For debuging
    args = request.args
    if ("token" in list(args.keys())) and len(list(args.keys())) == 1:
        return mongoRead.getLogsbyApplication(application)
    else:
        if ("year" in list(args.keys())) and ("month" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 3:
            year = args['year']
            month = args['month']
            return mongoRead.getLogsbyApplicationAndYearAndMonth(application, year, month)
        elif ("year" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 2:
            year = args['year']
            return mongoRead.getLogsbyApplicationAndYear(application, year)
        elif ("filter" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 2:
            filter = args['filter']
            if filter == "today":
                return mongoRead.getTodayLogsbyApplication(application)
            elif filter == "yesterday":
                return mongoRead.getYesterdayLogsbyApplication(application)
            elif filter == "thismonth":
                return mongoRead.getThisMonthLogsbyApplication(application)
            elif filter == "lastmonth":
                return mongoRead.getLastMonthLogsbyApplication(application)
            elif filter == "thisyear":
                return mongoRead.getThisYearLogsbyApplication(application)
            elif filter == "lastyear":
                return mongoRead.getLastYearLogsbyApplication(application)
            else:
                abort(404)
        elif ("date" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 2:
            date = args['date']
            return mongoRead.getLogsbyApplicationAndPartialDate(application, date)
        else:
            abort(404)


@app.route("/logs/apps", methods=["GET"])
@check_for_token
def getLogsApps():
    if request.method != "GET":
        abort(405)
    return mongoRead.getApplications()


@app.route("/logs/<string:application>/graph", methods=["GET"])
@check_for_token
def getNumberOfLogsbyApp(application):
    if request.method != "GET":
        abort(405)
    # print(request.args) # For debuging
    args = request.args
    if ("token" in list(args.keys())) and len(list(args.keys())) == 1:
        return mongoRead.getLogsbyApplication(application)
    else:
        if ("year" in list(args.keys())) and ("month" in list(args.keys())) and ("token" in list(args.keys())) and len(list(args.keys())) == 3:
            year = args['year']
            month = args['month']
            return mongoRead.getNumberOfLogsbyApplicationAndYearAndMonth(application, year, month)
        else:
            abort(404)


@app.errorhandler(401)
def unauthorized(e):
    return jsonify(error=str(e))


@app.errorhandler(403)
def forbidden(e):
    return jsonify(error=str(e))


@app.errorhandler(404)
def not_found(e):
    return jsonify(error=str(e))


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify(error=str(e))
