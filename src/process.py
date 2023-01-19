import pandas as pd
import time
import geopandas
from glob import glob
from shapely.ops import cascaded_union
from collections import defaultdict
from utils import run_func
from functools import reduce

name_map = {
    "CCO Holdings, LLC": "Charter Communications Inc",
    "Windstream Services LLC, Debtor-In-Possession": "Windstream Holdings, Inc.",
    "Connect Everyone LLC": "Starry, Inc.",
    "Frontier Communications Corporation, DIP": "Frontier Communications Corporation",
    "California Internet, L.P. dba GeoLinks": "GeoLinks",
    "Etheric Communications LLC": "Etheric Networks, Inc.",
    "Consolidated  Communications, Inc.": "Consolidated Communications, Inc.",
    "Frontier Communications Northwest, LLC": "Ziply Fiber",
    "Citynet West Virginia, LLC": "Citynet, LLC",
    "Computer 5, Inc. d/b/a LocalTel Communications": "LocalTel Communications",
    "Armstrong Telephone Company - Northern Division": "Armstrong Holdings, Inc.",
    "Commnet Wireless, LLC": "ATN International, Inc.",
    "Mediacom Communications Corporation": "Mediacom Communications Corp.",
    "Continental Divide Electric Cooperative": "Continental Divide Electric Cooperative, Inc.",
    "South Arkansas Telephone Company": "South Arkansas Telephone Co.",
    "Digital Connections Inc. dba PRODIGI": "Digital Connections, Inc.",
    "Shenandoah Cable Television, LLC": "Shenandoah Telecommunications Company",
    "Direct Communications Rockland, Inc": "Direct Communications Rockland, Inc.",
    "Pine Belt Communications, Inc.": "Pine Belt Communications Co. Inc.",
    "Savage Communications": "Savage Communications Inc.",
    "Hamilton County Telephone Co-op": "Hamilton County Telephone Co-Op",
    "Hotwire Communications, Ltd": "Hotwire Communications Ltd.",
    "Altice USA, Inc.": "Altice",
    "TruVista Communications, Inc.": "TruVista Communications of Georgia, LLC",
    "Hawaii Dialogix Telecom LLC": "Hawaii Dialogix Telecom LLC",
    "Safelink Internet LLC": "Safelink Internet",
    "American Heartland": "Farmers Telephone Company",
    "Cellular Services LLC.": "Cellular Services LLC",
    "Scott County Telephone Cooperative, Inc.": "Scott County",
    "Micrologic Inc.": "Micrologic, Inc.",
    "Pioneer Wireless, Inc": "Pioneer Wireless, Inc.",
    "St. John Telco": "St. John Telephone, Inc.",
    "One Ring Networks, Inc": "One Ring Networks, Inc.",
    "Emery Telephone dba Emery Telcom": "Emery Telcom",
    "XIT Telecommunication & Technology": "XIT Rural Telephone Cooperative, Inc.",
    "Somerset Telephone Co., Inc.": "SOMERSET TELEPHONE COMPANY",
    "Siuslaw Broadband, LLC dba Hyak Technologies": "Siuslaw Broadband, LLC",
    "Minnesota Connections c/o Consolidated Tel Company": "Consolidated Telephone Company",
    "DoCoMo Pacific, Inc.": "Docomo Pacific",
    "Roseau Electric Cooperative, Inc.": "Roseau Electric Cooperative",
    "Custer Telephone Cooperative, Inc.": "Custer Telephone Cooperative Inc.",
    "Lakeland Communications Group, LLC": "Lakeland Communications, Inc.",
    "LigTel Communications, Inc.": "Ligtel Communications",
    "Hamilton Long Distance Company": "Hamilton.net, Inc.",
    "Allen's T.V. Cable Service, Inc.": "Allen's TV Cable Service, Inc.",
    "W. T. Services, Inc.": "W.T. Services, Inc.",
    "Heart of the Catskills Comm. Inc., dba MTC Cable": "MTC Cable",
    "Citizens Vermont Acquisition Corporation": "Citizens Telephone Company",
    "Nova Cablevision, Inc": "Nova Cablevision, Inc.",
    "yondoo Broadband LLC": "yondoo Broadband, LLC",
    "Baraga Telephone Company": "Baraga Telephone Company Inc.",
    "Miles Communications LLC": "Miles Communications, Inc.",
    "PVT NetWorks, Inc.": "Penasco Valley Telephone Cooperative, Inc.",
    "Yucca Telecommunications Systems, Inc.": "Yucca Telecom",
    "H&B Communication's, Inc.": "H&B Enterprises Inc.",
    "MARQUETTE-ADAMS TELEPHONE COOPERATIVE, INC.": "Marquette-Adams Telephone Cooperative, Inc.",
    "Pinpoint Bidding Coalition": "Pinpoint Holdings, Inc.",
    "Computer Techniques, Inc. dba CTI Fiber": "CTI Fiber",
    "Barry Technology Services, LLC": "Barry Technology Services",
    "Bloosurf, LLC": "Bloosurf",
    "St Paul Cooperative Telephone Association": "St Paul Coop Telephone Assoc",
    "Farmers Mutual Cooperative Telephone Company": "FARMERS MUTUAL TELEPHONE COMPANY",
    "NTS Communications, LLC": "NTS, Inc.",
    "Unified Communications Inc.": "Unified Communications, Inc.",
    "Peoples Communication, LLC.": "Peoples Communication, Inc.",
    "Wood County Telephone Company d/b/a Solarus": "Solarus",
    "Comcell Inc.": "Comcell, Inc.",
    "Taylor Telephone Coop., Inc. dba Taylor Telecom": "Taylor Telephone Cooperative, Inc.",
    "Plateau Telecommunications, Incorporated": "Plateau",
    "AMA Communications, LLC": "AMA Communicaitons, L.L.C.",
    "AirCell, Inc.": "AirCell",
    "Bays-ET Highspeed LLC": "Bays-ET Highspeed Internet LLC",
    "Big Bend Telecom LTD": "Big Bend Telephone Company, Inc.",
    "Blue Ridge Cable Technologies, Inc.": "Blue Ridge Cable Technologies, Inc.",
    "Cass Cable TV, Inc.": "Cass Cable TV, Inc.",
    "City of Wilson GreenLight": "City of Wilson",
    "Climax Telephone Company dba CTS Telecom, Inc.": "Climax Telephone Company",
    "Cumberland Telephone Company, Inc": "CUMBERLAND TELEPHONE COMPANY",
    "Cumby Telephone Coooertive, Inc.": "Cumby Telephone Coop., Inc.",
    "Data Stream Mobile Technoligies Inc.": "Data Stream",
    "Get Wireless Inc": "Getwireless.net",
    "Hartington Telecommunications Co., Inc,": "Hartington Telecommunications Co., Inc.",
    "Hilliary Communications Consortium": "Hilliary Communications, LLC",
    "Hillsboro Telephone Company,  Inc.": "Hillsboro Telephone Company",
    "Home Telephone ILEC, LLC": "Home Telephone ILEC, LLC d/b/a Home Telecom",
    "Hood Canal Telephone Co., Inc": "Hood Canal Communications",
    "Kingdom Telecommunications, Inc.": "Kingdom Telecommunications Inc",
    "Lincolnville Communications": "Lincolnville Telephone Company",
    "Local Internet Service Company, Inc.": "Local Internet Service Company",
    "Martell Enterprise  Inc.": "Martell Enterprises, Inc.",
    "Massena Telephone Company, Inc.": "Massena Telephone Company",
    "Moundridge Telephone Company": "Moundridge Telephone Co.",
    "MyServer.org, Inc dba San Diego Broadband": "San Diego Broadband",
    "Newbreak Management, LLC": "Newbreak Communications",
    "NexGenAccess Incorporated": "NexGenAccess",
    "Northwoods Communication Technologies, LLC": "Northwoodsconnect",
    "One Point Technologies Inc": "One Point Technologies Inc.",
    "Panhandle Telecommunication Systems, Inc.": "Panhandle Telephone Cooperative, Inc.",
    "Pathwayz Communications Inc": "Pathwayz Communications, Inc.",
    "RONAN TELEPHONE COMPANY": "Ronan Telephone Co",
    "Rainbow Communications LLC": "Rainbow Telecommunications Association, Inc.",
    "SOUTHWEST ARKANSAS TELEPHONE COOPERATIVE, INC.": "Southwest Arkansas Telephone Cooperative, Inc.",
    "South Central Wireless, Inc.": "South Central Wireless Inc.",
    "Southern Montana Telephone Company (SMTC)": "Southern Montana Telephone Company",
    "Steelville Telephone Exchange Inc.": "Steelville Telephone Exchange Inc",
    "Tekstar Communications, Inc. dba Arvig": "Arvig Enterprises, Inc.",
    "Upsala Cooperative Telephone Association dba Sytek": "UPSALA COOPERATIVE TELEPHONE ASSOCIATION",
    "Valley Telephone Cooperative, Inc": "Valley Telephone Cooperative, Inc.",
    "Velocity.Net Communications, Inc.": "Velocity Communications, Inc.",
    "Woodstock Telephone Co.": "Woodstock Telephone Company",
    "ZIRKEL Wireless, LLC": "Zirkel Wireless",
    "coon valley cooperative telephone association inc.": "Coon Valley Co-op Telephone Association, Inc.",
}


