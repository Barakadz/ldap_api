from pymongo import MongoClient
from datetime import datetime, timedelta
from calendar import monthrange, month_name
import time

MONGO_HOST = "10.10.10.20"
MONGO_DBUSER = "mongoadmin"
MONGO_DBPASS = "mongopass"
MONGO_DBNAME = "API_LDAP"
MONGO_COLLECTIONNAME_APPS = "applications"
MONGO_COLLECTIONNAME_LOGS = "logs"


def addApplications():
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_APPS]

    functions = ["Helpdesk",
                 "MyCheckup",
                 "MyDocs",
                 "MyCard",
                 "HPM",
                 "QRGenerator",
                 "HpsProd",
                 "pumaprd",
                 "pumalabs","pumaimport","hmdmft"]
    for f in functions:
        post = {"name": f, "code": f.lower()}
        collection.insert_one(post)


def getApplications():
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_APPS]

    query = {}

    results = collection.find(query, {"_id": 0})

    if results.count() == 0:
        return {"applications": False, "exception": "No application available"}

    list = []
    for result in results:
        list.append(result)

    return {"applications": True, "count": len(list), "result": list}


# All Logs Functions
def getAllLogs():
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {}

    results = collection.find(query, {"_id": 0})

    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No logs available"}

    list = []
    for result in results:
        list.append(result)

    return {"logs": True, "count": len(list), "result": list[::-1]}


def getAllLogsByPartialDate(partialdate):
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {"date.partialdate": partialdate}

    results = collection.find(query, {"_id": 0})
    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No logs available"}

    list = []
    for result in results:
        list.append(result)

    return {"logs": True, "count": len(list), "result": list[::-1]}


def getAllLogsByYear(year):
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {"date.year": year}

    results = collection.find(query, {"_id": 0})
    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No logs available"}

    list = []
    for result in results:
        list.append(result)

    return {"logs": True, "count": len(list), "result": list[::-1]}


def getAllLogsByYearAndMonth(year, month):
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {"date.year": year, "date.month": month}

    results = collection.find(query, {"_id": 0})
    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No logs available"}

    list = []
    for result in results:
        list.append(result)

    return {"logs": True, "count": len(list), "result": list[::-1]}


# Filtered Logs Functions
def getLogsbyApplication(application):
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {"application": application}

    results = collection.find(query, {"_id": 0})
    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No such application"}

    list = []
    for result in results:
        list.append(result)

    return {"logs": True, "count": len(list), "result": list[::-1]}


def getLogsbyApplicationAndPartialDate(application, partialdate):
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {"application": application, "date.partialdate": partialdate}

    results = collection.find(query, {"_id": 0})
    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No such application"}

    list = []
    for result in results:
        list.append(result)

    return {"logs": True, "count": len(list), "result": list[::-1]}


def getLogsbyApplicationAndYear(application, year):
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {"application": application, "date.year": year}

    results = collection.find(query, {"_id": 0})
    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No such application"}

    list = []
    for result in results:
        list.append(result)

    return {"logs": True, "count": len(list), "result": list[::-1]}


def getLogsbyApplicationAndYearAndMonth(application, year, month):
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {"application": application,
             "date.year": year, "date.month": month}

    results = collection.find(query, {"_id": 0})
    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No such application"}

    list = []
    for result in results:
        list.append(result)

    return {"logs": True, "count": len(list), "result": list[::-1]}


# Special Logs Functions
def getTodayAllLogs():
    today = datetime.now()
    today = today.strftime('%m-%d-%Y')
    # print(today) # For Debuging
    return getAllLogsByPartialDate(today)


def getTodayLogsbyApplication(application):
    today = datetime.now()
    today = today.strftime('%m-%d-%Y')
    # print(today) # For Debuging
    return getLogsbyApplicationAndPartialDate(application, today)


def getYesterdayAllLogs():
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.strftime('%m-%d-%Y')
    # print(yesterday) # For Debuging
    return getAllLogsByPartialDate(yesterday)


def getYesterdayLogsbyApplication(application):
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.strftime('%m-%d-%Y')
    # print(yesterday) # For Debuging
    return getLogsbyApplicationAndPartialDate(application, yesterday)


def getThisMonthAllLogs():
    month = time.strftime('%m')
    year = time.strftime('%Y')
    # print(month+"-"+year) # For Debuging
    return getAllLogsByYearAndMonth(year, month)


