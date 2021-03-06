import pickle
import random
from pathlib import Path
import spacy
from utils.csv2json import csv2json
from utils.json2spacy import json2spacy
from spacy.util import minibatch, compounding
from tqdm import trange


def inference(output_path, text):
    nlp2 = spacy.load(output_path)
    doc2 = nlp2(text)
    output = [[ent.label_, ent.text] for ent in doc2.ents]
    return output


def train(
    data_path,
    labels,
    model=None,
    new_model_name="new_model",
    output_dir=None,
    n_iter=10,
):
    with open(data_path, "rb") as fp:
        TRAIN_DATA = pickle.load(fp)
    """Setting up the pipeline and entity recognizer, and training the new entity."""
    if model is not None:
        nlp = spacy.load(model)
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")
        print("Created blank 'en' model")
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner)
    else:
        ner = nlp.get_pipe("ner")
    for i in labels:
        ner.add_label(i)
    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.entity.create_optimizer()

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        for itn in trange(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for idx, batch in enumerate(batches):
                print(idx)
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35, losses=losses)
            print("Losses", losses)

    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta["name"] = new_model_name
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)


if __name__ == "__main__":

    csv2json("ner_datasetreference.csv", "new.json", "abc")
    json2spacy("new.json", "new_ner_corpus_260")
    LABEL = [
        "Tag",
        "I-geo",
        "B-geo",
        "I-art",
        "B-art",
        "B-tim",
        "B-nat",
        "B-eve",
        "O",
        "I-per",
        "I-tim",
        "I-nat",
        "I-eve",
        "B-per",
        "I-org",
        "B-gpe",
        "B-org",
        "I-gpe",
    ]
    train(
        "new_ner_corpus_260",
        LABEL,
        "en",
        new_model_name="new_model",
        output_dir="output",
        n_iter=10,
    )
    text = "Gianni Infantino is the president of FIFA."
    out = inference("output", text)
    print(out)
