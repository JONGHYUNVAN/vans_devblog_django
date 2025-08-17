# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'VansDevBlog Search Service'
copyright = '2025, van'
author = 'van'
release = '0.0.1'

# -- Path setup --------------------------------------------------------------
import os
import sys
import django

# Django 프로젝트 경로 추가
sys.path.insert(0, os.path.abspath('../../'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vans_search_service.settings')
django.setup()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

# -- Autodoc configuration --------------------------------------------------
autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'show-inheritance': True,
    'member-order': 'bysource',
    'exclude-members': '__weakref__'
}

# 모듈 레벨 변수 제외
autodoc_mock_imports = []

def skip_module_variables(app, what, name, obj, skip, options):
    """모듈 레벨 변수들을 문서에서 제외"""
    if what == "data" and hasattr(obj, '__module__'):
        # analyzer, tokenizer 등의 elasticsearch dsl 객체들 제외
        if any(x in str(type(obj)) for x in ['analyzer', 'tokenizer', 'normalizer']):
            return True
    return skip

def setup(app):
    app.connect('autodoc-skip-member', skip_module_variables)

templates_path = ['_templates']
exclude_patterns = []

language = 'python'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

# Furo 테마 설정
html_title = "VansDevBlog Search Service"
html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#2563eb",
        "color-brand-content": "#2563eb",
        "color-admonition-background": "transparent",
    },
    "dark_css_variables": {
        "color-brand-primary": "#3b82f6",
        "color-brand-content": "#3b82f6",
    },
}
