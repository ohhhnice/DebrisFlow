import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 12))

# 定义层的位置和大小
layers = [
    {
        "name": "Input",
        "type": "input",
        "x": 0.1,
        "y": 0.9,
        "width": 0.2,
        "height": 0.05,
    },
    {
        "name": "Conv3-64",
        "type": "conv",
        "x": 0.4,
        "y": 0.8,
        "width": 0.2,
        "height": 0.05,
    },
    {
        "name": "MaxPool",
        "type": "pool",
        "x": 0.4,
        "y": 0.7,
        "width": 0.2,
        "height": 0.05,
    },
    # 添加更多层...
]

# 绘制层
for layer in layers:
    if layer["type"] == "input":
        ax.add_patch(
            patches.Rectangle(
                (layer["x"], layer["y"]),
                layer["width"],
                layer["height"],
                edgecolor="black",
                facecolor="lightblue",
            )
        )
    elif layer["type"] == "conv":
        ax.add_patch(
            patches.Rectangle(
                (layer["x"], layer["y"]),
                layer["width"],
                layer["height"],
                edgecolor="black",
                facecolor="lightgreen",
            )
        )
    elif layer["type"] == "pool":
        ax.add_patch(
            patches.Rectangle(
                (layer["x"], layer["y"]),
                layer["width"],
                layer["height"],
                edgecolor="black",
                facecolor="lightcoral",
            )
        )
    ax.text(
        layer["x"] + 0.05, layer["y"] + 0.025, layer["name"], fontsize=10, color="black"
    )

# 连接层
for i in range(len(layers) - 1):
    ax.annotate(
        "",
        xy=(
            layers[i]["x"] + layers[i]["width"],
            layers[i]["y"] + layers[i]["height"] / 2,
        ),
        xytext=(layers[i + 1]["x"], layers[i + 1]["y"] + layers[i + 1]["height"] / 2),
        arrowprops=dict(arrowstyle="->", lw=1.5),
    )

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")
plt.show()
