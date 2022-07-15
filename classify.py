from glob import iglob
from os import getcwd, mkdir,listdir, rmdir
from os.path import exists,join,basename,isdir
import cv2
import numpy as np
from shutil import move
from colorama import Fore, init, Style
from statistics import mode


Working_dir = getcwd()
bright = Style.BRIGHT
green, blue, red, cyan, reset = Fore.GREEN + bright, Fore.BLUE + bright, Fore.RED + bright, Fore.CYAN, Fore.RESET
init(convert=True, autoreset=True)
config_file='yolov3.cfg'
weights_file = 'yolov3.weights'
class_file='yolov3.txt'
total_data = 'data'
net = cv2.dnn.readNet(weights_file, config_file)
classes_list = ['person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 
 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
  'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 
  'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 
  'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 
  'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 
  'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 
  'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 
  'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush','other']

def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers

def process(image_file):
    global classes       
    image = cv2.imread(image_file)
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392
    classes = None
    classes = classes_list
    blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(get_output_layers(net))
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    if len(indices)==0:
        folder ='other'
    else:
        detect_list = [class_ids[i] for i in indices]
        if 0 in detect_list:
            folder='person'
        else:
            folder = str(classes[mode(detect_list)])
    print(f"{green}[+] Processing file - {basename(image_file)} to {folder}")
    move(image_file,join(Working_dir,total_data,folder,basename(image_file)))


[mkdir(total_data)if not exists(total_data) else None]
[mkdir(join(Working_dir,total_data,folder)) for folder in classes_list if not exists(join(Working_dir,total_data,folder))]


path = input("[+] Enter path or drag and drop the folder : ").replace('"','')

if path=='':
    path = input("[+] Enter path or drag and drop the folder : ").replace('"','')

for filename in iglob(f'{path}/**/*',recursive=True):
    try:
        process(filename)
    except Exception as e:
        print(f"{red}[-] Error - {e}")
        continue

print(f"{green}[+] Deleteing empty folders")
path = join(Working_dir,total_data)
for folder in iglob(f'{path}/*/',recursive=True):
    if isdir(folder):
        if not listdir(folder):
            print(f"{red}[-] Deleteing empty folders - {folder}")
            rmdir(folder)