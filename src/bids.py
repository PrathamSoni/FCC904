import pandas as pd
from collections import defaultdict

from process import get_census, get_processed_bids, get_bids, get_existing, get_county_shapes, name_map
from distance import get_distances
from utils import run_func


def get_number_with_neighbors(cell):
    counter = 0
    for bidder, data in cell.items():
        if data["neighbor_status"] not in [0]:  # counts satellites as local competitor always
            counter += 1
    return counter


def get_collapsed_bid_table(bidders):
    def subprocess(bidders):
        new_table = defaultdict(dict)
        for idx, row in processed_bids.iterrows():
            id = row["GEOID"]
            bidder = row["bidder"]
            if "bidders" not in new_table[id]:
                new_table[id]["bidders"] = dict()

            new_table[id]["bidders"][bidder] = {"neighbors": row["neighbors"], "round": row["round"],
                                                "neighbor_status": row["neighbor_status"]}
            if row["winner"]:
                new_table[id]["winner"] = bidder
                new_table[id]["blocks"] = row["won_blocks"]
                new_table[id]["round"] = row["round"]
                new_table[id]["neighbor_status"] = row["neighbor_status"]
                new_table[id]["all_neighbors"] = row["all_neighbors"]
                new_table[id]["geometry"] = row["geometry"]
                new_table[id]["population"] = row["B01001e1"]
                new_table[id]["age"] = row["B01002e1"]

        collapsed_bids = pd.DataFrame.from_dict(new_table, orient='index')
        collapsed_bids = collapsed_bids.reset_index().rename(columns={"index": "GEOID"})
        collapsed_bids = collapsed_bids.merge(bidders, how="left", left_on="winner", right_on="bidder").drop(
            columns=["bidder"])

        collapsed_bids["competition bidders"] = collapsed_bids.apply(lambda x: get_number_with_neighbors(x.bidders),
                                                                     axis=1)
        collapsed_bids["num_bidders"] = collapsed_bids.apply(lambda x: len(x.bidders), axis=1)
        return collapsed_bids

    return run_func(subprocess, "../outputs/collapsed_bids.pkl", bidders)


def get_second_best(bidders, winner):
    max_sat = 0
    max_existing = 0
    max_neighbor = 0
    max_wild_tract = 0
    second_highest = set()
    second_bid = 0

    for name, values in bidders.items():
        bid = values["round"]
        neighbor_status = values["neighbor_status"]
        if name != winner:
            if bid > 13:
                if bid >= second_bid:
                    if bid > second_bid:
                        second_bid = bid
                        second_highest.clear()
                    second_highest.add(neighbor_status)
                if neighbor_status == 0:
                    max_wild_tract = max(max_wild_tract, bid - 13)
                if neighbor_status == 1:
                    max_neighbor = max(max_neighbor, bid - 13)
                if neighbor_status == 2:
                    max_existing = max(max_existing, bid - 13)
                if neighbor_status == 3:
                    max_sat = max(max_sat, bid - 13)

    winning_round = None
    winner_neighbor_dummy = None
    winner_existing_dummy = None
    winner_sat_dummy = None
    winner_wild_tract_dummy = None
    if type(winner) == str:
        winner_values = bidders[winner]
        winning_round = winner_values["round"]
        winner_wild_tract_dummy = 0 == winner_values["neighbor_status"]
        winner_neighbor_dummy = 1 == winner_values["neighbor_status"]
        winner_existing_dummy = 2 == winner_values["neighbor_status"]
        winner_sat_dummy = 3 == winner_values["neighbor_status"]

    return max_wild_tract, max_neighbor, max_existing, max_sat, 0 in second_highest, 1 in second_highest, 2 in second_highest, 3 in second_highest, winning_round, winner_wild_tract_dummy, winner_neighbor_dummy, winner_existing_dummy, winner_sat_dummy


# should all be in process
def get_composite_table(processed_bids):
    def subprocess(processed_bids):
        # should be in process (gives won blocks to all bidder rows)
        won_blocks = processed_bids[processed_bids.winner][["GEOID", "won_blocks"]]
        new = processed_bids.drop("won_blocks", axis=1).merge(won_blocks, how="left", left_on="GEOID",
                                                              right_on="GEOID").copy()
        new = new.drop(['neighbors', 'geometry', 'num_blocks_won', 'census_block_group', 'all_neighbors'], axis=1)

        new_columns = pd.DataFrame(
            collapsed_bids.apply(lambda x: get_second_best(x.bidders, x.winner), axis=1).tolist(),
            index=collapsed_bids.GEOID,
            columns=["max_wild_tract",
                     "max_neighbor",
                     "max_existing",
                     "max_sat",
                     "second_wild_tract_dummy",
                     "second_neighbor_dummy",
                     "second_existing_dummy",
                     "second_sat_dummy",
                     "winner_round",
                     "winner_wild_tract_dummy",
                     "winner_neighbor_dummy",
                     "winner_existing_dummy",
                     "winner_sat_dummy",
                     ]).reset_index()
        new = new.merge(new_columns)

        new["wild_tract_dummy"] = new["neighbor_status"] == 0
        new["neighbor_dummy"] = new["neighbor_status"] == 1
        new["existing_dummy"] = new["neighbor_status"] == 2
        new["sat_dummy"] = new["neighbor_status"] == 3
        new = new.drop('neighbor_status', axis=1)
        new = new * 1

        item_info = pd.read_csv("../data/item_status.csv")[
            ["census_id", "reserve_price", "locations"]].drop_duplicates()
        new = new.merge(item_info, how="left", left_on="GEOID", right_on="census_id")

        new["reserve_price_per_location"] = new["reserve_price"] / new["locations"]
        new["final_price"] = (new["round"] - 1) / 18 * new["reserve_price"]
        new["final_price_per_location"] = new["final_price"] / new["locations"]

        new.to_csv("../outputs/composite_table.csv")
        return new

    return run_func(subprocess, "../outputs/composite_table.pkl", processed_bids)


if __name__ == "__main__":
    # move this into process
    raw_bids = pd.read_csv("../data/all_bids.csv")
    bidders = raw_bids.groupby("bidder").agg({"t+l_weight": "first", "tier": "first", "latency": "first"}).reset_index()
    bidders["bidder"] = bidders["bidder"].map(lambda x: name_map[x] if x in name_map else x)

    bids = get_bids()
    existing = get_existing()
    county_shapes = get_county_shapes()
    processed_bids = get_processed_bids(bids, existing, None, county_shapes, None)

    collapsed_bids = get_collapsed_bid_table(bidders)

    # should be in process
    partial_table = collapsed_bids[["GEOID", "num_bidders"]]
    processed_bids = processed_bids.merge(partial_table, how="left")

    composite_table = get_composite_table(processed_bids)
