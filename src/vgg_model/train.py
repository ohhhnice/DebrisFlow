import sys
import torch
import os
from pathlib import Path
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from load_data import DebrisFlow
from argparse import ArgumentParser
import torchvision.models as models
from torch.utils.tensorboard import SummaryWriter

ROOT = Path(__file__).resolve().parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def train(args):
    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
    )

    train_dataset = DebrisFlow(root_dir=args.train_data, transform=transform)
    train_dataloader = DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True)
    val_dataset = DebrisFlow(root_dir=args.val_data, transform=transform)
    val_dataloader = DataLoader(
        val_dataset, batch_size=args.batch_size, shuffle=True)

    vgg19 = models.vgg19(pretrained=False).to(device)
    vgg19.load_state_dict(torch.load(args.model_path))
    vgg19.classifier[6] = torch.nn.Linear(4096, 2).to(device)
    total = sum(p.numel() for p in vgg19.parameters())
    print("Number of parameters: %.2fM" % (total / 1e6))

    optimizer = torch.optim.Adam(vgg19.parameters(), lr=args.lr)
    criterion = torch.nn.CrossEntropyLoss().to(device)

    total_train_step = 0
    total_test_step = 0
    writer = SummaryWriter(args.log_dir)

    for epoch in range(args.epochs):
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

        print("===============Epoch: {}===============".format(epoch+1))
        print("整体测试集上的Loss: {}".format(total_test_loss))
        print("整体测试集上的准确率: {}".format(total_accuracy / len(val_dataset)))
        writer.add_scalar("Loss/test", total_test_loss, total_test_step)
        writer.add_scalar("Accuracy/test", total_accuracy /
                          len(val_dataset), total_test_step)
        total_test_step += 1
        torch.save(vgg19.state_dict(),
                   os.path.join(
                       args.save_pth_dir,
                       f"vgg19_epoch{epoch+1}_accuracy{total_accuracy / len(val_dataset)}_loss{total_test_loss}.pth"
        ))


if __name__ == "__main__":
    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[1]
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))

    parser = ArgumentParser()
    parser.add_argument("--train_data", type=str,
                        default="./data/vgg", help="train dataset root")
    parser.add_argument("--val_data", type=str,
                        default="./data/vgg", help="val dataset root")
    parser.add_argument("--batch_size", type=int, default=3, help="batch size")
    parser.add_argument("--epochs", type=int, default=50,
                        help="number of epochs")
    parser.add_argument("--lr", type=float, default=0.001,
                        help="learning rate")
    parser.add_argument("--model_path", type=str,
                        default="models/pretrained/vgg/vgg19_weights.pth", help="model weights path")
    parser.add_argument("--log_dir", type=str, default="logs", help="log dir")
    parser.add_argument("--save_pth_dir", type=str,
                        default="models/trained/vgg", help="save train pth dir")
    args = parser.parse_args()
    train(args)
