#!/usr/bin/env python3
from hyper import HTTPConnection, HTTP20Connection
from hyper.tls import init_context

import json

devEnvironments = ["dev", "development"]
prodEnvironments = ["prod", "production"]

def getOrRaise(dict, key, default=None):
    result = dict.get(key, default)
    if result == None:
        raise ValueError("Missing {} key in request".format(key))
    return result

def getEnvironment(dict):
    result = getOrRaise(dict, "environment")
    if result in devEnvironments + prodEnvironments:
        return result
    raise ValueError("Invalid Environment found. Please set either 'dev' or 'prod' as the value for 'environment' key in request.")


def send_push(input):
    topic = getOrRaise(input, "topic")    
    token = getOrRaise(input, "token_hex")
    apnsPayload = getOrRaise(input, "apns")
    environment = getEnvironment(input)

    if environment in devEnvironments:
        host = "api.development.push.apple.com"
        pushCert = "cert/pushcert_dev.p12" 
    if environment in prodEnvironments:
        host = "api.push.apple.com"
        pushCert = "cert/pushcert_prod.p12" 

    print(host)

    method = "POST"
    path = "/3/device/{}".format(token)

    # Build headers
    headers = {"apns-topic": topic}
    
    if input.get("apns-push-type"):
        headers["apns-push-type"] = input.get("apns-push-type")
    if input.get("apns-id"):
        headers["apns-id"] = input.get("apns-id")
    if input.get("apns-expiration"):
        headers["apns-expiration"] = input.get("apns-expiration")
    if input.get("apns-priority"):
        headers["apns-priority"] = input.get("apns-priority")
    if input.get("apns-collapse-id"):
        headers["apns-collapse-id"] = input.get("apns-collapse-id")
    

    conn = HTTPConnection(
        host=host,
        secure=True,
        port=443,
        ssl_context=init_context(cert=pushCert)
    )

    conn.request(
        method=method,
        url=path,
        body=json.dumps(apnsPayload).encode("utf-8"),
        headers=headers
    )

    return conn.get_response()


def lambda_handler(event, context):
    try:
        response = send_push(event)
    
        return {
            "statusCode": response.status,
            "body": response.read().decode("utf-8")
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps(e)
        }



if __name__ == "__main__":
    # Running Executable from Script

    apnsPayload = {
        "aps": { "alert": "Test Alert!" },
        "acme": "Some Test Metadata"
    }
    
    event = {
        "topic": "com.schustudios.PushExample",
        "token_hex": "4177cc6b62437e0943c5b9fd3d5bad8344c80ae7ed38bb429d7bdb26b1a6f042",
        "environment": "development",
        "apns": apnsPayload

    }

    try:
        response = send_push(event)
    
        print("Status Code: {}".format(response.status))
        print(response.read().decode("utf-8"))

    except Exception as e:
        print(e)