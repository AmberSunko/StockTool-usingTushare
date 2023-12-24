from torch.utils.data import  DataLoader,Dataset
import os,re

def collate_fn(batch):
    # content,label=list(zip(*batch))
    # return content,label
    return tuple(zip(*batch))

def tokenlize(content):
     content = re.sub("<.*?>","",content)
     fileters = ['\.',':','\t','\n','\x97','\x96','#','$','%','&']
     content = re.sub("|".join(fileters),' ',content)
     content = re.sub("'s",' is',content)
     content = re.sub("'m",' am',content)
     content = re.sub("'ve",' have',content)
     content =re.sub("\d+",lambda x:x.group(0)+" ",content)
     tokens = [i.strip().lower() for i in content.split()]
     return tokens

class ImdbDataset(Dataset):
    def __init__(self,train=True):
        self.train_data_path = "../Data/torchData/aclImdb/train"
        self.test_data_path = "../Data/torchData/aclImdb/test"
        data_path = self.train_data_path if train else self.test_data_path

        #文件名放入列表
        temp_data_path = [os.path.join(data_path,"pos"),os.path.join(data_path,"neg")]
        self.total_file_path = []
        for path in temp_data_path:
            file_name_list = os.listdir(path)
            file_path_list = [os.path.join(path,i) for i in file_name_list if i.endswith(".txt")]
            self.total_file_path.extend(file_path_list)

    def __getitem__(self, index):
        file_path = self.total_file_path[index]
        label = 0 if file_path.split("\\")[-2]=="neg" else 1
        content = open(file_path,encoding="utf-8").read()
        tokens = tokenlize(content)
        return tokens,label

    def __len__(self):
        return  len(self.total_file_path)

def get_dataloader(train=True):
    imdb_dataset = ImdbDataset(train)
    data_loader = DataLoader(imdb_dataset,batch_size=2,shuffle=True,collate_fn=collate_fn)
    return data_loader

for index,(input,target) in enumerate(get_dataloader()):
    print(index)
    print(input)
    print(target)
    break
