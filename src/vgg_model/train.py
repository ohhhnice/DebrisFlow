import torch
import os
from torch.utils.tensorboard import SummaryWriter
from src.vgg_model.vgg import *

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def train_based_on_vgg19(
    train_data_folder: str,
    val_data_folder: str,
    batch_size: int,
    model_weights_path: str,
    feature_size: int,
    class_size: int,
    device: str,
    lr: float,
    log_dir: str,
    epochs: int,
    save_pth_dir: str,
):
    transform = transformer()
    train_dataloader, val_dataloader, _, len_val_dataset = load_train_and_val_data(
        train_data_folder, val_data_folder, batch_size, transform
    )
    vgg19 = load_vgg_model(model_weights_path, feature_size, class_size, device)

    optimizer = torch.optim.Adam(vgg19.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss().to(device)

    total_train_step = 0
    total_test_step = 0
    writer = SummaryWriter(log_dir)

    os.makedirs(save_pth_dir, exist_ok=True)

    for epoch in range(epochs):
        vgg19.train()
        for i, (img, label) in enumerate(train_dataloader):
            img, label = img.to(device), label.to(device)
            output = vgg19(img)
            loss = criterion(output, label)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_train_step += 1
            writer.add_scalar("Loss/train", loss.item(), total_train_step)

        vgg19.eval()
        total_test_loss = 0
        total_accuracy = 0
        with torch.no_grad():
            for img, label in val_dataloader:
                img, label = img.to(device), label.to(device)
                output = vgg19(img)
                loss = criterion(output, label)
                total_test_loss += loss.item()
                accuracy = (output.argmax(1) == label).sum().item()
                total_accuracy += accuracy

        print("===============Epoch: {}===============".format(epoch + 1))
        print("整体测试集上的Loss: {}".format(total_test_loss))
        print("整体测试集上的准确率: {}".format(total_accuracy / len_val_dataset))
        writer.add_scalar("Loss/test", total_test_loss, total_test_step)
        writer.add_scalar(
            "Accuracy/test", total_accuracy / len_val_dataset, total_test_step
        )
        total_test_step += 1
        torch.save(
            vgg19.state_dict(),
            os.path.join(
                save_pth_dir,
                f"vgg19_epoch{epoch+1}_accuracy{total_accuracy / len_val_dataset}_loss{total_test_loss}.pth",
            ),
        )
