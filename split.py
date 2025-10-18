import csv

# Hardcoded config
INPUT_FILE = "jan.csv"
NUM_PARTS = 100
PREFIX = "split_"

def main():
    with open(INPUT_FILE, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        header, rows = reader[0], reader[1:]
        total_rows = len(rows)
        chunk_size = (total_rows + NUM_PARTS - 1) // NUM_PARTS  # ceiling division

        for i in range(NUM_PARTS):
            start = i * chunk_size
            end = start + chunk_size
            chunk = rows[start:end]
            if not chunk:
                break

            filename = f"{PREFIX}{i+1:03}.csv"
            with open(filename, "w", newline='', encoding='utf-8') as out_f:
                writer = csv.writer(out_f)
                writer.writerow(header)
                writer.writerows(chunk)

            print(f"✅ {filename}: {len(chunk)} rows")

    print(f"\n🎉 Done. Split into {i+1} file(s).")

if __name__ == "__main__":
    main()

