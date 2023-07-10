import setuptools


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='net_map',
    version='2.1',
    author='Katlin Sampson',
    author_email='katlinvsampson@gmail.com',
    description='Creates network map and switch list',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Niltak/net_map',
    project_urls={
        'Bug Tracker': 'https://github.com/Niltak/net_map/issues',
    },
    license="LICENSE.md",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires=['nil_lib', 'networkx', 'diffios', 'pyyaml'],
)