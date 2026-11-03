"""Production WSGI entry point. Put an HTTPS reverse proxy in front of this server."""
import os
from waitress import serve
from app import app
if __name__ == '__main__':
    serve(app, host=os.environ.get('BIND_HOST','127.0.0.1'),port=int(os.environ.get('PORT','5000')),threads=4)
