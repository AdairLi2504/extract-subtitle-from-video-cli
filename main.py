import difflib

import argparse
import cv2
from cnocr import CnOcr

# config of command
parser = argparse.ArgumentParser(description="Get the caption of the video")
parser.add_argument('-f', "--File", type=str, required=True, help='Path of the Video File')
parser.add_argument('-r', "--SequenceMatcherRation", type=float, help='decide if it is a new line')
parser.add_argument('-c', "--Cut", type=float, help="cut the 1/c bottom of the video as the area to OCR")
parser.add_argument('-s', "--Score", type=float, help="the minimum score it should get")
parser.add_argument('-t', "--Thresh", type=int, help="the thresh to threshold")
parser.add_argument('-ml' "--MinLength", type=int, help="the minimum length of a new line")
args = parser.parse_args()


# the function covert time to lrc format

def lrc_time_format(time):
    second = time % 60
    second = round(second, 2)
    secondstr = str(second)
    secondstr = secondstr.split('.')[0].rjust(2, '0') + '.' + secondstr.split('.')[1].ljust(2, '0')
    minute = int(time / 60)
    minutestr = str(minute)
    minutestr = minutestr.rjust(2, '0')
    return '[' + minutestr + ':' + secondstr + ']'


if __name__ == "__main__":
    if args.SequenceMatcherRation is None:
        smr = 0.7
    else:
        smr = args.SequenceMatcherRation
    if args.Cut is None:
        cut = 2
    else:
        cut = args.Cut
    if args.Thresh is None:
        thresh = 200
    else:
        thresh = args.Thresh
    if args.Score is None:
        score = 0.5
    else:
        score = args.Score
    if args.ml__MinLength is None:
        minLength = 2
    else:
        minLength = args.ml__MinLength
    capture = cv2.VideoCapture(args.File)
    ocr = CnOcr()
    textOCR = ""
    textNow = ""
    i = 0
    fps = capture.get(cv2.CAP_PROP_FPS)
    print(fps)
    if capture.isOpened():
        while True:
            i = i + 1
            ret, img = capture.read()
            if not ret:break
            height = len(img)
            width = len(img[0])
            img = img[int(height * (1 - 1 / cut)):height, 0:width]
            ret, binary = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY_INV)
            out = ocr.ocr(binary)
            if len(out) > 0:
                for j in out:
                    if (j["score"] > score) and (len(j["text"]) >= minLength):
                        textOCR = ""
                        break
                for j in out:
                    if (j["score"] > score) and (len(j["text"]) >= minLength):
                        textOCR = textOCR + j["text"] + " "
            if difflib.SequenceMatcher(None, textOCR, textNow).ratio() < smr:
                textNow = textOCR
                print(lrc_time_format(i/fps),textOCR)
    else:
        print("failed to open video")
