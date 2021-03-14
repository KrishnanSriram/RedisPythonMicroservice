from flask import Flask, jsonify 
import logging
import json
import os
from logging.config import fileConfig
from base64 import b64decode, b64encode
from pdf2image import convert_from_path
import redis

from flask.globals import request

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
fileConfig('logging.cfg')

def load_setting():
    with open('settings.json', 'r') as file:
        return json.load(file)[os.getenv('FLASK_ENV')]

# app.config.from_pyfile('settings.py')
app.config.update(load_setting())

@app.route('/')
def root():
  logging.info('/health invoked')
  return jsonify({"message": "Use POST to convert PDF to image"}), 200

@app.route('/health')
def health() -> str: 
  logging.info('/health invoked')
  return jsonify({"message": "All is well"}), 200

@app.route('/', methods=['POST'])
def root_post():
  org_filename = request.json.get("filename")
  image_filename = request.json.get("image_filename")
  file = request.json.get("file")
  metadata = request.json.get("metadata")
  publish_to = request.json.get("publish_to")
  message = 'Convert {0} to {1} and pass all information \n{2} \nto {3}'.format(org_filename, image_filename, metadata, publish_to)
  logging.info(message)

  # File convertor - string to PDF
  bytes = b64decode(file, validate=True)
  pdf_file = './pdfs/{0}'.format(org_filename) 
  image_file = './images/{0}'.format(image_filename)
  with open(pdf_file, "wb") as fh:
    fh.write(bytes)

  # File convertor - PDF to image
  pages = convert_from_path(pdf_file, 500)
  for page in pages:
    logging.info('Converting file')
    page.save(image_file, 'JPEG')
  
  # File convertor - JPG file to base64 string
  logging.info('Proceed to read file {0}'.format(image_file))
  with open(image_file, "rb") as imgfh:
    encoded_image = b64encode(imgfh.read()).decode('utf-8')

  # send file over redis channel
  REDIS_HOST = app.config.get("REDIS_HOST")
  REDIS_PORT = app.config.get("REDIS_PORT")
  logging.info('We need to load this JSON {0} into Dictionary'.format(metadata))
  response_dict = json.loads(json.dumps(metadata))
  response_dict["filename"] = image_filename
  response_dict["file"] = encoded_image
  client = redis.Redis(REDIS_HOST, REDIS_PORT, db=0)
  client.publish(publish_to, json.dumps(response_dict))

  return "Data successfully published", 200
