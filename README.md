# WhatsApp chat statistic

WhatsApp statistic utility script written in python3

Usage: *wastat.py configfile chatfile*

chatfile - You can download char archive from mobile WhatsApp client

## Config file

```json
{
  "groupInterval": 15,  
  "lowMessageLimit": 200, 
  "nameMapping": [ 
    {"ident": "+1 237 555-55-55", "alias": "My friend"},
    ...
  ]
}
```

`groupInterval` - Group consecutive messages if written within this interval. 0 - disabled grouping

`lowMessageLimit` - Drop users from a graph with messages less then that. 0 - No drop.

`nameMapping`  - Mapping for chat participants. Maps `ident` to `alias`
