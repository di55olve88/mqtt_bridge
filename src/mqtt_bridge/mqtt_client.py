# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import ssl
from pdb import set_trace as bp

import paho.mqtt.client as mqtt
import rospy


def default_mqtt_client_factory(params):
    u""" MQTT Client factory

    :param dict param: configuration parameters
    :return mqtt.Client: MQTT Client
    """    
    ca = "/home/nvidia/Downloads/certs/icstx22/Amazon_Root_CA_1.pem" 
    cert = "/home/nvidia/Downloads/certs/icstx22/c9faf68aac-certificate.pem.crt"
    private = "/home/nvidia//Downloads/certs/icstx22/c9faf68aac-private.pem.key"

    # create client
    client_params = params.get('client', {})
    client = mqtt.Client()

    ssl_context = ssl.create_default_context()
    ssl_context.set_alpn_protocols("x-amzn-mqtt-ca")
    ssl_context.load_cert_chain(certfile=cert, keyfile=private)
    ssl_context.load_verify_locations(cafile=ca)

    #configure tls
    client.tls_set_context(context=ssl_context)

    # configure username and password
    account_params = params.get('account', {})
    if account_params:
        client.username_pw_set(**account_params)

    # configure message params
    message_params = params.get('message', {})
    if message_params:
        inflight = message_params.get('max_inflight_messages')
        if inflight is not None:
            client.max_inflight_messages_set(inflight)
        queue_size = message_params.get('max_queued_messages')
        if queue_size is not None:
            client.max_queued_messages_set(queue_size)
        retry = message_params.get('message_retry')
        if retry is not None:
            client.message_retry_set(retry)

    # configure userdata
    userdata = params.get('userdata', {})
    if userdata:
        client.user_data_set(userdata)

    # configure will params
    will_params = params.get('will', {})
    if will_params:
        client.will_set(**will_params)

    return client


def create_private_path_extractor(mqtt_private_path):
    def extractor(topic_path):
        if topic_path.startswith('~/'):
            return '{}/{}'.format(mqtt_private_path, topic_path[2:])
        return topic_path
    return extractor


__all__ = ['default_mqtt_client_factory', 'create_private_path_extractor']