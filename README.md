# Basic NLTK-based Named Entity Recognition Pipeline

## Components

The pipeline is composed of several Docker containers:

1. Sentence splitter
2. Word tokenizer
3. Part-of-speech tagger
4. Named-entity chunker

Each container runs a single process, a server that implements the Concrete Thrift service *Annotator* on port 9090.  *Annotator* supports a method ```annotate :: Communication -> Communication```, and we call Docker containers like this an *Analytic*.  They accept Communications, and return them with some annotation.  In principle, any of these analytics could be used in isolation by passing Communications directly to it, but different analytics depend on preexisting annotations: the tagger has to know what the tokens are, the tokenizer has to know what the sentences are, and so forth.  Encoding these annotations in Concrete objects is a tedious process, so we'll create one more Docker container:

### Top-level composite analytic

This container also implements the *Annotator* interface, but it's only job is to accept minimal Communications (e.g. where only the *text* field is filled in) and pass them through the other containers in the appropriate order.  We'll only expose this top-level container as a service, and so from other applications' perspectives it appears like a single analytic that provides four types of annotation.

Finally, there is a trivial web interface with a text box for the user to submit communications to the pipeline and display all named entities it finds.

## Building pipeline

Assuming you have Docker, Docker Compose, and Git installed, building and running the pipeline is trivial:

```
git clone https://gitlab.hltcoe.jhu.edu/lippincott/docker-nltk.git
cd docker-nltk
docker-compose build --force-rm
docker-compose up
```

Now, you should have the top-level analytic listening on port 9090.

## Using the pipeline

The file ```scripts/concrete_annotator_client.py``` implements the *Client* aspect of the *Annotator* interface, and can be used to connect to the pipeline:

```
python scripts/concrete_annotator_client.py -p 9090
```

This will let you enter text, run it through the pipeline, and print out any named entities that were found:

```
Write some text > John went to Philadelphia.  While there, he met Sue.
GSP Philadelphia
PERSON John
PERSON Sue
```

Note this *isn't* showing the full annotated communication, which now has sentence, token, part-of-speech, and named-entity information (this would be an *ugly* object) but you could easily modify ```scripts/concrete_annotator_client.py``` to see it.  Or to run in batch mode over a database of communications.  Or...

## Caveats and potential improvements

This is a *tremendously simple* example: each container is actually the same Docker image, just running different server code.  This is because the analytics are all the default solutions from NLTK, and so the dependencies are identical.  However, since the analytics are decoupled, it would be easy to swap in a different e.g. part-of-speech tagger analytic that uses the same tag inventory.

The code for each analytic server (in the ```scripts/``` directory) has a ton of duplication that could be factored out.  However, if your analytics were more diverse, this would be less the case: for example, in this pipeline none of the analytic servers need to be passed any arguments or model paths, but real-life analytics will need more involved initialization, might need special data manipulation, etc.  At the end of the day though, the *Annotator* interface is all the end-user should need to understand.

## Further resources

[Docker build file reference](https://docs.docker.com/engine/reference/builder/)

[Docker Compose reference](https://docs.docker.com/compose/compose-file/)

[Concrete data specification](https://github.com/hltcoe/concrete)
