#!/usr/bin/python2.7

import sys
import requests
from shutil import copyfile

##############################
# variables

bool_debug = False
string_authtype = "non-federated"
string_url = "https://api.cloudsync.netapp.com/api/relationships-v2"
string_account = "account-xyzxyzxy"
string_fed_refreshtoken = ""
string_fed_clientid = ""
string_nonfed_password = ""
string_nonfed_user = ""
string_nonfed_clientid = ""

url_refresh = "https://netapp-cloud-account.auth0.com/oauth/token"
url_relationships = "https://api.cloudsync.netapp.com/api/relationships-v2"

##############################
# main

# read bearer token from local file
with open("./bearer.token") as handle_file:
    list_lines = handle_file.readlines()
handle_file.close()
if len(list_lines) != 1:
    print "unexpected number of lines in file bearer.token"
    sys.exit(1)
string_token = str(list_lines[0]).strip()

# construct headers for request to Cloud Sync service
json_headers = {'x-account-id': string_account, 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + string_token}
if bool_debug:
    print "debug: header json == " + str(json_headers)

# send request for relationships info to Cloud Sync service
obj_response = requests.get(url_relationships, headers=json_headers)
if bool_debug:
    print "debug: requests return json == " + obj_response.text

# check to see of the token expired and refresh if neccessary
if obj_response.status_code == 401 and "TokenExpiredError" in obj_response.json()["message"]:
    if bool_debug:
        print "debug: initial request to Cloud Sync service requires bearer token refresh"

    # construct json payload for refresh post for federated user authentication to Cloud Sync
    if string_authtype == "federated":
        json_refreshheaders = {'Content-Type': 'application/json'}
        json_refreshdata = {'grant_type': 'refresh_token', 'refresh_token': string_fed_refreshtoken, 'client_id': string_fed_clientid}
    # construct json payload for refresh post for non-federated user authentication to Cloud Sync
    elif string_authtype == "nonfederated" or string_authtype == "non-federated" or string_authtype == "non federated":
        json_refreshheaders = {'Content-Type': 'application/json'}
        json_refreshdata = {'username': string_nonfed_user, 'scope': 'openid profile', 'audience': 'https://api.cloud.netapp.com', 'client_id': string_nonfed_clientid, 'grant_type': 'p
assword', 'password': string_nonfed_password, 'Realm': 'Username-Password-Authentication'}
    # unrecognised authtype string
    else:
        print("unrecognised authtype string, please update variables at the top of the script file")
        sys.exit(1)

    # send post request to refresh token
    obj_response = requests.post(url_refresh, headers=json_refreshheaders, json=json_refreshdata)

    # barf if refresh fails
    if obj_response.status_code != 200:
        print "problem refreshing token for federated cloud manager user: response code " + str(obj_response.status_code)
        sys.exit(1)
    if bool_debug:
        print "debug: refresh requests return json == " + obj_response.text

    # copy the old token file and store the new token
    copyfile("./bearer.token", "./bearer.token.old")
    with open("./bearer.token", "w") as handle_file:
        handle_file.write(obj_response.json()["access_token"])
    handle_file.close()

    # repeat request for relationships info to Cloud Sync service with new token
    obj_response = requests.get(url_relationships, headers=json_headers)
    if bool_debug:
        print "debug: requests return json == " + obj_response.text

print obj_response.text

# read previously running relationships from file
with open("./running.jobs") as handle_file:
    list_lines = handle_file.readlines()
handle_file.close()
dict_runningjobs = {}
for string_line in list_lines:
    dict_runningjobs[string_line.split(",")[0].strip()] = string_line.split(",")[1].strip()
print dict_runningjobs

# check for recently completed jobs
list_completedjobs = []
for obj_sync in obj_response.json():
    string_sync = str(obj_sync["source"]["nfs"]["host"]) + str(obj_sync["source"]["nfs"]["export"]) + \
            "~" + str(obj_sync["target"]["nfs"]["host"]) + str(obj_sync["target"]["nfs"]["export"])
    print string_sync

    # job was previously seen in the running state
    if string_sync in dict_runningjobs.keys():
        # pop the job from the runningjobs dictionary and save the stats
        if obj_sync["activity"]["status"] == "DONE":
            dict_runningjobs.pop(string_sync, None)
            list_completedjobs.append(string_sync + "," + str(obj_sync["activity"]["executionTime"]) + "," + \
                    str(obj_sync["activity"]["bytesCopied"]) + "\n")

    # new job that is still running, add it to the list of running jobs
    elif obj_sync["activity"]["status"] == "RUNNING":
        dict_runningjobs[string_sync] = obj_sync["activity"]["startTime"]

# write out the list of currently running jobs
with open("./running.jobs", "w") as handle_file:
    for string_sync in dict_runningjobs.keys():
        handle_file.write(str(string_sync + "," + dict_runningjobs[string_sync]))
handle_file.close()

# write out the list of completed jobs
with open("./completed.jobs", "a") as handle_file:
    for string_job in list_completedjobs:
        handle_file.write(str(string_job))
handle_file.close()
