from concrete import Communication, AnnotationMetadata, Section, TextSpan
from concrete.services import Annotator
from concrete.util.concrete_uuid import AnalyticUUIDGeneratorFactory
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol

import re
import time

from bottle import route, run, template, request

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", dest="port", default=8080)
    parser.add_argument("--host", dest="host", default="0.0.0.0")
    parser.add_argument("--annotator-port", dest="annotator_port", default=9090)
    parser.add_argument("--annotator-host", dest="annotator_host", default="ne.annotator")
    options = parser.parse_args()

    @route("/")
    def index():
        return '''
        <form action="/" method="post">
        Enter or paste some text: <input name="text" type="text" />
        <input value="Submit" type="submit" />
        </form>
        '''

    @route('/', method='POST')
    def index():
        text = request.forms.get('text')
        transport = TSocket.TSocket(options.annotator_host, options.annotator_port)
        transport = TTransport.TFramedTransport(transport)
        protocol = TCompactProtocol.TCompactProtocol(transport)
        client = Annotator.Client(protocol)
        transport.open()
        augf = AnalyticUUIDGeneratorFactory()
        aug = augf.create()
        c = Communication(id="",
                          text=text,
                          uuid=aug.next(),
                          type="user-supplied input",
                          metadata=AnnotationMetadata(timestamp=int(time.time()), tool="stdin"),
                          sectionList=[Section(uuid=aug.next(), sentenceList=[], kind="paragraph", textSpan=TextSpan(start=0, ending=len(text)))],
                          entitySetList=[],
                          entityMentionSetList=[],
        )
            
        new_c = client.annotate(c)
        form = '''<form action="/" method="post">
        Enter or paste some text: <input name="text" type="text" />
        <input value="Submit" type="submit" />
        </form>
        '''
        return form + "\n".join(["<h3>%s</h3>" % text] + ["\n".join(["<br>%s %s" % (e.type, e.canonicalName) for e in es.entityList]) for es in new_c.entitySetList])

    
    run(host=options.host, port=options.port)
