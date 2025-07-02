# Project info
project = 'FunPay Parsers'
copyright = '2025, Qvvonk'
author = 'Qvvonk'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []

language = 'en'


# Theme
html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    'icon_links': [
        {
            'name': 'Telegram',
            'url': 'https://t.me/funpay_hub',
            'icon': 'fa-brands fa-telegram',
        },
        {
            'name': 'PyPi',
            'url': 'https://pypi.org/project/funpayparsers/',
            'icon': 'fa-brands fa-python',
        },
        {
            'name': 'GitHub',
            'url': 'https://github.com/funpayhub/funpayparsers',
            'icon': 'fa-brands fa-square-github',
        },
    ],
}

html_static_path = ['_static']
