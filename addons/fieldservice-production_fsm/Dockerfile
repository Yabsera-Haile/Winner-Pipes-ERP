FROM bitnami/odoo:14
# copy addons

# This is mount path - gets overwritten
#COPY addons /opt/bitnami/odoo/addons

# This is odoo platform path
COPY addons /opt/bitnami/odoo/odoo/addons
COPY base.xml /opt/bitnami/odoo/odoo/addons/web/static/src/xml

# install pkg in venv
RUN . /opt/bitnami/odoo/venv/bin/activate && pip install pycryptodome

# This is failsafe, but manually needs to be copied
#COPY addons /opt/bitnami/odoo/mongrov

# no listing dbs
#RUN sed -i 's/;.*list_db.*/list_db=False/g' /opt/bitnami/odoo/conf/odoo.conf