def get_bids():
    def subprocess():
        bids = pd.read_csv("../data/all_bids.csv")[["round", "bidder", "tier", "latency", "census_id"]]
        bids["state"] = bids["census_id"] // 10000000000
        bids = bids.groupby(["bidder", "census_id"]).agg({'round': 'max', 'state': 'first'}).reset_index()
        bids["bidder"] = bids["bidder"].map(lambda x: name_map[x] if x in name_map else x)
        return bids

    return run_func(subprocess, "../data/bids.pkl")


def get_existing():
    def subprocess():
        existing = pd.read_csv("../data/existing_service.csv", encoding="latin")
        existing["bg"] = existing["BlockCode"] // 1000
        existing = existing.loc[
            (existing["MaxAdDown"] >= 25) & (existing["MaxAdUp"] >= 3) & (existing["TechCode"] != 60)]
        existing["state"] = existing["bg"] // 10000000000
        existing['names'] = [frozenset(x) for x in
                             zip(existing.ProviderName, existing.HoldingCompanyName, existing.DBAName,
                                 existing.HocoFinal)]
        return existing

    return run_func(subprocess, "../data/existing.pkl")


def get_winners():
    def subprocess():
        winners = pd.read_csv("../data/all_assigned_census_blocks.csv")[["bidder", "block_id", "state", "census_id"]]
        winners = winners.groupby(['bidder', 'census_id'], as_index=False).agg({"block_id": list, "state": "first"})
        winners["bidder"] = winners["bidder"].map(lambda x: name_map[x] if x in name_map else x)
        return winners

    return run_func(subprocess, "../data/winners.pkl")


