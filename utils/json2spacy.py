import json
import pickle


def json2spacy(input_file=None, output_file=None):
    try:
        training_data = []
        lines = []
        with open(input_file, "r") as f:
            lines = f.readlines()
        for line in lines:
            data = json.loads(line)
            text = data["content"]
            entities = []
            for annotation in data["annotation"]:
                point = annotation["points"][0]
                labels = annotation["label"]
                if not isinstance(labels, list):
                    labels = [labels]
                for label in labels:
                    entities.append((point["start"], point["end"] + 1, label))
            training_data.append((text, {"entities": entities}))
        with open(output_file, "wb") as fp:
            pickle.dump(training_data, fp)
    except Exception as e:
        print("Unable to process " + input_file + "\n" + "error = " + str(e))
        raise
