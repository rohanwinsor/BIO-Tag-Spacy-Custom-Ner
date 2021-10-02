import json
import pandas as pd
from tqdm import tqdm


def csv2json(input_path, output_path, unknown_label):
    try:
        df = pd.read_csv(input_path, encoding="ISO-8859-1", index_col=False)[:]
        df = df[["Word", "Tag"]]
        input_path = input_path.replace(".csv", ".tsv")
        df.to_csv(input_path, index=False, sep="\t")
        size = df.shape[0]
        f = open(input_path, "r")
        fp = open(output_path, "w")
        data_dict = {}
        annotations = []
        label_dict = {}
        s = ""
        start = 0
        for line in tqdm(f, total=size):
            if line[0 : len(line) - 1] != ".\tO":
                word, entity = line.split("\t")
                s += word + " "
                entity = entity[: len(entity) - 1]
                if entity != unknown_label:
                    if len(entity) != 1:
                        d = {}
                        d["text"] = word
                        d["start"] = start
                        d["end"] = start + len(word) - 1
                        try:
                            label_dict[entity].append(d)
                        except:
                            label_dict[entity] = []
                            label_dict[entity].append(d)
                start += len(word) + 1
            else:
                data_dict["content"] = s
                s = ""
                label_list = []
                for ents in list(label_dict.keys()):
                    for i in range(len(label_dict[ents])):
                        if label_dict[ents][i]["text"] != "":
                            l = [ents, label_dict[ents][i]]
                            for j in range(i + 1, len(label_dict[ents])):
                                if (
                                    label_dict[ents][i]["text"]
                                    == label_dict[ents][j]["text"]
                                ):
                                    di = {}
                                    di["start"] = label_dict[ents][j]["start"]
                                    di["end"] = label_dict[ents][j]["end"]
                                    di["text"] = label_dict[ents][i]["text"]
                                    l.append(di)
                                    label_dict[ents][j]["text"] = ""
                            label_list.append(l)

                for entities in label_list:
                    label = {}
                    label["label"] = [entities[0]]
                    label["points"] = entities[1:]
                    annotations.append(label)
                data_dict["annotation"] = annotations
                annotations = []
                json.dump(data_dict, fp)
                fp.write("\n")
                data_dict = {}
                start = 0
                label_dict = {}
    except Exception as e:
        print("Unable to process file" + "\n" + "error = " + str(e))
        raise
