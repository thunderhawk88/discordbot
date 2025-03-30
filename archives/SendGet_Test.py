import discord,pathlib,random,datetime,json,os,subprocess,calendar,requests,csv,time

class Set_Error():
    def __init__(self, _statuscode, _result = None, _reason = None):
        self.statuscode_ = _statuscode
        self.result_ = _result
        self.reason_ = _reason

    def __str__(self):
        return "{\"statud_code\":\"" + str(self.statuscode_) + "\", \"result\":\"" + str(self.result_) + "\", \"reason\":\"" + str(self.reason_) + "\"}"
    
    def SetStatuscode(self,_statuscode):
        self.statuscode_ = _statuscode
        return self.statuscode_

    def SetReason(self,_reason):
        self.reason_ = _reason
        return self.reason_
    
    def SetReason(self,_result):
        self.result_ = _result
        return self.reason_
    
    @property
    def status_code(self):
        return self.statuscode_
    
    @property
    def result(self):
        return self.result_

    @property
    def reason(self):
        return self.reason_


def SendGet(_baseURL,_endpoint,_headers):
    _URI = str(_baseURL) + str(_endpoint)

    try:
        _response = _session.get(url = _URI, headers = _headers)
    except requests.exceptions.HTTPError as e:
        _response = Set_Error(999,"Error","[HTTPError] API failed. URI = " + str(_URI) + ". Reason: " + e.args[0])
        print(_response.reason)
        return _response
    except requests.exceptions.ReadTimeout as e:
        _response = Set_Error(999,"Error","[Timed Out] API failed. URI = " + str(_URI) + "")
        print(_response.reason)
        return _response
    except requests.exceptions.MissingSchema as e:
        _response = Set_Error(999,"Error","[MissingSchema] API failed. URI = " + str(_URI) + "")
        print(_response.reason)
        return _response
    except requests.exceptions.ConnectionError as e:
        _response = Set_Error(999,"Error","[ConnectionError] API failed. URI = " + str(_URI))
        print(_response.reason)
        return _response
    except requests.exceptions.RequestException as e:
        _response = Set_Error(999,"Error","[RequestException] API failed. URI = " + str(_URI) + "")
        print(_response.reason)
        return _response
    return _response.json()

##########################

_session = requests.Session()

baseURL= "https://api.mangadex.or"
endpoint = "/manga?limit=" + str(24) + "&order%5BfollowedCount%5D=desc"

result = SendGet(baseURL,endpoint,None)

if result.result == 'ok':
    print(result)
else:
    print(result.result)
    print(result.reason)
