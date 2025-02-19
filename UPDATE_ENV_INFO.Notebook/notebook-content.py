# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "b726adfa-518b-4fad-9ae3-2250b9b95ecf",
# META       "default_lakehouse_name": "DE_LH_RAW",
# META       "default_lakehouse_workspace_id": "cf6b9fab-9075-4a96-9da7-cdd8f4007577"
# META     },
# META     "warehouse": {}
# META   }
# META }

# CELL ********************

import sempy.fabric as fabric
client = fabric.FabricRestClient()
workspaceId = fabric.get_workspace_id()
print("workspaceId : " , workspaceId)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

pbi_token = mssparkutils.credentials.getToken('https://analysis.windows.net/powerbi/api') 


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import requests
url = f'https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items'


headers = {
    'Authorization': f'Bearer {pbi_token}',
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers)
hm = {"workspaceId" :workspaceId }
if response.status_code == 200:
    items = response.json()['value']
    for item in items:
        if not hm.get(item['type'])  :
            hm[item['type']] = {item['displayName'] : item['id']}
        else :
            hm[item['type']][item['displayName']] = item['id']
else:
    print(f"Failed to retrieve datasets. Status Code: {response.status_code}, Response: {response.text}")

df = spark.createDataFrame([hm])
df.write.mode("overwrite").format('json').save('Files/env_info.json')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
