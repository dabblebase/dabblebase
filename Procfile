# Run all development server processes via one process manager with honcho.
#
# Start/spawn all processes with `honcho start` at the command-line.
# Stop children processes with Control+C to send the interrupt signal.
#
# For more information, see: https://honcho.readthedocs.io/en/latest/index.html#what-are-procfiles

# Note: Ordering is not necessarily logical but makes the honcho colors work :)

proxy: caddy run
server: uvicorn --port=8001 --reload server.main:app
celery-worker: celery -A server.celery.celery_app worker --loglevel=info
realtime: cd realtime && mix phx.server
celery-beat: celery -A server.celery.celery_app beat --loglevel=info
web: cd web && npm run dev
