import os
import yaml
import diffios
import net_map
import nil_lib as ks

###
### TODO: The whole module needs Refactoring
###

def survey_site_list(site_list, user, inventory=None, pwd=None):

    if not pwd:
        pwd = ks.verify_pwd(user)

    if not isinstance(site_list, list):
        site_list = [site_list]

    for site in site_list:
        site_code = site['site_code']
        net_map.net_map(site['core_ip'], user, pwd=pwd)
        survey_site_config_collect(site_code, user, pwd=pwd)
        survey_site_config_compare(site_code)
        survey_site_secureCRT(site_code, user)
        if inventory:
            survey_site_inventory(site_code, user, pwd=pwd)


def survey_site_config_collect(site_code, user, yaml_inventory=None, pwd=None):
    if not pwd:
        pwd = ks.verify_pwd(user)

    if not yaml_inventory:
        yaml_inventory = 'site_info/{0}/{0}.yaml'.format(site_code)

    switch_list = ks.format_site_yaml(yaml_inventory, user, pwd=pwd)
    switch_list_configs = ks.switch_list_send_command(switch_list, 'sh run')

    for switch_config in switch_list_configs:
        if switch_config['name']:
            file_dir = 'site_info/{0}/configs/'.format(site_code)
            file_name = switch_config['name']

            ks.file_create(
                file_name,
                file_dir,
                switch_config['output'],
                override=True
            )

# Arconic site_info groupings

# def survey_site_config_compare(site_code):

#     file_dir = 'site_info/{0}/configs/'.format(site_code)
#     compare_dir = 'site_info/{0}/diff/'.format(site_code)

#     config_template = 'site_info/.baseline/baseline.txt'
#     config_ignore = 'site_info/.baseline/ignore.txt'

#     for subdir, dirs, files in os.walk(file_dir):
#         for file_name in files:
#             compare_file = file_dir + file_name
#             data_results = diffios.Compare(
#                 config_template,
#                 compare_file,
#                 config_ignore
#             )

#             ks.file_create(
#                 file_name[:-4],
#                 compare_dir,
#                 data_results.delta(),
#                 override=True
#             )


def survey_site_config_compare(file_dir, output_dir=None, filter=None):

    if not output_dir:
        output_dir = 'configs/pwl/'
    else:
        if output_dir[-1:] != '/':
            output_dir = output_dir + '/'

    config_template = 'templates/.baseline/baseline.txt'
    config_ignore = 'templates/.baseline/ignore.txt'

    for subdir, dirs, files in os.walk(file_dir):
        for file_name in files:
            if filter:
                if filter not in file_name:
                    continue
            compare_file = file_dir + file_name
            data_results = diffios.Compare(
                config_template,
                compare_file,
                config_ignore
            )
            ks.file_create(
                file_name[:-4],
                output_dir,
                data_results.delta(),
                override=True
            )


def survey_site_inventory(site_code, user, site_yaml=None, pwd=None):

    if not pwd:
        pwd = ks.verify_pwd(user)
    if not site_yaml:
        site_yaml = f'site_info/{site_code}/{site_code}.yaml'

    switch_list = ks.format_site_yaml(
        site_yaml,
        user,
        pwd=pwd
    )

    switch_inventory = ks.switch_list_send_command(
        switch_list,
        'sh inventory',
        fsm=True
    )

    for switch in switch_inventory[:]:
        if not switch['name']:
            switch_inventory.remove(switch)

    file_name = f'{site_code}_inventory'
    file_dir = f'site_info/{site_code}/'
    switch_inventory = {'Switchlist': switch_inventory}

    ks.file_create(
        file_name,
        file_dir,
        switch_inventory,
        file_extension='yaml',
        override=True
    )


def survey_site_secureCRT(site_code, jumpbox, user):

    baseline = 'templates/.baseline/baseline_secureCRT.ini'
    with open(baseline, 'r') as baseline_ini:
        ini_data = baseline_ini.readlines()

    yaml_inventory = 'site_info/{0}/{0}.yaml'.format(site_code)
    with open(yaml_inventory, 'r') as yaml_file:
        switch_list = yaml.load(yaml_file, Loader=yaml.FullLoader)

    for num, line in enumerate(ini_data):
        if '[username]' in line:
            ini_data[num] = ini_data[num].replace('[username]', user)
        if '[hostname]' in line:
            index = num
        if '[jumpbox]' in line:
            ini_data[num] = ini_data[num].replace('[jumpbox]', jumpbox)
            break

    file_dir = 'site_info/{0}/secureCRT/'.format(site_code)

    for switch in switch_list['Switchlist']:
        switch_ini = ini_data.copy()
        switch_ini[index] = switch_ini[index].replace('[hostname]', switch['host'])
        ks.file_create(
            switch['hostname'],
            file_dir,
            switch_ini,
            file_extension='ini',
            override=True
        )


def survey_site_check(
    site_code,
    user,
    show_command, 
    site_yaml=None,
    file_description=None,
    pwd=None):

    # TODO: Needs Refactoring
    pass

    # if not pwd:
    #     pwd = ks.verify_pwd(user)

    # switch_list_data = ks.inventory_send_command(
    #     site_code,
    #     show_command,
    #     user,
    #     yaml_inventory=yaml_inventory,
    #     fsm=True,
    #     pwd=pwd
    # )

    # # Removing Switches that were not connected to
    # errored_switch_list = []
    # for switch_list in switch_list_data:
    #     if not switch_list['name']:
    #         errored_switch_list.append(switch_list)
    # for errored_switch in errored_switch_list:
    #     switch_list_data.remove(errored_switch)

    # if file_description:
    #     file_name = '{0}_{1}'.format(site_code, file_description)
    # else:
    #     file_name = '{0}_{1}'.format(site_code, show_command)
    
    # file_dir = 'site_info/{0}/'.format(site_code)
    # switch_list_data = {'Switchlist': switch_list_data}

    # ks.file_create(
    #     file_name,
    #     file_dir,
    #     switch_list_data,
    #     file_extension='yaml',
    #     override=True
    # )


if __name__ == "__main__":
    pass
