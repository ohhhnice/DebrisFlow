import torch
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from torchvision.transforms.transforms import Compose
from torchvision.models.vgg import VGG
import torchvision.models as models

from src.vgg_model.load_data import DebrisFlow


def transformer() -> Compose:
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
    )
    return transform


def load_train_and_val_data(
    train_data_folder: str, val_data_folder: str, batch_size: int, transform: Compose
) -> tuple[DataLoader, DataLoader]:
    train_dataset = DebrisFlow(root_dir=train_data_folder, transform=transform)
    train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_dataset = DebrisFlow(root_dir=val_data_folder, transform=transform)
    val_dataloader = DataLoader(val_dataset, batch_size=batch_size, shuffle=True)
    return train_dataloader, val_dataloader, len(train_dataset), len(val_dataset)


def load_vgg_model(
    model_weights_path: str, feature_size: int, class_size: int, device: str
) -> VGG:
    """用于训练"""
    vgg19 = models.vgg19(pretrained=False).to(device)
    # vgg19.load_state_dict(torch.load(model_weights_path))
    vgg19.classifier[6] = torch.nn.Linear(4096, feature_size).to(device)
    vgg19.classifier.append(torch.nn.ReLU(True).to(device))
    vgg19.classifier.append(torch.nn.Dropout(p=0.5).to(device))
    vgg19.classifier.append(torch.nn.Linear(feature_size, class_size).to(device))

    total = sum(p.numel() for p in vgg19.parameters())
    print("Number of parameters: %.2fM" % (total / 1e6))
    return vgg19


def load_extract_feature_vgg_model(
    model_weights_path: str,
    feature_size: int,
    class_size: int,
    device: str,
) -> VGG:
    """用于提取特征"""
    vgg19 = models.vgg19(pretrained=False).to(device)
    vgg19.classifier[3] = torch.nn.Linear(4096, feature_size).to(device)
    vgg19.classifier[6] = torch.nn.Linear(feature_size, class_size).to(device)
    vgg19.load_state_dict(torch.load(model_weights_path))
    vgg19.classifier = torch.nn.Sequential(*list(vgg19.classifier.children())[:-3])
    return vgg19
