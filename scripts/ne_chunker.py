#!/usr/bin/env python

from concrete import Communication, AnnotationMetadata, Entity, EntityMention, EntitySet, EntityMentionSet, TokenRefSequence
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
        text = communication.text
        augf = AnalyticUUIDGeneratorFactory(communication)
        aug = augf.create()
        entities = {}
        for section in communication.sectionList:
            for sentence in section.sentenceList:
                tokens = [x.text for x in sentence.tokenization.tokenList.tokenList]
                tags = [x.tag for x in sentence.tokenization.tokenTaggingList[-1].taggedTokenList]
                for subtree in nltk.ne_chunk(zip(tokens, tags)).subtrees():
                    if subtree.label() != "S":
                        name = " ".join([x[0] for x in subtree.leaves()])
                        logging.info("Found named entity \"%s\"", name)
                        entities[(name, subtree.label())] = entities.get(name, []) + [EntityMention(uuid=aug.next(),
                                                                                                    entityType=subtree.label(),
                                                                                                    tokens=TokenRefSequence(tokenIndexList=[], tokenizationId=sentence.tokenization.uuid))]
                        
        communication.entitySetList.append(EntitySet(uuid=aug.next(),
                                                     metadata=AnnotationMetadata(timestamp=int(time.time()), tool="nltk"),
                                                     entityList=[Entity(uuid=aug.next(),
                                                                        mentionIdList=[x.uuid for x in v],
                                                                        canonicalName=k[0],
                                                                        type=k[1]) for k, v in entities.iteritems()]))

        communication.entityMentionSetList.append(EntityMentionSet(uuid=aug.next(),
                                                                   metadata=AnnotationMetadata(timestamp=int(time.time()), tool="nltk"),
                                                                   mentionList=sum(entities.values(), [])))

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
    ipfactory = TCompactProtocol.TCompactProtocolFactory()
    opfactory = TCompactProtocol.TCompactProtocolFactory()

    server = TNonblockingServer.TNonblockingServer(processor, transport, ipfactory, opfactory)
    logging.info('Starting the server...')
    server.serve()
