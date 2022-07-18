import logging
import nil_lib as ks


def site_yaml_compare(site_code) -> None:
    '''
    Compares existing site yaml file with a newly created site yaml file.
    Creates a file dividing switch updates, adds, and removes.
    '''
    site_yaml = ks.file_loader(
        f'site_info/{site_code}/{site_code}.yml')
    new_site_yaml = ks.file_loader(
        f'site_info/{site_code}/{site_code}_new.yml')

    change_list = {
        "update": [],
        "add": [],
        "remove": []
    }
    for switch in site_yaml['Switchlist'][:]:
        found = ks.search_within_list(
            switch['host'], new_site_yaml['Switchlist'], 'host')
        if found:
            if switch['hostname'] != found['hostname']:
                change_list['update'].append(found)
            site_yaml['Switchlist'].remove(switch)
            new_site_yaml['Switchlist'].remove(found)
            continue
        if not found:
            change_list['remove'].append(switch)
    for switch in new_site_yaml['Switchlist']:
        change_list['add'].append(switch)

    ks.file_create(
        f'{site_code}_changelist',
        f'site_info/{site_code}/',
        change_list,
        'yaml',
        override=True
    )


def site_yaml_changes(site_code, debug=None) -> None:
    '''
    Uses the changelist to update the site yaml file.
    '''
    site_yaml = ks.file_loader(
        f'site_info/{site_code}/{site_code}.yml')
    change_list = ks.file_loader(
        f'site_info/{site_code}/{site_code}_changelist.yml')

    for switch in site_yaml['Switchlist']:
        found = ks.search_within_list(
            switch['host'], change_list['update'], 'host')
        if found:
            switch['hostname'] = found['hostname']
            switch['neighbor'] = found['neighbor']

    for switch_add in change_list['add']:
        site_yaml['Switchlist'].append(switch_add)

    for switch_remove in change_list['remove']:
        site_yaml['Switchlist'].remove(switch_remove)
            
    if not debug:
        ks.file_create(
            f'{site_code}',
            f'site_info/{site_code}/',
            site_yaml,
            'yaml',
            override=True
        )


def site_yaml_update_hardware(site_code, user, pwd=None):
    '''
    '''
    if not pwd:
        pwd = ks.verify_pwd(user)

    site_yaml = ks.file_loader(
        f'site_info/{site_code}/{site_code}.yml')
    switch_list = ks.format_site_yaml(site_code, user, pwd=pwd)

    switch_list_output = ks.switch_list_send_command(
        switch_list, 'show version', fsm=True)

    for switch in switch_list_output[:]:
        if not switch['name']:
            switch_list_output.remove(switch)

    for switch in site_yaml['Switchlist']:
        found = ks.search_within_list(
            switch['host'], switch_list_output, 'host')
        if found:
            switch['hardware'] = {}
            if found['device_type'] == 'cisco_ios':
                switch['hardware']['version'] = found['output'][0]['version']
                switch['hardware']['model'] = found['output'][0]['hardware']
                switch['hardware']['mac'] = found['output'][0]['mac']
                switch['hardware']['serial'] = found['output'][0]['serial']
            if found['device_type'] == 'cisco_nxos':
                switch['hardware']['version'] = found['output'][0]['os']
                switch['hardware']['model'] = [found['output'][0]['platform']]
                switch['hardware']['mac'] = []
                switch['hardware']['serial'] = [found['output'][0]['serial']]
            if not found['device_type']:
                logging.warning(f'Missing device_type from {found["name"]}')

    ks.file_create(
        site_code,
        f'site_info/{site_code}/',
        site_yaml,
        file_extension='yml',
        override=True
    )


if __name__ == "__main__":
    pass
