if __name__ == '__main__':
    # 打开文件并读取内容
    file_name = './data/results_of_China%20modernization.csv'
    # file_name = './data/results_of_Chinese%20style%20modernization.csv'
    # file_name = './data/results_of_Chinese%20path%20to%20modernization.csv'
    with open(file_name, "r", encoding="utf-8") as file:  # r: read
        content = file.read()
    # 将内容按行分割成列表
    lines = content.split("\n")
    print("原始数据共", len(lines), "行")

    # 使用set去除重复元素
    unique_lines = set(lines)
    print("去重后数据共", len(unique_lines), "行")
    # 将去重后的内容写入新文件
    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n".join(unique_lines))
