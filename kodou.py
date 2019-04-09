# import it
import kodou


# create a Part object
part = kodou.Part(events={
    # specify some microtonal notes and some beats
    "notes": [n + 1/6 for n in range(60, 85)] + [85],
    "beats":
    [n * 1/7 for n in range(7)] + \
    [1 + (n * 1/6) for n in range(6)] + \
    [2 + (n * 1/5) for n in range(5)] + \
    [3 + (n * 1/4) for n in range(4)] + \
    [4 + (n * 1/3) for n in range(3)] + [5]},
            # add some metadata to them
            metadata={
                "articulation": {(0, 1): ("^", ".", "-"),
                                 (1, 2): (">", "trill"),
                                 (2, 3): ("marcato", "prallprall", "+"),
                                 (3, 4): "reverseturn",
                                 (4, 5): ("shortfermata", "prallmordent", "<>"),
                                 5: "marcato"},
                "dynamic": {0: "sf", 1: "sf", 2: "sf", 3: "sf", 4: "sf", 5: "fff",
                            (0, 1): ">", (1, 2): "dim", (2, 3): "<", (3, 4): ">", (4, 5): "cresc"},
                "legato": {"solid": [(0, 1), (4, 5)],
                           "dotted": [(1, 2), (3, 4)],
                           "halfdashed": [(2, 3)]},
                "barline": {4: "!", 5: "|."}
            })


# and process everything
kodou.kodou(part)