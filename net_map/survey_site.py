import os
import diffios
from net_map import net_map
from nil_lib import *


def survey_site_list(
    site_list, user, inventory=None, pwd=None) -> None:
    '''
    '''
    if not isinstance(site_list, list):
        site_list = [site_list]

    for site in site_list:
        site_code = site['site_code']
        net_map(site['core_ip'], user, pwd=pwd)
        get_site_configs(site_code, user, pwd=pwd)
        compare_site_configs(site_code)
        create_site_SecureCRT(site_code, user)
        if inventory:
            get_site_inventory(site_code, user, pwd=pwd)


def get_site_configs(
    site_code, user, pwd=None) -> None:
    '''
    '''
    switch_list = format_site_yaml(site_code, user, pwd=pwd)
    switch_configs = switch_list_send_command(
        switch_list, ['do term len 0', 'sh run'])

    for config in switch_configs:
        if config['name']:
            file_dir = f'site_info/{site_code}/configs/dump/'
            file_name = config['name']

            file_create(
                file_name, file_dir,
                config['output'], override=True)


def get_site_inventory(
    site_code, user, site_yaml=None, pwd=None) -> None:
    '''
    '''
    switch_list = format_site_yaml(
        site_yaml,  user, pwd=pwd)

    switch_inventory = switch_list_send_command(
        switch_list, 'sh inventory', fsm=True)

    for switch in switch_inventory[:]:
        if not switch['name']:
            switch_inventory.remove(switch)

    file_name = f'{site_code}_inventory'
    file_dir = f'site_info/{site_code}/'
    data = {'Switchlist': switch_inventory}

    file_create(
        file_name, file_dir, data,
        file_extension='yml', override=True)
    

def get_site_hardware(
    site_code, user, pwd=None):
    '''
    '''
    switch_list = format_site_yaml(
        site_code, user, pwd=pwd)

    switch_list = switch_list_send_command(
        switch_list, 'show version', fsm=True)

    hardware_list = []
    for switch in switch_list[:]:
        if not switch['name']:
            # TODO: CONNECTION ISSUE LIST
            switch['name'] = switch['output']
            del switch['output']
            continue

        switch['data'] = switch['output']
        del switch['output']
        del switch['host']
        del switch['device_type']

        for output in switch['data']:
            if 'hardware' in output.keys():
                hardware_list += output['hardware']
            elif 'platform' in output.keys():
                hardware_list.append(output['platform'])

    file_name = f'{site_code}_hardware'
    file_dir = f'site_info/{site_code}/'
    data = {'Switchlist': switch_list, 'Hardware': hardware_list}

    file_create(
        file_name, file_dir, data,
        file_extension='yml', override=True)
    

def compare_site_configs(
    site_code, output_dir=None, filter=None) -> None:
    '''
    '''
    config_template = 'templates/.baseline/baseline.txt'
    config_ignore = 'templates/.baseline/ignore.txt'

    file_dir = f'site_info/{site_code}/{site_code}.yml'
    for subdir, dirs, files in os.walk(file_dir):
        for file_name in files:
            if filter:
                if filter not in file_name:
                    continue
            
            compare_file = file_dir + file_name
            data_results = diffios.Compare(
                config_template, compare_file, config_ignore)
            file_create(
                file_name[:-4], output_dir,
                data_results.delta(), override=True)


def create_site_SecureCRT(
    site_code, jumpbox, user):
    '''
    '''
    ini_data = file_loader(
        'templates/.baseline/baseline_secureCRT.ini',
        file_lines=True)
    switch_list = file_loader(
        f'site_info/{site_code}/{site_code}.yml')

    for num, line in enumerate(ini_data):
        if '[username]' in line:
            ini_data[num] = ini_data[num].replace('[username]', user)
        if '[hostname]' in line:
            index = num
        if '[jumpbox]' in line:
            ini_data[num] = ini_data[num].replace('[jumpbox]', jumpbox)
            break

    file_dir = f'site_info/{site_code}/secureCRT/'
    for switch in switch_list['Switchlist']:
        switch_ini = ini_data.copy()
        switch_ini[index] = switch_ini[index].replace(
            '[hostname]', switch['host'])
        file_create(
            switch['hostname'], file_dir, switch_ini,
            file_extension='ini', override=True)


if __name__ == "__main__":
    pass
