import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import torchvision
from torchvision import datasets, models, transforms
from PIL import Image


img_width, img_height = 224, 224


train_folder = "C:/Users/aruns/OneDrive/Documents/MGR workshop/sign"


batch_size = 3
num_epochs = 9


data_transforms = transforms.Compose([
    transforms.Resize((img_width, img_height)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

train_dataset = datasets.ImageFolder(train_folder, transform=data_transforms)
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)


model = models.vgg16(pretrained=True)


for param in model.features.parameters():
    param.requires_grad = False


num_ftrs = model.classifier[6].in_features
model.classifier[6] = nn.Linear(num_ftrs, len(train_dataset.classes))


criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)


exp_lr_scheduler = lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

for epoch in range(num_epochs):
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)

       
        outputs = model(inputs)
        loss = criterion(outputs, labels)

        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    
    exp_lr_scheduler.step()


def classify_image(img_path):
    
    img = Image.open(img_path).convert('RGB')
    img = data_transforms(img).unsqueeze(0)

    
    with torch.no_grad():
        img = img.to(device)
        outputs = model(img)
        probs = nn.functional.softmax(outputs, dim=1)[0]
        _, preds = torch.max(outputs, 1)

    
    class_name = train_dataset.classes[preds.item()]
    probability = probs[preds.item()].item()

    
    print(f'Prediction: {class_name} with probability: {probability*100:.2f}%')


img_path = r"C:\Users\aruns\OneDrive\Documents\MGR workshop\test images\signature (2).png"
classify_image(img_path)