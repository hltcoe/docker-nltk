#!/usr/bin/env python

from concrete import Communication, AnnotationMetadata, ConcreteThriftException
from concrete.services import Annotator
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory

from thrift.transport import TSocket, TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TNonblockingServer

import logging

class CommunicationHandler():
    def __init__(self):
        services = []
        for service in ["sentence.splitter", "word.tokenizer", "pos.tagger", "ne.chunker"]:
            
            transport = TTransport.TFramedTransport(
                TSocket.TSocket(host=service, port=9090)
            )

            protocol = TCompactProtocol.TCompactProtocol(transport)

            client = Annotator.Client(protocol)

            transport.open()
            
            services.append(client)
            
        self.sentence_splitter, self.word_tokenizer, self.pos_tagger, self.ne_chunker = services;

    def annotate(self, communication):
        logging.info("Annotating communication with UUID %s", communication.uuid)
        return self.ne_chunker.annotate(
            self.pos_tagger.annotate(
                self.word_tokenizer.annotate(
                    self.sentence_splitter.annotate(communication))))
            
if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", dest="port", type=int, default=9090)
    options = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    handler = CommunicationHandler()
    processor = Annotator.Processor(handler)
    transport = TSocket.TServerSocket(port=options.port)
    ipfactory = TCompactProtocol.TCompactProtocolFactory()
    opfactory = TCompactProtocol.TCompactProtocolFactory()

    server = TNonblockingServer.TNonblockingServer(processor, transport, ipfactory, opfactory)

    logging.info('Starting the server...')
    server.serve()
