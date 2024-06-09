from base64 import b64encode

try:
    from run import app
    import unittest
    
except Exception as e:
    print(f"Some modules ar missing {e}")

class FlaskTest(unittest.TestCase):

    ## GET /
    #Check for response 200
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_index_content(self):
        tester = app.test_client(self)
        response = tester.get("/")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_index_data(self):
        tester = app.test_client(self)
        response = tester.get("/")
        self.assertTrue(b"GSH LDAP API" in response.data)

    ## GET /get/users
    #Check for response 200
    def test_getUsers(self):
        tester = app.test_client(self)
        response = tester.get("/get/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_getUsers_content(self):
        tester = app.test_client(self)
        response = tester.get("/get/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_index_data(self):
        tester = app.test_client(self)
        response = tester.get("/get/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertTrue(b"users" in response.data)

    ## GET /get/companies
    #Check for response 200
    def test_getCompany(self):
        tester = app.test_client(self)
        response = tester.get("/get/companies?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_getCompany_content(self):
        tester = app.test_client(self)
        response = tester.get("/get/companies?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_getCompany_data(self):
        tester = app.test_client(self)
        response = tester.get("/get/companies?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertTrue(b"GSHA" in response.data)

    ## GET /get/<filiale>/users
    #Check for response 200
    def test_getUsersByCompany(self):
        tester = app.test_client(self)
        response = tester.get("/get/GSHA/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_getUsersByCompany_content(self):
        tester = app.test_client(self)
        response = tester.get("/get/GSHA/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_getUsersByCompany_data(self):
        tester = app.test_client(self)
        response = tester.get("/get/GSHA/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertTrue(b"fullname" in response.data)

    ## GET /get/departments
    #Check for response 200
    def test_getDeparments(self):
        tester = app.test_client(self)
        response = tester.get("/get/departments?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_getDeparments_content(self):
        tester = app.test_client(self)
        response = tester.get("/get/departments?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_getDeparments_data(self):
        tester = app.test_client(self)
        response = tester.get("/get/departments?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertTrue(b"departments" in response.data)

    ## POST /mycheckup/auth
    #Check for response 200
    def test_authMyCheckup(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/mycheckup/auth", headers={"Authorization": f"Basic {credentials}"})
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_authMyCheckup_content(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/mycheckup/auth", headers={"Authorization": f"Basic {credentials}"})
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_authMyCheckup_data(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/mycheckup/auth", headers={"Authorization": f"Basic {credentials}"})
        self.assertTrue(b'"authenticated":true' in response.data)

    ## POST /helpdesk/auth
    #Check for response 200
    def test_authHelpdesk(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/helpdesk/auth", headers={"Authorization": f"Basic {credentials}"})
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_authHelpdesk_content(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/helpdesk/auth", headers={"Authorization": f"Basic {credentials}"})
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_authHelpdesk_data(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/helpdesk/auth", headers={"Authorization": f"Basic {credentials}"})
        self.assertTrue(b'"authenticated":true' in response.data)
		
    ## POST /mydocs/auth
    #Check for response 200
    def test_authMyDocs(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/mydocs/auth", headers={"Authorization": f"Basic {credentials}"})
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_authMyDocs_content(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/mydocs/auth", headers={"Authorization": f"Basic {credentials}"})
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_authMyDocs_data(self):
        tester = app.test_client(self)
        credentials = b64encode(b"ct.test@groupe-hasnaoui.com:123456").decode('utf-8')
        response = tester.post("/mydocs/auth", headers={"Authorization": f"Basic {credentials}"})
        self.assertTrue(b'"authenticated":true' in response.data)

    ## POST /logs
    #Check for response 200
    def test_getLogs(self):
        tester = app.test_client(self)
        response = tester.get("/logs?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_getLogs_content(self):
        tester = app.test_client(self)
        response = tester.get("/logs?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_get_data(self):
        tester = app.test_client(self)
        response = tester.get("/logs?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertTrue(b'authenticated' in response.data)

    ## POST /get/locked
    #Check for response 200
    def test_getLocked(self):
        tester = app.test_client(self)
        response = tester.get("/get/locked")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_getLocked_content(self):
        tester = app.test_client(self)
        response = tester.get("/get/locked")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_getLocked_data(self):
        tester = app.test_client(self)
        response = tester.get("/get/locked")
        self.assertTrue(b'locked' in response.data)

    ## POST /unlock
    #Check for response 200
    def test_PutUnlock(self):
        tester = app.test_client(self)
        response = tester.put("/unlock?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_PutUnlock_content(self):
        tester = app.test_client(self)
        response = tester.put("/unlock?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_PutUnlock_data(self):
        tester = app.test_client(self)
        response = tester.put("/unlock?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertTrue(b'unlocked' in response.data)


    ## GET /logs/helpdesk
    #Check for response 200
    def test_getLogsHelpdesk(self):
        tester = app.test_client(self)
        response = tester.get("/logs/helpdesk?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_getLogsHelpdesk_content(self):
        tester = app.test_client(self)
        response = tester.get("/logs/helpdesk?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_getHelpdesk_data(self):
        tester = app.test_client(self)
        response = tester.get("/logs/helpdesk?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertTrue(b'true' in response.data)

    ## GET /logs/error
    #Check for response 200
    def test_getLogsError(self):
        tester = app.test_client(self)
        response = tester.get("/logs/error?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #Check if content return application/json
    def test_getLogsError_content(self):
        tester = app.test_client(self)
        response = tester.get("/logs/error?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertEqual(response.content_type, "application/json") #or html/text

    #Check for data returned
    def test_getError_data(self):
        tester = app.test_client(self)
        response = tester.get("/logs/error?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE")
        self.assertTrue(b'No such application' in response.data)

if __name__ == '__main__':
    unittest.main()