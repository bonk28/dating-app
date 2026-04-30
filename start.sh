#!/bin/bash
gunicorn run:app --worker-class gevent --bind 0.0.0.0:$PORT --workers 1 --timeout 120
