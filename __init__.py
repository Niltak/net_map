#! /user/bin/env python3 -i

# Network Map v2
# Developed by Katlin Sampson

import networkx as nx
import nil_lib as ks


def net_map(
    target_switch,
    user,
    site_code=None,
    port_display=None,
    reroute_switch_list=None,
    depth=None,
    pwd=None,
    debug=None) -> None:

    if not pwd:
        pwd = ks.verify_pwd(user)
    if reroute_switch_list:
        reroute_switch_list = ks.file_loader(reroute_switch_list)
    if depth:
        counter = 0

    switch_list_cdp, switch_list_errored = net_map_cdp(
        target_switch,
        user,
        pwd=pwd
    )

    if not switch_list_cdp:
        print(f'Could not connect to the main switch {target_switch}!')
        return

    detected_switch_list = [{
        'host': target_switch,
        'hostname': switch_list_cdp[0]['name']
    }]

    if not site_code:
        site_code = switch_list_cdp[0]['name'].split('-')[0]

    site_code = site_code.lower()

    while True:
        switch_list, detected_switch_list = net_map_active_list(
            switch_list_cdp,
            detected_switch_list,
            reroute_switch_list
        )

        if not switch_list:
            break
        if depth:
            if counter == depth:
                break
            counter += 1

        crawler_list_cdp, crawler_list_errored = net_map_cdp(
            switch_list,
            user,
            pwd=pwd
        )

        switch_list_errored += crawler_list_errored
        switch_list_cdp += crawler_list_cdp

    detected_switch_list, switch_list_cdp, switch_list_errored = net_map_cleanup(
        detected_switch_list,
        switch_list_cdp,
        switch_list_errored
    )

    net_map_yaml(
        site_code,
        switch_list_cdp
    )

    net_map_cyto(
        site_code,
        switch_list_cdp,
        switch_list_errored,
        port_display
    )

    if debug:
        net_map_test_output(
            site_code,
            detected_switch_list,
            switch_list_cdp,
            switch_list_errored
        )


def net_map_cleanup(detected_switch_list, switch_list_cdp, switch_list_errored):

    for detected_switch in detected_switch_list:
        for switch_cdp in switch_list_cdp:
            if switch_cdp['name'] in detected_switch['hostname']:
                detected_switch['hostname'] = switch_cdp['name']
                switch_cdp['host'] = detected_switch['host']
                break
    
    for switch_cdp in switch_list_cdp:
        for cdp in switch_cdp['output']:
            found = ks.search_within_list(
                cdp['management_ip'],
                detected_switch_list,
                'host'
            )
            if found:
                cdp['destination_host'] = found['hostname']

    locate_errors = switch_list_cdp.copy()
    for switch_cdp in locate_errors:
        if not 'host' in switch_cdp.keys():
            switch_list_cdp.remove(switch_cdp)
            switch_name = 'Removing entry {0}!'.format(switch_cdp['name'])
            print(switch_name)

    if switch_list_errored:
        for switch_errored in switch_list_errored:
            switch = ks.search_within_list(
                switch_errored['output'],
                detected_switch_list,
                'host'
            )
            switch_errored['hostname'] = switch['hostname']
            switch_errored['host'] = switch_errored.pop('output')

    return detected_switch_list, switch_list_cdp, switch_list_errored


def net_map_cdp(switch_list, user, pwd=None):

    if not pwd:
        pwd = ks.verify_pwd(user)
    if not isinstance(switch_list, list):
        switch_list = [switch_list]

    switch_list_errored, switch_list_server = [], []

    switch_list = ks.format_switch_list(switch_list, user, pwd=pwd)
    switch_list_cdp = ks.switch_list_send_command(
        switch_list, 'sh cdp neighbors detail', fsm=True)

    for switch_cdp in switch_list_cdp:
        # Verify cdp connected and isn't a random server
        if switch_cdp['name'] and user not in switch_cdp['name']:
            crawler_cdp = []
            for cdp in switch_cdp['output']:
                if isinstance(cdp, str):
                    print(f'Issue with {switch_cdp}')
                    continue
                # Only record switches
                if 'Linux' not in cdp['platform']:
                    if 'Switch' in cdp['capabilities']:
                        # Changes Nexus dest_host key to destination_host
                        if 'dest_host' in cdp.keys():
                            cdp['destination_host'] = cdp['dest_host']
                            del cdp['dest_host']
                        if '.tcom.purdue.edu' in cdp['destination_host']:
                            cdp['destination_host'] = cdp['destination_host'].split('.', 1)[0]
                        crawler_cdp.append(cdp)
            switch_cdp['output'] = crawler_cdp
        # Catch switches that did not get logged into
        elif not switch_cdp['name']:
            switch_list_errored.append(switch_cdp)
        # Catch servers
        else:
            switch_list_server.append(switch_cdp)

    for switch_errored in switch_list_errored:
        switch_list_cdp.remove(switch_errored)

    for switch_server in switch_list_server:
        switch_list_cdp.remove(switch_server)

    return switch_list_cdp, switch_list_errored


