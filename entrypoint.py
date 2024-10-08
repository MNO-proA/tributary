# import the flask web framework
from flask import Flask
import json
import redis as redis
from flask import Flask, request
from loguru import logger

HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"
@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    return {"redis_database_values": f'{engine_temperature_values}', "success": True}, 200


# practically identical to the above
@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    sum_of_engine_temp_values = 0
    for engine_temp in engine_temperature_values:
        sum_of_engine_temp_values += float(engine_temp)
    average_engine_temperature = sum_of_engine_temp_values / len(engine_temperature_values)
    logger.info(f"average engine temperature is: {average_engine_temperature}")
    return {"Current_engine_temperature_value": engine_temperature_values[0],
            "Average_engine_temperature_value": average_engine_temperature}, 200