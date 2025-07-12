# Run all development server processes via one process manager with honcho.
#
# Start/spawn all processes with `honcho start` at the command-line.
# Stop children processes with Control+C to send the interrupt signal.
#
# For more information, see: https://honcho.readthedocs.io/en/latest/index.html#what-are-procfiles

proxy: caddy run
server: uvicorn --port=8001 --reload server.main:app
web: cd web && npm run dev
celery: celery -A server.celery.celery_app worker --loglevel=info
