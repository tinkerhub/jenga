from setuptools import setup, find_packages

requirements = [
    "airtable-python-wrapper==0.15.0",
    "deta==0.6",
    "Flask==1.1.2",
    "jinja2>=2.11.3",
    "python-dotenv==0.14.0",
    "requests==2.23.0",
    "requests-oauthlib==1.3.0",
    "Werkzeug==1.0.1",
    "gunicorn",
    "Flask-Cors==3.0.9",
    "PyJWT==1.7.1",
    "flake8==3.8.4",
    "black==20.8b1",
]

setup(
    name="jenga",
    version="0.0.1",
    zip_safe=False,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=requirements,
)
