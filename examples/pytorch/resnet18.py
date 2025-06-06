import numpy as np
import os      
import argparse
import sys
from ksnn.api import KSNN
from ksnn.types import *
import cv2 as cv
import time

mean = [103.94, 116.78, 123.68]
var = [0.01700102]

def show_top5(output):
    output_sorted = sorted(output, reverse=True)
    top5_str = '----Resnet18----\n-----TOP 5-----\n'
    for i in range(5):
        value = output_sorted[i]
        index = np.where(output == value)
        for j in range(len(index)):
            if (i + j) >= 5:
                break
            if value > 0:
                topi = '{}: {}\n'.format(index[j], value)
            else:
                topi = '-1: 0.0\n'
            top5_str += topi
    print(top5_str)

def softmax(x):
    return np.exp(x)/sum(np.exp(x))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--library", help="Path to C static library file")
    parser.add_argument("--model", help="Path to nbg file")
    parser.add_argument("--picture", help="Path to input picture")
    parser.add_argument("--level", help="Information printer level: 0/1/2")
    args = parser.parse_args()
    if args.model :
        if os.path.exists(args.model) == False:
            sys.exit('Model \'{}\' not exist'.format(args.model))
        model = args.model
    else :
        sys.exit("NBG file not found !!! Please use format: --model")
    if args.picture :
        if os.path.exists(args.picture) == False:
            sys.exit('Input picture \'{}\' not exist'.format(args.picture))
        picture = args.picture
    else :
        sys.exit("Input picture not found !!! Please use format: --picture")
    if args.library :
        if os.path.exists(args.library) == False:
            sys.exit('C static library \'{}\' not exist'.format(args.library))
        library = args.library
    else :
        sys.exit("C static library not found !!! Please use format: --library")
    if args.level == '1' or args.level == '2' :
        level = int(args.level)
    else :
        level = 0

    resnet18 = KSNN('VIM3')
    print(' |---+ KSNN Version: {} +---| '.format(resnet18.get_nn_version()))

    print('Start init neural network ...')

    resnet18.nn_init(library=library, model=model, level=level)

    print('Done.')

    print('Get input data ...')
    cv_img = list()
    orig_img = cv.imread(picture, cv.IMREAD_COLOR)
    img = cv.resize(orig_img, (224, 224)).astype(np.float32)
    img[:, :, 0] = img[:, :, 0] - mean[0]
    img[:, :, 1] = img[:, :, 1] - mean[1]
    img[:, :, 2] = img[:, :, 2] - mean[2]
    img = img * var[0]
    
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    
    img = img.transpose(2, 0, 1)
    cv_img.append(img)
    print('Done.')

    print('Start inference ...')
    start = time.time()

    '''
        default input_tensor is 1
        default output_tensor is 1
    '''
    outputs = resnet18.nn_inference(cv_img, input_tensor=1, output_tensor=1, platform = 'PYTORCH', reorder='2 1 0', output_format=output_format.OUT_FORMAT_FLOAT32)
    end = time.time()
    print('Done. inference : {} s'.format(end - start))

    show_top5(softmax(np.array(outputs[0], dtype=np.float32)))

