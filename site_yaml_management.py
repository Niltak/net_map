import nil_lib as ks


def site_yaml_compare(site_code) -> None:
    '''
    Compares existing site yaml file with a newly created site yaml file.
    Creates a file dividing switch updates, adds, and removes.
    '''
    site_yaml = ks.file_loader(
        f'site_info/{site_code}/{site_code}.yaml')
    new_site_yaml = ks.file_loader(
        f'site_info/{site_code}/{site_code}_new.yaml')

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
        f'site_info/{site_code}/{site_code}.yaml')
    change_list = ks.file_loader(
        f'site_info/{site_code}/{site_code}_changelist.yaml')

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


if __name__ == "__main__":
    pass
