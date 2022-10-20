import pandas as pd
from tqdm import tqdm
from functools import reduce


def main():
    features = ["B01001e1", "B01002e1"]

    list_tables = []
    stubs = set([feature[:3].lower() for feature in features])
    files_map = {f"../data/safegraph_open_census_data_2019/data/cbg_{stub}.csv": [feature for feature in features if feature[:3].lower()==stub] for stub in stubs}
    for file, features in tqdm(files_map.items()):
        keys = ["census_block_group"] + features
        table = pd.read_csv(file, usecols=keys)
        list_tables.append(table)
    df_merged = reduce(lambda left, right: pd.merge(left, right, on=['census_block_group'],
                                                    how='outer'), list_tables)
    df_merged.to_pickle("../outputs/all_census_data.pkl")


if __name__ == "__main__":
    main()
