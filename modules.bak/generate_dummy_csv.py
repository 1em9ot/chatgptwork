import csv

def generate_dummy_csv(filename="sample.csv", num_rows=10):
    fieldnames = ['id', 'name', 'value']
    data = [
        {'id': i, 'name': f"Item_{i}", 'value': i * 10}
        for i in range(1, num_rows + 1)
    ]
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Dummy CSV file '{filename}' generated with {num_rows} rows.")

if __name__ == "__main__":
    generate_dummy_csv()