def get_county_shapes():
    def subprocess():
        shapefiles = glob("../data/all_data/*.shp")
        county_shapes = []
        for file in shapefiles:
            county_shapes.append(geopandas.read_file(file))

        county_shapes = pd.concat(county_shapes)[["STATEFP", "COUNTYFP", "TRACTCE", "BLKGRPCE", "GEOID", "geometry"]]
        county_shapes["GEOID"] = pd.to_numeric(county_shapes["GEOID"])
        return county_shapes

    return run_func(subprocess, "../data/county_shapes.pkl")


def get_state_shapes(county_shapes):
    def subprocess():
        state_shapes = county_shapes.groupby("STATEFP")["geometry"].apply(list).reset_index(name="geometry")
        state_shapes["geometry"] = state_shapes["geometry"].apply(cascaded_union)
        state_shapes = geopandas.GeoDataFrame(state_shapes)
        for index, row in state_shapes.iterrows():
            neighbors = state_shapes[~state_shapes.geometry.disjoint(row['geometry'])]
            state_shapes.at[index, "neighbors"] = ", ".join(neighbors.STATEFP.tolist())
        return state_shapes

    return run_func(subprocess, "../data/state_shapes.pkl")


def neighbor_status(census_id, neighbors, satellite):
    if satellite:
        return 3
    neighbors_set = set(neighbors)
    if len(neighbors_set) == 0:
        return 0
    elif census_id in neighbors:
        return 2
    else:
        return 1


