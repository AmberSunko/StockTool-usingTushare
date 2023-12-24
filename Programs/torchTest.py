import torch,os,numpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from torch import nn
from torch import optim
import  torch.nn.functional as F
from torch.utils.data import Dataset,DataLoader
#数据集
from torchvision.datasets import MNIST
from torchvision.transforms import Compose,Normalize,ToTensor


BATCH_SIZE=128
device =  torch.device("cuda" if torch.cuda.is_available() else "cpu")
data_path = "../Data/torchData/SMSSpamCollection"

class MyDataset(Dataset):
    def __init__(self):
        lines=open(data_path,encoding='utf-8').readlines()
        lines = [[i[:4].strip(),i[4:].strip()] for i in lines]
        self.df = pd.DataFrame(lines,columns=["label","sms"])
    def __getitem__(self, index):
        sigle_item = self.df.iloc[index,:]
        return sigle_item.values[0],sigle_item.values[1]
    def __len__(self):
        return self.df.shape[0]

class Lr(nn.Module):
    def __init__(self):
        super(Lr,self).__init__()
        self.linear = nn.Linear(1,1)

    def forward(self,x):
        out = self.linear(x)
        return out

my_dataset = MyDataset()

def get_datalodaer(train=True,batch_size=BATCH_SIZE):
    transform_fn = Compose([
        ToTensor(),
        Normalize(mean=(0.1307,),std=(0.3081,))
    ])
    mnist = MNIST(root="../Data/torchData",train=train,download=False,transform=transform_fn)
    data_loader = DataLoader(dataset=mnist,batch_size=batch_size,shuffle=True,drop_last=True)
    return data_loader


class MnistNet(nn.Module):
    def __init__(self):
        super(MnistNet,self).__init__()
        self.fc1 = nn.Linear(28*28*1,28)
        self.fc2 = nn.Linear(28,10)

    def forward(self,x):
        x = x.view(-1,28*28*1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.fc2(x)
        return F.log_softmax(x,dim=-1)

mnist_net = MnistNet()
optimizer = optim.Adam(mnist_net.parameters(),lr=0.001)
if os.path.exists("../Data/torchModel/mnist_net.pt"):
    mnist_net.load_state_dict(torch.load("../Data/torchModel/mnist_net.pt"))
    optimizer.load_state_dict(torch.load("../Data/torchResult/mnist_optimizer.pt"))
def train(epoch):
    mode = True
    mnist_net.train(mode=mode)

    train_dataloader = get_datalodaer(train=mode,batch_size=128)

    for index,(data,target) in enumerate(train_dataloader):
        optimizer.zero_grad()
        output = mnist_net(data)
        loss = F.nll_loss(output,target)
        loss.backward()
        optimizer.step()
        if index%10 == 0:
            print(epoch,index,loss.item())
    torch.save(mnist_net.state_dict(),"../Data/torchModel/mnist_net.pt")
    torch.save(optimizer.state_dict(),"../Data/torchResult/mnist_optimizer.pt")

def test():
    loss_list = []
    acc_list = []
    test_loss= 0
    correct = 0
    mnist_net.eval()
    test_dataloader = get_datalodaer(train=False,batch_size=2)
    for index,(input,target) in enumerate(test_dataloader):
        with torch.no_grad():
            output = mnist_net(input)
            test_loss =F.nll_loss(output,target)
            loss_list.append(test_loss)
            pred=output.max(dim=-1)[-1]
            cur_acc = pred.eq(target).float().mean()
            acc_list.append(cur_acc)
            break
    print(numpy.mean(loss_list),numpy.mean(acc_list))

test()

# model.eval()
# predict =model(x)
#
# plt.figure(figsize=(20,8))
# plt.scatter(x.cpu().numpy().reshape(-1),y.cpu().numpy().reshape(-1))
# plt.plot(x.cpu().numpy().reshape(-1),predict.cpu().detach().numpy().reshape(-1),c="r")
# plt.show()