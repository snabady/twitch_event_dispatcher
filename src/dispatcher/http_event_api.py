from flask import Flask, request, jsonify
from src.dispatcher.event_dispatcher import post_event
import logging
from src.utils import log


app = Flask (__name__)

logger = logging.getLogger(__name__)
logger = log.add_logger_handler(logger)
logger.setLevel(logging.DEBUG)   

@app.route("/trigger_event", methods=["POST"])
def trigger_event():
    data = request.get_json(force=True)
    logger.debug(data)
    event_type = data.get("event_type")
    event_data = data.get("event_data")

    if not event_type or event_data is None:
        return jsonify({"error": "event_type and event_data required"}), 400 
    post_event(event_type, event_data)
    return jsonify({"status": "event triggered", "event_type": event_type, "event_data": event_data})