# this can be re-written with distance logic
def get_processed_bids(bids, existing, winners, county_shapes, state_shapes):
    def subprocess():
        with open("../outputs/neighbors.log", "w") as log:
            pass

        total_time = 0
        processed_bid_list = []
        for state_code in state_shapes["STATEFP"].tolist():
            print(state_code)
            start = time.time()
            state_bids = bids.loc[bids["state"] == int(state_code)]
            state_bids = state_bids.groupby("census_id").agg({"bidder": list, "round": list}).reset_index()
            state_bids = state_bids.merge(county_shapes, left_on="census_id", right_on="GEOID")

            neighbors = state_shapes.loc[state_shapes["STATEFP"] == state_code]["neighbors"].item().split(", ")
            neighbors = [int(n) for n in neighbors]
            state_existing = existing.loc[existing["state"].isin(neighbors)]
            state_existing = state_existing.groupby("bg")["names"].apply(set).reset_index(name="names")
            state_existing = state_existing.merge(county_shapes, left_on="bg", right_on="GEOID")
            state_existing = geopandas.GeoDataFrame(state_existing)

            for index, row in state_bids.iterrows():
                bidders = row["bidder"]
                rounds = dict(zip(bidders, row["round"]))
                bg = row.census_id

                neighbors = state_existing[~state_existing.geometry.disjoint(row['geometry'])]
                ids = neighbors.GEOID.tolist()
                list_set_set_names = neighbors.names.tolist()
                neighbors_dict = dict(zip(ids, list_set_set_names))

                winner_data = winners.loc[winners.census_id == bg]
                winner_bidder = winner_data.bidder.tolist()
                winner_blocks = winner_data.block_id.tolist()
                winner_bidder = winner_bidder[0] if len(winner_bidder) == 1 else None
                winner_blocks = winner_blocks[0] if len(winner_blocks) == 1 else []

                bids_with_neighbors = defaultdict(list)
                for nbg, nexisting_names in neighbors_dict.items():
                    for nexisting_name in nexisting_names:
                        for bidder in bidders:
                            if bidder in nexisting_name:
                                bids_with_neighbors[bidder].append(nbg)

                for bidder in bidders:
                    sat = bidder in ['Space Exploration Technologies Corp.', 'Viasat, Inc.',
                                     'Hughes Network Systems, LLC']
                    processed_bid_list.append([bidder,
                                               bg,
                                               rounds[bidder],
                                               neighbors_dict,
                                               bids_with_neighbors[bidder],
                                               bidder == winner_bidder,
                                               winner_blocks if bidder == winner_bidder else [],
                                               sat,
                                               row.geometry])

            state_time = time.time() - start
            with open("../outputs/neighbors.log", "a") as log:
                log.write(f"{state_code} {state_time}\n")
            total_time += state_time
            print(state_time)

        with open("../outputs/neighbors.log", "a") as log:
            log.write(f"final time {total_time}")

        processed_bid_table = geopandas.GeoDataFrame(processed_bid_list,
                                                     columns=["bidder", "GEOID", "round", "all_neighbors",
                                                              "neighbors", "winner", "won_blocks", "satellite",
                                                              "geometry"])

        processed_bid_table["neighbor_status"] = processed_bid_table.apply(
            lambda x: neighbor_status(x.GEOID, x.neighbors, x.satellite), axis=1)

        processed_bid_table["num_blocks_won"] = processed_bid_table.won_blocks.apply(len)
        processed_bid_table["neighbor_bgs"] = processed_bid_table.neighbors.apply(len)
        processed_bid_table["all_neighbor_bgs"] = processed_bid_table.all_neighbors.apply(len)

        census = get_census()
        # dist = get_distances(bids, existing, county_shapes)[["bidder", "census_id", "dist"]]

        processed_bid_table = processed_bid_table.merge(census, how="left", left_on="GEOID", right_on="census_block_group")
        # processed_bids = processed_bids.merge(dist, how="left", left_on=["bidder", "GEOID"],
        #                                       right_on=["bidder", "census_id"])
        # processed_bids.dist = processed_bids.dist.fillna(0)
        return processed_bid_table

    return run_func(subprocess, '../outputs/data.pkl')


