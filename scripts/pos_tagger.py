#!/usr/bin/env python

from concrete import Communication, AnnotationMetadata, TokenTagging, TaggedToken
from concrete.services import Annotator
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory

from thrift.transport import TSocket, TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TServer
from thrift.server import TNonblockingServer

import time
import logging

import nltk

class CommunicationHandler():
    def annotate(self, communication):
        text = communication.text
        augf = AnalyticUUIDGeneratorFactory(communication)
        aug = augf.create()
        for section in communication.sectionList:
            for sentence in section.sentenceList:
                tokens = [x.text for x in sentence.tokenization.tokenList.tokenList]
                sentence.tokenization.tokenTaggingList.append(TokenTagging(uuid=aug.next(),
                                                                           metadata=AnnotationMetadata(timestamp=int(time.time()), tool="nltk"),
                                                                           taggedTokenList=[],
                                                                           taggingType="Penn Treebank"))
                for i, (tok, tag) in enumerate(nltk.pos_tag(tokens)):
                    logging.info("Tagged %s as %s", tok, tag)
                    sentence.tokenization.tokenTaggingList[-1].taggedTokenList.append(TaggedToken(tokenIndex=i, tag=tag))

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
    ipfactory = TCompactProtocol.TCompactProtocolFactory()
    opfactory = TCompactProtocol.TCompactProtocolFactory()

    server = TNonblockingServer.TNonblockingServer(processor, transport, ipfactory, opfactory)
    logging.info('Starting the server...')
    server.serve()