def getThisMonthLogsbyApplication(application):
    month = time.strftime('%m')
    year = time.strftime('%Y')
    # print(month+"-"+year) # For Debuging
    return getLogsbyApplicationAndYearAndMonth(application, year, month)


def getLastMonthAllLogs():
    month = time.strftime('%m')
    year = time.strftime('%Y')
    if int(month) == 1:
        month = '12'
    else:
        if int(month) <= 10:
            month = '0'+str(int(month) - 1)
        else:
            month = str(int(month) - 1)

    # print(month+"-"+year) # For Debuging
    return getAllLogsByYearAndMonth(year, month)


def getLastMonthLogsbyApplication(application):
    month = time.strftime('%m')
    year = time.strftime('%Y')
    if int(month) == 1:
        month = '12'
    else:
        if int(month) <= 10:
            month = '0'+str(int(month) - 1)
        else:
            month = str(int(month) - 1)

    # print(month+"-"+year) # For Debuging
    return getLogsbyApplicationAndYearAndMonth(application, year, month)


def getThisYearAllLogs():
    year = str(time.strftime('%Y'))
    # print(year) # For Debuging
    return getAllLogsByYear(year)


def getThisYearLogsbyApplication(application):
    year = str(time.strftime('%Y'))
    # print(year) # For Debuging
    return getLogsbyApplicationAndYear(application, year)


def getLastYearAllLogs():
    year = str(int(time.strftime('%Y')) - 1)
    # print(year) # For Debuging
    return getAllLogsByYear(year)


def getLastYearLogsbyApplication(application):
    year = str(int(time.strftime('%Y')) - 1)
    # print(year) # For Debuging
    return getLogsbyApplicationAndYear(application, year)


# Graph Functions
def getNumberOfLogsbyApplicationAndYearAndMonth(application, year, month):

    try:
        NUMBER_OF_DAYS_IN_MONTH = monthrange(int(year), int(month))[1]
    except:
        return {"logs": False, "exception": f"Error in year: {year} or month: {month}"}
    # Set Mongo Connection
    client = MongoClient(
        f"mongodb://{MONGO_DBUSER}:{MONGO_DBPASS}@{MONGO_HOST}")
    # Get Database
    db = client[MONGO_DBNAME]
    # Get Collection
    collection = db[MONGO_COLLECTIONNAME_LOGS]

    query = {"application": application,
             "date.year": year, "date.month": month}

    results = collection.find(query, {"_id": 0, "date.fulldate": 0, "date.partialdate": 0,
                              "date.time": 0, "login": 0, "authenticated": 0, "exception": 0})
    # print(results.count()) # For debuging
    if results.count() == 0:
        return {"logs": False, "exception": "No such application"}

    list = []
    dict = {}
    for result in results:
        list.append(result)

    for i in range(1, NUMBER_OF_DAYS_IN_MONTH+1):
        count = 0
        for entry in list:
            if str(i).zfill(2) == entry['date']['day']:
                count += 1
        dict[i] = count

    # To return MONTH_TXT in French
    # import locale
    # locale.setlocale(locale.LC_ALL, 'fr_FR')
    MONTH_TXT = month_name[int(month)]

    APPLICATION = db[MONGO_COLLECTIONNAME_APPS].find_one(
        {"code": application}, {"_id": 0, "code": 0, "desc": 0})["name"]

    return {"logs": True, "application": APPLICATION, "month": month, "monthtxt": MONTH_TXT, "year": year, "start": 1, "end": NUMBER_OF_DAYS_IN_MONTH,  "totalcount": len(list), "result": dict}


if __name__ == "__main__":
    # print(getApplications())
    # addApplications()

    # getAllLogs()
    # getAllLogsByYear("2019")
    # getAllLogsByMonth("04")
    # getLogsbyApplication("mycard")
    # getLogsbyApplicationAndYear("helpdesk", "2019")
    # getLogsbyApplicationAndYearAndMonth("helpdesk", "2021", "05")
    # getAllLogsByPartialDate("05-01-2021")
    # getLogsbyApplicationAndPartialDate("helpdesk", "05-01-2021")

    # print(getYesterdayAllLogs())
    # print(getYesterdayLogsbyApplication("helpdesk"))
    # print(getLastMonthAllLogs())
    # print(getLastMonthLogsbyApplication("helpdesk"))
    # print(getLastYearAllLogs())
    # print(getLastYearLogsbyApplication("helpdesk"))

    # print(getNumberOfLogsbyApplicationAndYearAndMonth("helpdesk", "2021", "04"))
    pass
