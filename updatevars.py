import json
import requests
import pandas as pd
import gitlab

projectid=''
privatetoken=''
inputfile=''

def getvar(json,name,env):
  for entry in json:
     if name == entry['key'] and env == entry['environment_scope']:
        return entry

def updatevar(projectid,authkey,name,env,value,protected):
    authheader = {'PRIVATE-TOKEN': authkey}
    params = {'value': value, 'protected': protected, 'environment_scope': env }
    requesturl = 'https://gitlab.com/api/v4/projects/' + projectid + '/variables/' + name

    response = None
    try:
        response = requests.put(requesturl, headers=authheader, data=params)
        if response.status_code != 200:
            print(response.text)
            raise Exception('Recieved non 200 response while sending response to CFN.')
        return

    except requests.exceptions.RequestException as e:
        if req != None:
            print(req.text)
        print(e)
        raise 

def createvar(projectid,authkey,name,env,value,protected):
    authheader = {'PRIVATE-TOKEN': authkey}
    params = {'key': name, 'value': value, 'protected': protected, 'environment_scope': env }
    requesturl = 'https://gitlab.com/api/v4/projects/' + projectid + '/variables'

    response = None
    try:
        response = requests.post(requesturl, headers=authheader,params=params)
        if response.status_code != 200 and response.status_code != 201:
            print(response.text)
            raise Exception('Recieved non 200/201 response while sending response to CFN.')
        return

    except requests.exceptions.RequestException as e:
        if req != None:
            print(req.text)
        print(e)
        raise 

def deletevar(projectid,authkey,name):
    authheader = {'PRIVATE-TOKEN': authkey}
    requesturl = 'https://gitlab.com/api/v4/projects/' + projectid + '/variables/' + name

    response = None
    try:
        response = requests.delete(requesturl, headers=authheader)

        while response.status_code == 204:
            response = requests.delete(requesturl, headers=authheader)

        if response.status_code != 204 and response.status_code != 404:
            print(response.text)
            raise Exception('Recieved non 204/404 response while trying to delete')
        return

    except requests.exceptions.RequestException as e:
        if req != None:
            print(req.text)
        print(e)
        raise 

authheader = {'PRIVATE-TOKEN': privatetoken}
params = {'per_page': '100'}
requesturl = 'https://gitlab.com/api/v4/projects/' + projectid + '/variables'

response = requests.get(requesturl, headers=authheader, params=params)

numpages=response.headers['X-Total-Pages']
numpages=int(numpages)

curpage=1
currentvarsjson = []

for curpage in range(1, numpages + 1):
   params['page'] = curpage
   response = requests.get(requesturl, headers=authheader, params=params)
   tempoutput = response.json()
   currentvarsjson = currentvarsjson + tempoutput

newvarsfile=pd.read_csv(inputfile,index_col=0,usecols=["key","environment_scope","protected","masked","variable_type","value"])
tempjson=json.loads(newvarsfile.to_json(orient="table"))
newvarsjson = json.loads(json.dumps(tempjson['data']))

varsnoactionctr = 0
varsupdatectr = 0
varscreatectr = 0
varsdelctr = 0
varssuccessctr = 0
varserrorctr = 0

varstoupdate = []
varstodelete = []

for newvar in newvarsjson:
    newvarname = None
    newvarvalue = None
    newvarenv = None
    newvarprotect = None

    newvarname = newvar['key']
    newvarvalue = newvar['value']
    newvarenv = newvar['environment_scope']
    newvarprotect = newvar['protected']

    if newvarvalue is None:
        newvarvalue = 'null'

    currentvar = getvar(currentvarsjson,newvarname,newvarenv)

    if currentvar is not None:
        if currentvar['value'] == newvarvalue:
            if currentvar['protected'] != newvarprotect:
                output = 'Env variable ' + newvarname + ' / ' + newvarenv + ' protection will be updated. Must delete and recreate'
                varsupdatectr = varsupdatectr + 1
                print output
                #deletevar(projectid,privatetoken,newvarname)
                varstoupdate.append(newvarname)
                #updatevar(projectid,privatetoken,newvarname,newvarenv,newvarvalue,newvarprotect)
                #varsupdatectr = varsupdatectr + 1
            else:
                output = 'Env variable ' + newvarname + ' / ' + newvarenv + ' needs no update.'
                #print output
                varsnoactionctr = varsnoactionctr + 1
        else:
            output = 'Env variable ' + newvarname + ' / ' + newvarenv + ' will be updated.'
            print output
            varsupdatectr = varsupdatectr + 1
    else:
        output = 'Env variable ' + newvarname + ' / ' + newvarenv + ' will be created.'
        print output
        createvar(projectid,privatetoken,newvarname,newvarenv,newvarvalue,newvarprotect)
        varscreatectr = varscreatectr + 1

print 'Variables created: ' + str(varscreatectr)
print 'Variables updated: ' + str(varsupdatectr)
print 'Variables deleted: ' + str(varsdelctr)
print 'Variables no action taken ' + str(varsnoactionctr)
            

