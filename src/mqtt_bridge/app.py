#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import inject
import paho.mqtt.client as mqtt
import rospy
from pdb import set_trace as bp
from six import string_types as basestring
import ssl
import paho.mqtt.client as mqtt



from .bridge import create_bridge
from .mqtt_client import default_mqtt_client_factory
from .util import lookup_object





def create_config(mqtt_client, serializer, deserializer, mqtt_private_path):
    if isinstance(serializer, basestring):
        serializer = lookup_object(serializer)
    if isinstance(deserializer, basestring):
        deserializer = lookup_object(deserializer)
    private_path_extractor = create_private_path_extractor(mqtt_private_path)
    def config(binder):
        binder.bind('serializer', serializer)
        binder.bind('deserializer', deserializer)
        binder.bind(mqtt.Client, mqtt_client)
        binder.bind('mqtt_private_path_extractor', private_path_extractor)
    return config


def mqtt_bridge_node():
    # init node
    rospy.init_node('mqtt_bridge_node')


    IoT_protocol_name = "x-amzn-mqtt-ca"
    aws_iot_endpoint = "a33ymm5qqy1bxl.iot.us-east-2.amazonaws.com" # <random>.iot.<region>.amazonaws.com
    url = "https://{}".format(aws_iot_endpoint)

    ca = "/home/nvidia/Downloads/certs/icstx22/Amazon_Root_CA_1.pem" 
    cert = "/home/nvidia/Downloads/certs/icstx22/c9faf68aac-certificate.pem.crt"
    private = "/home/nvidia//Downloads/certs/icstx22/c9faf68aac-private.pem.key"

    # load parameters
    params = rospy.get_param("~", {})
    mqtt_params = params.pop("mqtt", {})
    conn_params = mqtt_params.pop("connection")
    mqtt_private_path = mqtt_params.pop("private_path", "")
    bridge_params = params.get("bridge", [])

    # create mqtt client
    # mqtt_client_factory_name = rospy.get_param(
    #     "~mqtt_client_factory", ".mqtt_client:default_mqtt_client_factory")
    # mqtt_client_factory = lookup_object(mqtt_client_factory_name)
    ssl_context = ssl.create_default_context()
    ssl_context.set_alpn_protocols([IoT_protocol_name])
    ssl_context.load_cert_chain(certfile=cert, keyfile=private)
    ssl_context.load_verify_locations(cafile=ca)

    # load serializer and deserializer
    serializer = params.get('serializer', 'json:dumps')
    deserializer = params.get('deserializer', 'json:loads')

    # dependency injection
    # config = create_config(
    #     mqtt_client, serializer, deserializer, mqtt_private_path)
    # inject.configure(config)

    # configure and connect to MQTT broker
    mqtt_client = mqtt.Client()
    mqtt_client.tls_set_context(context=ssl_context)
    mqtt_client.on_connect = _on_connect
    mqtt_client.on_disconnect = _on_disconnect
    aws_iot_endpoint = "a33ymm5qqy1bxl.iot.us-east-2.amazonaws.com" # <random>.iot.<region>.amazonaws.com
    bp()
    mqtt_client.connect(aws_iot_endpoint, port=443)

    # configure bridges
    bridges = []
    for bridge_args in bridge_params:
        bridges.append(create_bridge(**bridge_args))

    # start MQTT loop
    mqtt_client.loop_start()

    # register shutdown callback and spin
    rospy.on_shutdown(mqtt_client.disconnect)
    rospy.on_shutdown(mqtt_client.loop_stop)
    rospy.spin()


def _on_connect(client, userdata, flags, response_code):
    rospy.loginfo('MQTT connected')


def _on_disconnect(client, userdata, response_code):
    rospy.loginfo('MQTT disconnected')


__all__ = ['mqtt_bridge_node']
