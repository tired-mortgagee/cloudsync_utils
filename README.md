# cloudsync_utils

This repo requires your access_token in a file called bearer.token in the local directory. Refer to the following site for instructions on how to get an client_id (refer to https://docs.netapp.com/us-en/occm/task_managing_cloud_central_accounts.html#copying-the-client-id), account_id ('Overview' page in Cloud Manager), and access_token (refer to https://docs.netapp.com/us-en/cloud-manager-automation/cm/wf_common_identity_create_user_token.html). The access_token is simply the raw ascii text of the bearer token on one line without any 'Bearer' prefix.

There are two modes of authentication, federated and non-federated, requiring some variables in the cloudsync_joblength.py script file to be updated.

Non-federated requires that the string_authtype variable is set to "non-federated", the string_account variable set to the appropriate value, the string_nonfed_user and string_nonfed_password strings set to the credentials of the Cloud Manager service account, and the string_nonfed_clientid to the appropriate value. 

Federeated requires that the string_authtype variable is set to "federated", the string_account variable set to the appropriate value, the string_fed_refreshtoken set (refer to https://services.cloud.netapp.com/refresh-token), and the string_fed_clientid to the appropriate value. 

The ./cloudsync_joblength.py script can then be run. It is written for Python 2.7.

The script deals with token refresh (when that is required), creating a new file bearer.token.old and overwriting the bearer.token file. The script will also create a file called running.jobs file and a file called completed.jobs. The completed.jobs file contains the information on job paths (source~target), the running time (in milliseconds), and the number of bytes copied in the job.

This script will only process jobs that it first sees in a RUNNING state during one script execution, and then in a DONE state during a subsequent script execution.
