"""CampusFind: HTML/Tailwind/JavaScript served with a persistent Flask/SQLite API."""
from __future__ import annotations
import io
import os
import secrets
from datetime import timedelta
from pathlib import Path
import click
from dotenv import load_dotenv
from flask import g, Flask, jsonify, request, send_file, send_from_directory, session
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

BASE_DIR=Path(__file__).resolve().parent
load_dotenv(BASE_DIR/'.env')
# Read the data-directory environment only after loading .env.
from backend.api import bp as api_bp, current_user
from backend.auth import bp as auth_bp
from backend.db import get_db, close_db, execute, get_secret_key, init_db, query
from backend.security import csrf_token, limited
from backend.validation import email_address, ugandan_phone, password as validate_password

PAGES={'index','browse','item','report','dashboard','admin','login','register','verify','forgot','how-it-works','404'}

def create_app(test_config=None):
    app=Flask(__name__,static_folder='static',static_url_path='/static')
    production=os.environ.get('APP_ENV')=='production'
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or get_secret_key(),
        MAX_CONTENT_LENGTH=6*1024*1024, SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',SESSION_COOKIE_SECURE=production,
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        SMTP_HOST=os.environ.get('SMTP_HOST',''),SMTP_PORT=int(os.environ.get('SMTP_PORT','587')),
        SMTP_SECURITY=os.environ.get('SMTP_SECURITY','starttls'),SMTP_USERNAME=os.environ.get('SMTP_USERNAME',''),
        SMTP_PASSWORD=os.environ.get('SMTP_PASSWORD',''),MAIL_SENDER=os.environ.get('MAIL_SENDER',''),
        PUBLIC_ORIGIN=os.environ.get('PUBLIC_ORIGIN','http://127.0.0.1:5000').rstrip('/'))
    if test_config:app.config.update(test_config)
    if production:
        if len(app.secret_key) < 32: raise RuntimeError('Use a SECRET_KEY of at least 32 characters.')
        if not app.config['PUBLIC_ORIGIN'].startswith('https://'): raise RuntimeError('Production requires an HTTPS PUBLIC_ORIGIN.')
    if os.environ.get('TRUST_PROXY')=='1':app.wsgi_app=ProxyFix(app.wsgi_app,x_for=1,x_proto=1,x_host=1)
    init_db()
    app.register_blueprint(api_bp);app.register_blueprint(auth_bp)
    app.teardown_appcontext(close_db)

    @app.before_request
    def protect():
        # Evaluate expiry before serving either item metadata or its photo.
        if request.path.startswith(('/api/','/uploads/')):
            execute("UPDATE items SET archived=1 WHERE status='resolved' AND archived=0 AND retain_until IS NOT NULL AND datetime(retain_until)<=datetime('now') AND disputed=0")
        if not request.path.startswith('/api/'):return
        if request.method not in ('GET','HEAD','OPTIONS'):
            token=request.headers.get('X-CSRF-Token','')
            if not token or not secrets.compare_digest(token,session.get('csrf','')):
                return jsonify(error='Your session expired. Refresh the page and try again.'),403
            origin=request.headers.get('Origin')
            if origin and origin != app.config['PUBLIC_ORIGIN']:
                return jsonify(error='Request origin is not permitted.'),403
        if request.path.startswith('/api/auth/') and request.method=='POST':
            if limited('auth-ip:'+str(request.remote_addr),60,900):
                return jsonify(error='Too many account requests. Try again in 15 minutes.'),429
        if request.method not in ('GET','HEAD','OPTIONS') and not request.path.startswith('/api/auth/'):
            if limited('write:'+str(session.get('user_id') or request.remote_addr),120,60):
                return jsonify(error='Too many requests. Wait one minute.'),429
            get_db().execute('BEGIN IMMEDIATE')
            g.atomic_write=True

    @app.get('/')
    def home():return send_from_directory(BASE_DIR,'index.html')
    @app.get('/<page>.html')
    def page(page):
        if page not in PAGES:return not_found(None)
        return send_from_directory(BASE_DIR,page+'.html')
    @app.get('/favicon.svg')
    @app.get('/favicon.ico')
    def favicon():return send_from_directory(app.static_folder,'favicon.svg')
    @app.get('/uploads/<name>')
    def image(name):
        row=query('SELECT mime,data FROM image_blobs WHERE name=?',(name,),one=True)
        if not row:return not_found(None)
        item=query('SELECT * FROM items WHERE image_path=?',(name,),one=True)
        viewer=current_user()
        participant=viewer and item and query("SELECT 1 FROM claims WHERE item_id=? AND claimant_id=? AND status='approved'",(item['id'],viewer['id']),one=True)
        if not item or ((item['status']=='removed' or item['archived']) and not (viewer and (viewer['id']==item['user_id'] or viewer['role']=='admin' or participant))):
            return not_found(None)
        response=send_file(io.BytesIO(row['data']),mimetype=row['mime'],max_age=0)
        response.headers['Cache-Control']='private, no-store'
        return response
    @app.errorhandler(404)
    def not_found(_):
        if request.path.startswith('/api/'):return jsonify(error='Not found.'),404
        return send_from_directory(BASE_DIR,'404.html'),404
    @app.errorhandler(413)
    def too_large(_):return jsonify(error='Upload too large. Photos must be 5 MB or smaller.'),413
    @app.errorhandler(Exception)
    def failure(exc):
        if isinstance(exc,HTTPException):return exc
        app.logger.exception('Request failed')
        if request.path.startswith('/api/'):return jsonify(error='The request could not be completed. Please try again.'),500
        return send_from_directory(BASE_DIR,'404.html'),500
    @app.after_request
    def headers(response):
        if g.get('atomic_write'):
            if response.status_code < 400: get_db().commit()
            else: get_db().rollback()
            g.atomic_write=False
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
        response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; font-src 'self'; connect-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        if production:response.headers['Strict-Transport-Security']='max-age=31536000'
        if request.path.startswith('/api/') or response.mimetype=='text/html':response.headers['Cache-Control']='no-store'
        return response

    @app.cli.command('create-admin')
    @click.option('--email',prompt=True)
    @click.option('--name',prompt=True)
    @click.option('--phone',prompt=True)
    @click.password_option(confirmation_prompt=True)
    def create_admin(email,name,phone,password):
        """Create the first admin explicitly; no default accounts or passwords."""
        try:
            email=email_address(email);phone=ugandan_phone(phone);validate_password(password)
            if not 2<=len(name.strip())<=80:raise ValueError('Name must be 2–80 characters.')
        except ValueError as exc:raise click.ClickException(str(exc))
        if query('SELECT id FROM users WHERE email=?',(email,),one=True):raise click.ClickException('Email already registered. Use promote-admin for an existing verified account.')
        execute("INSERT INTO users(name,email,phone,password_hash,role,verified_at) VALUES(?,?,?,?,'admin',datetime('now'))",(name.strip(),email,phone,generate_password_hash(password)))
        click.echo('Administrator created. Keep these credentials private.')
    @app.cli.command('promote-admin')
    @click.argument('email')
    def promote_admin(email):
        row=query('SELECT id FROM users WHERE email=? AND verified_at IS NOT NULL',(email.lower(),),one=True)
        if not row:raise click.ClickException('Verified account not found.')
        execute("UPDATE users SET role='admin',session_version=session_version+1 WHERE id=?",(row['id'],))
        click.echo('Account promoted. Log in again.')
    @app.cli.command('maintenance')
    def maintenance():
        execute("UPDATE items SET archived=1 WHERE status='resolved' AND retain_until IS NOT NULL AND datetime(retain_until)<=datetime('now') AND disputed=0")
        execute("DELETE FROM email_challenges WHERE expires_at < strftime('%s','now')-86400")
        execute("DELETE FROM rate_limits WHERE resets_at < strftime('%s','now')")
        click.echo('Expired recovery records archived; expired challenges and rate counters cleaned.')
    return app

app=create_app()
if __name__=='__main__':
    print('CampusFind: http://127.0.0.1:'+os.environ.get('PORT','5000'))
    app.run(host='127.0.0.1',port=int(os.environ.get('PORT','5000')),debug=False)
