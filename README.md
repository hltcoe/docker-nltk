# Basic NLTK-based Named Entity Recognition Pipeline

## Components

The pipeline is composed of several Docker containers:

1. Sentence splitter
2. Word tokenizer
3. Part-of-speech tagger
4. Named-entity chunker

Each container runs a single process, a server that implements the Concrete Thrift service *Annotator* on port 9090.  *Annotator* supports a method ```annotate :: Communication -> Communication```, and we call Docker containers like this an *Analytic*.  They accept Communications, and return them with some annotation.  In principle, any of these analytics could be used in isolation by passing Communications directly to it, but different analytics depend on preexisting annotations: the tagger has to know what the tokens are, the tokenizer has to know what the sentences are, and so forth.  Encoding these annotations in Concrete objects is a tedious process, so we'll create one more Docker container:

5. Top-level composite analytic

This container also implements the *Annotator* interface, but it's only job is to accept minimal Communications (e.g. where only the *text* field is filled in) and pass them through the other containers in the appropriate order.  We'll only expose this top-level container to the users, and so from their perspective it appears like a single analytic that provides four types of annotation.

## Building pipeline

Assuming you have Docker, Docker Compose, and Git installed, building and running the pipeline is trivial:

```
git clone https://gitlab.hltcoe.jhu.edu/lippincott/docker-nltk.git
cd docker-nltk
docker-compose build
docker up
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

## Running on the muinigrid

Doing all of this on the minigrid is basically identical, although if you want to make the pipeline accessible e.g. to your laptop, you will have to perform some port-forwarding.  This is out-of-scope, but if you use SSH aliases as described [here](https://gitlab.hltcoe.jhu.edu/mini-grid/wiki/wikis/ssh-tricks), you can log into the minigrid with something like:

```
ssh r6n33 -L 9090:localhost:9090
```

and when you run the pipeline on ```r6n33```, you can access the pipeline at port 9090 on your local machine.

## Caveats and potential improvements

## Further resources