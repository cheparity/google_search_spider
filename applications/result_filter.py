if __name__ == '__main__':
    # todo Please replace the file name you want to filter
    file_name = './data/results_of_YOUR%20QUESTION.csv'
    with open(file_name, "r", encoding="utf-8") as file:  # r: read
        content = file.read()
    lines = content.split("\n")
    print("Raw data total ", len(lines), " rows.")

    # Remove duplicates using set
    unique_lines = set(lines)
    print("De-duplicated data total ", len(unique_lines), " rows.")
    # Rewrite the file
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n".join(unique_lines))
