import pandas as pd
from process import name_map, get_existing
from collections import defaultdict
from copy import deepcopy


def main():
    bids = pd.read_csv("data/all_bids.csv")[["round", "bidder", "tier", "latency", "census_id"]]
    bids["state"] = bids["census_id"] // 10000000000
    bids_unfiltered = bids
    bids = bids.drop_duplicates(subset=["bidder", "census_id"])

    bids["bidder"] = bids["bidder"].map(lambda x: name_map[x] if x in name_map else x)
    bids_unfiltered["bidder"] = bids_unfiltered["bidder"].map(lambda x: name_map[x] if x in name_map else x)

    existing = get_existing()
    bidders = set(bids.bidder.unique())
    all_names = set(existing.names.unique())

    found = defaultdict(set)
    bidders_no_matching = deepcopy(bidders)
    names_no_matching = deepcopy(all_names)

    for bidder in bidders:
        for name in all_names:
            if bidder in name:
                bidders_no_matching.discard(bidder)
                names_no_matching.discard(name)
                found[bidder] |= set(name)

    with open("../outputs/name_analysis/bidders_no_existing.txt", "w") as f:
        for bidder in bidders_no_matching:
            f.write(bidder + "\n")

    with open("../outputs/name_analysis/existing_no_bidders.txt", "w") as f:
        for name in names_no_matching:
            f.write(str(list(name)) + "\n")

    with open("../outputs/name_analysis/found.txt", "w") as f:
        for k, v in found.items():
            f.write(k + ": " + str(v) + "\n")

    for name in names_no_matching:
        print(", ".join(name))
