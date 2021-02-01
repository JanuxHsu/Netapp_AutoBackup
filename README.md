# Netapp_AutoBackup

### Before you start ###
Create **secret.json** with following format:
```
{
  "account": <Your Account>,
  "password": <Your Password>
}
```


usage:

volume_finder.py
```
python3 volume_finder.py -c <cluster> -f <path_to_secret.json>
```
This program create a json file that contains all the volume information of the cluster.
Keep only the volumes you wish to preform auto-snapshot by the below program.


volume_snapshot_trigger.py
```
python3 volume_snapshot_trigger.py -c <cluster> -f <path_to_secret.json> -i <path_to_volumes.json>
```
Above command will trigger the snapshot creation according the **-i <path_to_volumes.json>**
