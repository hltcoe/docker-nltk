#!/usr/bin/env python

from concrete import Communication, AnnotationMetadata, Tokenization, TokenList, Token, TokenizationKind
from concrete.services import Annotator
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory

from thrift.transport import TSocket, TTransport
from thrift.protocol import TCompactProtocol
from thrift.server import TNonblockingServer

import time
import logging

import nltk

class CommunicationHandler():
    def annotate(self, communication):
        print communication.id
        augf = AnalyticUUIDGeneratorFactory(communication)
        aug = augf.create()
        for section in communication.sectionList:
            for sentence in section.sentenceList:
                text = communication.text[sentence.textSpan.start:sentence.textSpan.ending]
                sentence.tokenization = Tokenization(uuid = aug.next(),
                                                     kind = TokenizationKind.TOKEN_LIST,
                                                     tokenList = TokenList(tokenList=[]),
                                                     tokenTaggingList = [],
                                                     metadata = AnnotationMetadata(timestamp=int(time.time()), tool="nltk"))
                                                     
                for i, token in enumerate(nltk.word_tokenize(text)):
                    logging.info("Found token %s", token)
                    sentence.tokenization.tokenList.tokenList.append(Token(tokenIndex=i, text=token))
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
