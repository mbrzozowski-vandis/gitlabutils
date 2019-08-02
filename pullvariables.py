import json
import requests
from csv import DictWriter

projectid=''
privatetoken = ''

requesturl='https://gitlab.com/api/v4/projects/' + projectid + '/variables'

finaloutput = []

curpage=1


authheader = {'PRIVATE-TOKEN': privatetoken}
params = {'per_page': '100','page': curpage}
response = requests.get(requesturl, headers=authheader, params=params)

numpages=response.headers['X-Total-Pages']
numpages=int(numpages)

for curpage in range(1, numpages + 1):
   params['page'] = curpage
   response = requests.get(requesturl, headers=authheader, params=params)
   tempoutput = response.json()
   finaloutput = finaloutput + tempoutput

#with open('variables', 'w') as outfile:
#    json.dump(json.dumps(finaloutput), outfile)

#outfile.close()


csvOutput = open("variables.csv", "w")
writer = DictWriter(csvOutput, finaloutput[0].keys())
writer.writeheader()
writer.writerows(finaloutput)
csvOutput.close()
