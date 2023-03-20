"""
OCI Function for Email Delivery Blocked Notification (Python example)

This function takes one or more OCI Email Domain log events and sends HTTP "postback"
notifications to a website address, similar to the Dyn Postback feature.

This function can be modified to support any type of log item.

Requirements/Dependencies:

OCI Email Delivery service configuration (https://docs.oracle.com/en-us/iaas/Content/Email/Reference/gettingstarted.htm)
- user with SMTP credentials
- required policies
- email domain with SPF + DKIM set up
- email domain logging enabled
- approved sender created

OCI Functions configuration (https://docs.oracle.com/en-us/iaas/Content/Functions/Tasks/functionsquickstartcloudshell.htm)
- VCN + subnet (private, using NAT Gateway)
- required policies
- application (with optional logging enabled)
- function with code to read Log and send HTTP request

OCI Service Connector Hub integration with Logging (https://docs.oracle.com/en-us/iaas/Content/service-connector-hub/create-service-connector-logging-source.htm)
- service connector using:
-- VCN subnet
-- Logging as source, pointed at Email Domain "outboundrelayed" log, and two log rule tasks added, "data.action = accept" and "data.errorType = 'Recipient suppressed'" (can fine-tune this to be more or less granular)
-- OCI Function as target
"""

import io
import json
import logging
import requests

from fdk import response

postback_url_with_params = "https://ascentwebs.com/dyn-http-handler.php?type=s&e={email}&dc={diagnostic}&message={message}"
postback_url_no_params = "https://ascentwebs.com/dyn-http-handler.php"

def handler(ctx, data: io.BytesIO=None):

    """
    Main Function handler routine, takes 
    """

    # Input is one or more Log events; parse into JSON and loop through them
    try:
        logs = json.loads(data.getvalue())

        for item in logs: 

            # Pull postback field values from log event
            log_data = item['logContent']['data']

            # For custom headers, gather them (if present) and loop through to add to request parameters
            #headers = log_data['headers']  # gives a dictionary of (header_name -> value) pairs

            params_values = {
                "email": log_data['recipient'],
                "diagnostic": log_data['smtpStatus'],
                "message": log_data['message']
            }

            # Traditional URL querystring GET method, no request body
            http_response = requests.get(postback_url_with_params.format(**params_values))
            # POST method
            #response = requests.get(postback_url_no_fields, params=params_values)

            logging.getLogger().info("Postback sent: {} Response: HTTP {} --- {}".format(http_response.url, http_response.status_code, http_response.text.replace('\n', '')))
       
    except (Exception, ValueError) as ex:
        logging.getLogger().error(str(ex))
        return
