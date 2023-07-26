# Standard Python modules

from datetime import datetime #, pytz

start_time = datetime.now()

import os, requests
# Set environment variables
# os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
# os.environ["TORCH_USE_CUDA_DSA"] = "1"

# Get the Brazil time zone

# brazil_tz = pytz.timezone('America/Sao_Paulo')

# Flask Python modules

# from flask import request, Response, render_template
from flask_cors import CORS

# APIFlask Python modules

from apiflask import APIFlask, Schema, HTTPError
# from apiflask.fields import Integer, Float, String, Boolean, DelimitedList
# from apiflask.validators import Length, OneOf

# Custom Python modules

from modules.aws import get_public_ipv4, reboot_ec2_instance

# FLASK APP DEFINITION -----------------

# Set current API version
version = '0.1'

# set openapi.info.title and openapi.info.version
app = APIFlask(__name__, title='OCTACITY AWS NVIDIA EC2 API', version=version, docs_ui='elements')
CORS(app)


# OPENAPI SPECIFICATION OPTIONS --------------

# openapi.info.description
app.config['DESCRIPTION'] = "API to manage AWS EC2 instance" # open('README.MD').read()

# openapi.info.contact
app.config['CONTACT'] = {
    'name': 'OCTA CITY SOLUTIONS',
    'url': 'http://octacity.org',
    'email': 'luisresende@id.uff.br'
}

# openapi.info.license
# app.config['LICENSE'] = {
#     'name': 'MIT',
#     'url': 'https://opensource.org/licenses/MIT'
# }

# openapi.info.termsOfService
# app.config['TERMS_OF_SERVICE'] = 'http://example.com'

# openapi.tags
app.config['TAGS'] = [{
    'name': "Server",
    "description": "Server information"
}]

cloudRunServerURL = 'https://octa-vision-oayt5ztuxq-ue.a.run.app'

try:
    awsIP = requests.get(f"{cloudRunServerURL}/ip").text
except:
    awsIP = ''
    
# openapi.servers
app.config['SERVERS'] = [{
#     'name': 'AWS NVIDIA Server',
#     'url': f"http://{awsIP}"
# }, {
    'name': 'Google Cloud Run Server',
    'url': cloudRunServerURL
}, {
    'name': 'Development Server',
    'url': 'http://localhost:5000'
}]

# openapi.externalDocs
app.config['EXTERNAL_DOCS'] = {
    'description': 'Find more info here',
    'url': 'https://octacity.org'
}

# FLASK CONFIGURATION OPTIONS ----------------

# Flask timeout
app.config['TIMEOUT'] = None  # Set timeout to None (no timeout)


# SERVER INFO ENDPOINTS -----------

@app.get("/init")
@app.doc(tags=['Server'])
def initialize():
    name = os.environ.get("NAME", app.title)
    return f'Server `{name}` version `v{version}` is running!'

@app.get("/ip")
@app.doc(tags=['Server'])
def server_ip():
    instance_id = 'i-01796a60ab18b8bd5'
    public_ipv4 = get_public_ipv4(instance_id)
    if 'ip' not in public_ipv4:
        message = "Failed to retrieve the public IPv4 address."
        print(message)
        raise HTTPError(500, message, public_ipv4['error'])
    print("Public IPv4 GET request successful:", public_ipv4['ip'])
    return public_ipv4['ip']

@app.get("/reboot")
@app.doc(tags=['Server'])
def server_reboot():
    instance_id = 'i-01796a60ab18b8bd5'
    message = reboot_ec2_instance(instance_id)
    if message == 'success':
        print(message)
        return message
    raise HTTPError(500, 'Internal server error when rebooting ec2 instance', message)

# Calculate the elapsed time (startup time)
end_time = datetime.now()
elapsed_time = end_time - start_time
print(f"Startup time for the Flask app: {elapsed_time.total_seconds():.1f} seconds")
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
