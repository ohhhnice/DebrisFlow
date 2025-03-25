import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import os


def plot_line_chart_from_csv(csv_file_path, field_name, save_folder=None):

    # 设置中文字体路径，确保字体文件在指定路径
    rcParams["font.sans-serif"] = ["Microsoft YaHei"]  # 如果没有，可能需要安装字体
    rcParams["axes.unicode_minus"] = False
    df = pd.read_csv(csv_file_path)
    plt.figure(figsize=(10, 6))
    plt.plot(df[field_name], marker="o", linestyle="-", color="b", label=field_name)
    plt.title(f"折线图 - {field_name}")
    plt.xlabel("Index")
    plt.ylabel(field_name)
    plt.legend()

    plt.grid(True)
    plt.tight_layout()

    if save_folder:
        os.makedirs(save_folder, exist_ok=True)
        csv_base_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        save_path = os.path.join(
            save_folder, f"{field_name}_line_chart_from_{csv_base_name}.png"
        )
        plt.savefig(save_path)
    else:
        plt.show()