def net_map_active_list(switch_list_cdp, detected_switch_list, reroute_switch_list):

    switch_list = []
    for switch_cdp in switch_list_cdp:
        for cdp in switch_cdp['output']:
            cdp_hostname = cdp['destination_host']
            if 'interface_ip' in cdp.keys():
                # Change Nexus mgmt_ip key to management_ip
                if 'mgmt_ip' in cdp.keys():
                    cdp['management_ip'] = cdp['mgmt_ip']
                if cdp['interface_ip']:
                    cdp['management_ip'] = cdp['interface_ip']
            # Check switch name from routed list
            if reroute_switch_list:
                reroute_check = ks.search_within_list(
                    cdp_hostname,
                    reroute_switch_list,
                    'hostname'
                )
                if reroute_check:
                    cdp['management_ip'] = reroute_check['host']  
            if not ks.search_within_list(
                cdp_hostname,
                detected_switch_list,
                'hostname'
            ):
                switch_list.append(cdp['management_ip'])
                detected_switch_list.append({
                    'host': cdp['management_ip'],
                    'hostname': cdp['destination_host']
                })

    return switch_list, detected_switch_list


def net_map_yaml(site_code, switch_list_cdp):

    switch_list_cdp = sorted(switch_list_cdp, key=lambda k: k['name'])
    inventory_list = []

    for switch in switch_list_cdp:
        unused_keys = [
            'management_ip',
            'platform',
            'remote_port',
            'software_version',
            'capabilities',
            'interface_ip',
            'sysname',
            'mgmt_ip',
            'version'
        ]

        for cdp in switch['output']:
            for key in unused_keys:
                if key in cdp.keys():
                    del cdp[key]

        inventory_item = {
            'hostname': switch['name'],
            'host': switch['host'],
            'groups': ['EXAMPLE_PCS_BUSINESS', site_code.upper()],
            'neighbor': switch['output'], 
            'data': {
                'location': 'EXAMPLE_DEPARTMENT',
                'role': 'EXAMPLE_CSW_DSW_ASW',
                'device_type': switch['device_type']
        }}
        inventory_list.append(inventory_item)

    inventory_list = {
        'Switchlist': inventory_list,
        'Ignorelist': None
    }

    file_dir = 'site_info/{0}/'.format(site_code)

    ks.file_create(
        site_code,
        file_dir,
        inventory_list,
        file_extension='yaml'
    )


def net_map_cyto(
    site_code,
    switch_list_cdp,
    switch_list_errored,
    port_display):

    g = nx.Graph()

    for switch_cdp in switch_list_cdp:
        if port_display:
            g.add_node(switch_cdp['name'])
        else:
            g.add_node(switch_cdp['name'])

    for switch_list in switch_list_errored:
        g.add_node(switch_list['hostname'])

    for switch_list in switch_list_cdp:
        switch_name = switch_list['name']
        for cdp in switch_list['output']:
            switch_cdp_name = cdp['destination_host']
            if not g.has_edge(switch_name, switch_cdp_name) or not g.has_edge(switch_cdp_name, switch_name):
                g.add_edge(switch_name, switch_cdp_name,)

    # Does not work with cytoscape
        # color_map = []
        # for node in g.nodes():
        #     if len(g[node]) > 5:
        #         color_map.append('red')
        #     else:
        #         color_map.append('blue')

    file_name = '{0}_cyto'.format(site_code)
    file_dir = 'site_info/{0}/'.format(site_code)
    data = nx.cytoscape_data(g)

    node_list = data['elements']['nodes']

    for node in node_list:
        node['data']['label'] = node['data'].pop('value')
        del node['data']['name']

    ks.file_create(
        file_name,
        file_dir,
        data,
        file_extension='json',
        override=True
    )


def net_map_test_output(
    site_code,
    detected_switch_list,
    switch_list_cdp,
    switch_list_errored):

    data = {
        'detected': detected_switch_list,
        'cdp': switch_list_cdp,
        'errored': switch_list_errored
    }

    file_name = f'{site_code}_debug'.format(site_code)

    ks.file_create(
        file_name,
        f'site_info/{site_code}/',
        data,
        file_extension='yaml',
        override=True
    )


if __name__ == "__main__":
    pass