def generate_bidder_table(processed_bid_table):
    def subprocess():
        agg = processed_bid_table.groupby("bidder").agg(
            {"GEOID": len, "round": "mean", "num_blocks_won": sum, "neighbor_bgs": "mean", "all_neighbor_bgs": "mean",
             "winner": sum})
        agg = agg.rename(
            columns={'GEOID': 'num bids', 'round': 'average final round number', 'num_blocks_won': 'total blocks won',
                     'neighbor_bgs': 'average neighbors per bid', 'all_neighbor_bgs': 'average any neighbors per bid',
                     "winner": "num wins"}).reset_index()
        existing = processed_bid_table.loc[processed_bid_table.neighbor_status == 2].groupby("bidder").agg(
            {"GEOID": len, "round": "mean", "num_blocks_won": sum, "neighbor_bgs": "mean", "all_neighbor_bgs": "mean",
             "winner": sum})
        existing = existing.rename(columns={'GEOID': 'existing bg bids', 'round': 'existing average final round number',
                                            'num_blocks_won': 'existing blocks won',
                                            'neighbor_bgs': 'existing average neighbors per bid',
                                            'all_neighbor_bgs': 'existing average any neighbors per bid',
                                            "winner": "existing num wins"}).reset_index()
        wild_tract = processed_bid_table.loc[processed_bid_table.neighbor_status == 0].groupby("bidder").agg(
            {"GEOID": len, "round": "mean", "num_blocks_won": sum, "neighbor_bgs": "mean", "all_neighbor_bgs": "mean",
             "winner": sum})
        wild_tract = wild_tract.rename(
            columns={'GEOID': 'wild tract bg bids', 'round': 'wild tract average final round number',
                     'num_blocks_won': 'wild tract blocks won',
                     'neighbor_bgs': 'wild tract average neighbors per bid',
                     'all_neighbor_bgs': 'wild tract average any neighbors per bid',
                     "winner": "wild tract num wins"}).reset_index()
        neighbor = processed_bid_table.loc[processed_bid_table.neighbor_status == 1].groupby("bidder").agg(
            {"GEOID": len, "round": "mean", "num_blocks_won": sum, "neighbor_bgs": "mean", "all_neighbor_bgs": "mean",
             "winner": sum})
        neighbor = neighbor.rename(columns={'GEOID': 'neighbor bg bids', 'round': 'neighbor average final round number',
                                            'num_blocks_won': 'neighbor blocks won',
                                            'neighbor_bgs': 'neighbor neighbors per bid',
                                            'all_neighbor_bgs': 'neighbor any neighbors per bid',
                                            "winner": "neighbor num wins"}).reset_index()
        winner = processed_bid_table.loc[processed_bid_table.winner]
        winner_agg = winner.groupby("bidder").agg({"round": "mean", "neighbor_bgs": "mean", "all_neighbor_bgs": "mean"})
        winner_agg = winner_agg.rename(
            columns={'round': 'winner average final round number', 'neighbor_bgs': 'winner average neighbors per bid',
                     'all_neighbor_bgs': 'winner average any neighbors per bid'}).reset_index()
        winner_existing = winner.loc[winner.neighbor_status == 2].groupby("bidder").agg(
            {"round": "mean", "neighbor_bgs": "mean", "all_neighbor_bgs": "mean"})
        winner_existing = winner_existing.rename(columns={'round': 'existing winner average final round number',
                                                          'neighbor_bgs': 'existing winner average neighbors per bid',
                                                          'all_neighbor_bgs': 'existing winner average any neighbors per bid'}).reset_index()
        winner_wild_tract = winner.loc[winner.neighbor_status == 0].groupby("bidder").agg(
            {"round": "mean", "neighbor_bgs": "mean", "all_neighbor_bgs": "mean"})
        winner_wild_tract = winner_wild_tract.rename(columns={'round': 'wild tract winner average final round number',
                                                              'neighbor_bgs': 'wild tract winner average neighbors per bid',
                                                              'all_neighbor_bgs': 'wild tract winner average any neighbors per bid'}).reset_index()
        winner_neighbor = winner.loc[winner.neighbor_status == 1].groupby("bidder").agg(
            {"round": "mean", "neighbor_bgs": "mean", "all_neighbor_bgs": "mean"})
        winner_neighbor = winner_neighbor.rename(
            columns={'round': 'neighbor winner average final round number',
                     'neighbor_bgs': 'neighbor winner neighbors per bid',
                     'all_neighbor_bgs': 'neighbor winner any neighbors per bid'}).reset_index()

        final = winner_neighbor.merge(winner_wild_tract, how="outer").merge(winner_existing, how="outer").merge(
            winner_agg,
            how="outer").merge(
            neighbor, how="outer").merge(wild_tract, how="outer").merge(existing, how="outer").merge(agg, how="outer")
        final = final.fillna(0)
        final["wins/bid"] = final["num wins"] / final["num bids"]
        final["blocks/win"] = final["total blocks won"] / final["num wins"]
        final = final.fillna(0)

        final.to_excel("../outputs/bidder_neighbor_percentage.xlsx", index=False)
        return final

    return run_func(subprocess, '../outputs/bidder_neighbor_percentage.pkl')


def get_census():
    def subprocess():
        features = ["B01001e1", "B01002e1"]

        list_tables = []
        stubs = set([feature[:3].lower() for feature in features])
        files_map = {f"../data/safegraph_open_census_data_2019/data/cbg_{stub}.csv": [feature for feature in features if
                                                                                      feature[:3].lower() == stub] for
                     stub
                     in stubs}
        for file, features in files_map.items():
            keys = ["census_block_group"] + features
            table = pd.read_csv(file, usecols=keys)
            list_tables.append(table)
        df_merged = reduce(lambda left, right: pd.merge(left, right, on=['census_block_group'],
                                                        how='outer'), list_tables)
        return df_merged

    return run_func(subprocess, "../outputs/all_census_data.pkl")


if __name__ == "__main__":
    bids = get_bids()
    existing = get_existing()
    winners = get_winners()
    county_shapes = get_county_shapes()
    state_shapes = get_state_shapes(county_shapes)
    processed_bid_table = get_processed_bids(bids, existing, winners, county_shapes, state_shapes)
    generate_bidder_table(processed_bid_table)

    get_census()
