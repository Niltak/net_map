# net_map

##### Example:
```python
from net_map import net_map


net_map(
    '10.10.10.10',      # Target switch's IP or hostname
    'cisco_user',       # Username
    site_code='test',   # Site name
    debug=True          # Will generate a debug file
)
```

##### Outputs:
Will generate the following folders and files.

*site_info/test/test.yml* -> Used as a database of switches for the site
```yaml
Switchlist:
- hostname: test-sw-c2960x-01
  host: 10.10.10.10
  groups:
  - EXAMPLE_PCS_BUSINESS
  - test
  neighbor:
  - destination_host: test-sw-c2960x-02
    local_port: GigabitEthernet1/0/51
  - destination_host: test-sw-c4451x-01
    local_port: GigabitEthernet2/0/25
  - destination_host: test-sw-c4451x-01
    local_port: GigabitEthernet1/0/49
  data:
    location: EXAMPLE_DEPARTMENT
    role: EXAMPLE_CSW_DSW_ASW
    device_type: cisco_ios
- hostname: test-sw-c2960x-02
  host: 10.10.10.11
  groups:
  - EXAMPLE_PCS_BUSINESS
  - test
  neighbor:
  - destination_host: test-sw-c2960x-01
    local_port: GigabitEthernet1/0/25
  data:
    location: EXAMPLE_DEPARTMENT
    role: EXAMPLE_CSW_DSW_ASW
    device_type: cisco_ios
- hostname: test-sw-c4451x-01
  host: 10.10.10.12
  groups:
  - EXAMPLE_PCS_BUSINESS
  - test
  neighbor:
  - destination_host: test-sw-c2960x-01
    local_port: GigabitEthernet0/0/2
  - destination_host: test-sw-c2960x-01
    local_port: GigabitEthernet0/0/1
  - destination_host: FOB3B-1
    local_port: GigabitEthernet0/0/0
  data:
    location: EXAMPLE_DEPARTMENT
    role: EXAMPLE_CSW_DSW_ASW
    device_type: cisco_ios
Ignorelist: null
```


*site_info/test/test_cyto.json* -> Used in cyto_map_server to create physical map
```json
{
 "data": [],
 "directed": false,
 "multigraph": false,
 "elements": {
  "nodes": [
   {
    "data": {
     "id": "test-sw-c2960x-01",
     "label": "test-sw-c2960x-01"
    }
   },
   {
    "data": {
     "id": "test-sw-c2960x-02",
     "label": "test-sw-c2960x-02"
    }
   },
   {
    "data": {
     "id": "test-sw-c4451x-01",
     "label": "test-sw-c4451x-01"
    }
   },
   {
    "data": {
     "id": "FOB3B-1",
     "label": "FOB3B-1"
    }
   }
  ],
  "edges": [
   {
    "data": {
     "source": "test-sw-c2960x-01",
     "target": "test-sw-c2960x-02"
    }
   },
   {
    "data": {
     "source": "test-sw-c2960x-01",
     "target": "test-sw-c4451x-01"
    }
   },
   {
    "data": {
     "source": "test-sw-c4451x-01",
     "target": "FOB3B-1"
    }
   }
  ]
 }
}
```


*site_info/test/test_debug.yml* -> Used in debugging switch connections
```yaml
detected:
- host: 10.10.10.10
  hostname: indy-esk-c2960x-01
- host: 10.10.10.11
  hostname: indy-esk-c2960x-02
- host: 10.10.10.12
  hostname: indy-esk-c4451x-01
- host: 10.10.20.13
  hostname: FOB3B-1
cdp:
- hostname: test-sw-c2960x-01
  host: 10.10.10.10
  groups:
  - EXAMPLE_PCS_BUSINESS
  - test
  neighbor:
  - destination_host: test-sw-c2960x-02
    local_port: GigabitEthernet1/0/51
  - destination_host: test-sw-c4451x-01
    local_port: GigabitEthernet2/0/25
  - destination_host: test-sw-c4451x-01
    local_port: GigabitEthernet1/0/49
  data:
    location: EXAMPLE_DEPARTMENT
    role: EXAMPLE_CSW_DSW_ASW
    device_type: cisco_ios
- hostname: test-sw-c2960x-02
  host: 10.10.10.11
  groups:
  - EXAMPLE_PCS_BUSINESS
  - test
  neighbor:
  - destination_host: test-sw-c2960x-01
    local_port: GigabitEthernet1/0/25
  data:
    location: EXAMPLE_DEPARTMENT
    role: EXAMPLE_CSW_DSW_ASW
    device_type: cisco_ios
- hostname: test-sw-c4451x-01
  host: 10.10.10.12
  groups:
  - EXAMPLE_PCS_BUSINESS
  - test
  neighbor:
  - destination_host: test-sw-c2960x-01
    local_port: GigabitEthernet0/0/2
  - destination_host: test-sw-c2960x-01
    local_port: GigabitEthernet0/0/1
  - destination_host: FOB3B-1
    local_port: GigabitEthernet0/0/0
  data:
    location: EXAMPLE_DEPARTMENT
    role: EXAMPLE_CSW_DSW_ASW
    device_type: cisco_ios
errored:
- name: false
  hostname: FOB3B-1
  host: 10.20.10.13
```
