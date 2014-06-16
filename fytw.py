import click
import os
import textwrap


@click.group()
@click.option('--debug', is_flag=True, default=False,
              help="Enable debug mode")
@click.option('--app', default='myapp', type=click.Path(),
              help="Application directory")
@click.pass_context
def cli(ctx, debug, app):
    ctx.obj = {}
    ctx.obj['DEBUG'] = debug
    ctx.obj['APP'] = app


@cli.command()
@click.argument('name', type=click.STRING)
@click.option('--url-prefix', default='',
              help="Url prefix for the model's views ")
@click.pass_context
def module(ctx, name, url_prefix):
    """ This is the fw cli application """
    files = {'__init__.py':'', 'controllers.py':'', 'forms.py':'', 'models.py':''}
    mod_path = '%s.%s' % (ctx.obj['APP'], name)
    if ctx.obj['DEBUG']:
        click.echo('Debug mode = %s' % ctx.obj['DEBUG'])
    if not os.path.exists(name):
        os.makedirs(name)
        for key, value in files.iteritems():
            path = os.path.join(name, key)
            files[key] = open(path, 'w')

        click.echo('from %s.controllers import mod_%s' % (mod_path, name),
                   file=files['__init__.py'])
        click.echo(textwrap.dedent('''\
            # Import flask dependencies
            from flask import Blueprint, request, render_template, flash, \
                redirect, url_for
            # Import other libraries that you migth need


            # Import module forms
            from %(mod_path)s import forms

            # Import module models (i.e. User)
            from %(mod_path)s import models

            # Create the actuall Blueprint
            mod_%(name)s = Blueprint('%(name)s', __name__, url_prefix='/%(url_prefix)s')

            def init_app(app):
                pass

            mod_%(name)s.init_app = init_app

            ''' % {'mod_path': mod_path, 'name': name, 'url_prefix': url_prefix}),
            file=files['controllers.py'])

        click.echo(textwrap.dedent('''\
            # Import application so we can get the DB connection
            from %s import app
            db_session = app.db.db_session
            logger = app.logger
            Base = app.db.Base

            # Create default, abstract Model so we can add the model
            # to the database in a easy way
            class Model(Base):
                __abstract__ = True

                def add(self):
                    try:
                        db_session.add(self)
                        db_session.flush()
                    except Exception as e:
                        logger.debug(e.message)
                        raise e
                    return True

            # Create other models here based on Model
            #class User(Model):
            #    __tablename__ = 'users'
            #    id = Column(Integer, primary_key=True, nullable=False)
            #    name = Column(String(50), unique=True, nullable=False)
            #    email = Column(String(120), unique=True, nullable=False)
            #    password = Column(String(256), nullable=False)
            #    authenticated = Column(Boolean, default=False)
            #    activated = Column(Boolean, default=False)
            #    role_id = Column(Integer, ForeignKey('user_roles.id'),
            #                     server_default='1')


            # Adding models to auto generate Admin pages.
            # Uncomment the next line and duplicate it for each model
            #app.models.append(dict(model=User, db_session=db_session))
            ''' % ctx.obj['APP']),
            file=files['models.py'])

        click.echo(textwrap.dedent('''\
            # Import Form from Flask-wtf
            from flask.ext.wtf import Form

            # Import models from the model file
            from %s.models import *
            ''' % mod_path),
            file=files['forms.py'])

        click.echo("module %s created" % name)
    else:
        click.echo("Module named %s already exists" % name)
