web: gunicorn predictive_whist.wsgi --log-level debug

# Run migrations as part of app deployment, using Heroku's Release Phase feature.
release: ./manage.py migrate --no-input