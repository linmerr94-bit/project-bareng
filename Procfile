release: python manage.py migrate && python manage.py populate_sample_data
web: gunicorn core_system.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --timeout 60 --access-logfile - --error-logfile -
