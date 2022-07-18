import json
from dash import Dash, html, dcc, callback_context
from dash.dependencies import Output, Input
import dash_cytoscape as cyto


def cyto_map_server(cyto_file):

    with open(cyto_file) as json_file:
        cyto_elements = json.load(json_file)

    cyto.load_extra_layouts()

    styles = {
        'data': {
            'width': 'calc(100% - 400px)',
            'height': '95vh',
            'float': 'left'
        },
        'data_map': {
            'width': '100%',
            'height': '95vh'
        },
        'menu': {
            'width': '400px',
            'height': '95vh',
            'float': 'right'
        },
        'menu_tab': {
            'width': 'calc(100% - 2px)',
            'height': '300px',
            'border': 'thin lightgrey solid'
        }
    }

    app = Dash(__name__)
    app.layout = html.Div([
        html.Div(className='data', style=styles['data'], children=[
            cyto.Cytoscape(
                id='data_map',
                # layout={'name': 'dagre', 'spacingFactor': '2'},
                layout={'name': 'klay'},
                # layout={'name': 'cola', 'convergenceThreshold': 0.001, 'maxSimulationTime': 25000, 'nodeSpacing': 25},
                style=styles['data_map'],
                elements=cyto_elements['elements']
            )
        ]),
        html.Div(className='menu', style=styles['menu'], children=[
            dcc.Tabs(id='menu_tabs', children=[
                dcc.Tab(label='Data Set', value='menu_data_set', children=[
                    html.Div(
                        id='menu_tab_data',
                        style=styles['menu_tab'],
                        children=[html.Blockquote('testing')])
                ]),
                dcc.Tab(label='Controls', value='menu_controls', children=[
                    html.Div(
                        id='menu_tab_controls',
                        style=styles['menu_tab'],
                        children=[html.Blockquote('testing')])
                ])
            ]),
            html.Div(id='download', children=[
                html.H3('Download Map: '),
                html.Button('jpg', id='get_jpg'),
                html.Button('png', id='get_png'),
                html.Button('svg', id='get_svg'),
            ])
        ])
    ])

    @app.callback(
        Output('data_map', 'generateImage'),
        [
            Input('data_map', 'imageData'),
            Input('get_jpg', 'n_clicks'),
            Input('get_png', 'n_clicks'),
            Input('get_svg', 'n_clicks')
        ]
    )
    def get_image(data, get_jpg, get_png, get_svg):

        file_extension = None
        ctx = callback_context
        if ctx.triggered:
            output = ctx.triggered[0]['prop_id'].split('.')[0]
            file_extension = output[-3:]

        return {
            'type': file_extension,
            'action': 'download',
            'options': {
                'quality': 1,
                'full': True
            }
        }

    app.run_server(debug=True)


if __name__ == '__main__':
    pass
