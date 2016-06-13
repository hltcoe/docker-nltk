#!/usr/bin/env python

from concrete import Communication, AnnotationMetadata, Sentence, TextSpan
from concrete.services import Annotator
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory

from thrift.transport import TSocket, TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TServer

import time
import logging

import nltk

class CommunicationHandler():
    def annotate(self, communication):
        augf = AnalyticUUIDGeneratorFactory(communication)
        aug = augf.create()        

        for section in communication.sectionList:
            text = communication.text[section.textSpan.start:section.textSpan.ending]
            current_offset = section.textSpan.start            
            for sent in nltk.sent_tokenize(text):
                initial = text.find(sent)
                s = Sentence(uuid=aug.next(),
                             textSpan=TextSpan(start=current_offset + initial, ending=current_offset + initial + len(sent)))
                section.sentenceList.append(s)                    
                current_offset = current_offset + initial + len(sent)
                text = communication.text[current_offset:]
        return communication
    
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", type=int, default=9090)
    options = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    handler = CommunicationHandler()
    processor = Annotator.Processor(handler)
    transport = TSocket.TServerSocket(port=options.port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TCompactProtocol.TCompactProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    logging.info('Starting the server...')
    server.serve()
