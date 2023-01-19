import geopandas
from shapely.ops import cascaded_union
from utils import run_func
from process import get_bids, get_existing, get_county_shapes


def find_dist(bids, existing, county_shapes):
    existing = existing.merge(county_shapes, how='left', right_on='GEOID', left_on='bg')
    existing = existing[~existing.geometry.isnull()]
    footprints = existing.groupby("names")["geometry"].apply(list).reset_index(name="geometry")
    footprint_dict = {}
    for index, row in footprints.iterrows():
        names = row.names
        locations = row.geometry
        new_dict = footprint_dict.copy()
        stop = False
        for n, l in footprint_dict.items():
            for name in names:
                if name in n:
                    new_dict.pop(n)
                    n = n.union(names)
                    l = l + locations
                    new_dict[n] = l

                    stop = True
                    break
            if stop:
                break
        if not stop:
            new_dict[names] = locations
        footprint_dict = new_dict

    footprints = {k: cascaded_union(v) for k, v in footprint_dict.items()}

    bids = bids.merge(county_shapes, how='left', right_on='GEOID', left_on='census_id')

    footprint_column = []
    for index, row in bids.iterrows():
        name = row.bidder
        for nameset, footprint in footprints.items():
            if name in nameset:
                footprint_column.append(footprint)
                break
        else:
            footprint_column.append(None)

    bids["footprint"] = footprint_column
    bids["dist"] = geopandas.GeoSeries(bids.geometry).distance(geopandas.GeoSeries(bids.footprint))
    return bids


def get_distances(bids, existing, county_shapes):
    return run_func(get_distances, '../outputs/distance_data.pkl', bids, existing, county_shapes)


if __name__ == "__main__":
    bids = get_bids(),
    existing = get_existing()
    county_shapes = get_county_shapes()
    get_distances(bids, existing, county_shapes)
