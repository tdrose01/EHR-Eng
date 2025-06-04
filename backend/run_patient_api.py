import os
import sys
import logging
from api.patient_api import app

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set environment variables
os.environ['PORT'] = '8001'
os.environ['FLASK_DEBUG'] = '1'

# Log registered routes
logger.info("Registered routes:")
for rule in app.url_map.iter_rules():
    logger.info(f"{rule.endpoint}: {rule.methods} {rule.rule}")

# Run the app
if __name__ == '__main__':
    try:
        logger.info("Starting Patient API...")
        app.run(host='0.0.0.0', port=8001, debug=True)
    except Exception as e:
        logger.error(f"Error starting Patient API: {e}", exc_info=True)
        sys.exit(1) 