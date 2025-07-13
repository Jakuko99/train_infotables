if __name__ == "__main__":
    with open("assets/stations.txt", "r", encoding="utf-8") as f:
        enum_values = []
        for line in f:
            line = line.strip().upper().split(">")
            line[1] = line[1].replace(" ", "_").replace("-", "_")
            enum_values.append(f"{line[1]} = {line[0]}")

    with open("station_ids.py", "w", encoding="utf-8") as f:
        f.write("from enum import Enum\n\n\n")
        f.write("class StationIds(Enum):\n")
        f.write("\n\t".join(enum_values))
