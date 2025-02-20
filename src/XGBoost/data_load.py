from torch.utils.data import Dataset
from PIL import Image
import os


class DebrisFlow(Dataset):
    def __init__(self, root_dir="./data", transform=None):
        self.root_dir = root_dir
        self.data = []
        self.transform = transform

        for label in os.listdir(root_dir):
            if not label.startswith("."):
                for file in os.listdir(os.path.join(root_dir, label)):
                    if not file.startswith("."):
                        self.data.append(
                            (os.path.join(root_dir, label, file), int(label)))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path, label = self.data[idx]
        img = Image.open(img_path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


if __name__ == "__main__":
    dataset = DebrisFlow()
    img, label = dataset.__getitem__(0)
