# Netapp_AutoBackup

!!! ### All **3** .py files must be copied ### !!!


### Before you start ###
Create **secret.json** with following format:
```
{
  "account": <Your Account>,
  "password": <Your Password>
}
```


usage:

take_snapshot.py
```
python3 take_snapshot.py -c <cluster> -f <path_to_secret.json> -n <full_volume_name>
```
