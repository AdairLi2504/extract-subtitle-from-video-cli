import difflib

from PIL import Image
import cv2
import easyocr
import argparse

parser = argparse.ArgumentParser(description="Get subtitle displayed on the video")
file = parser.add_argument("-f","--file",type=str,required=True,help="Path of the video file")
parser.add_argument("-p","--position",type=str,required=True,help="Position of the left top corner of the subtitle.It should be the pixel distance to the left side of the video, 'x', another pixel distance to the top of the video.e.g. 10x320 ")
parser.add_argument("-s","--size",type=str,required=True,help="Size of the subtitle.It should be the width, 'x', and the height. e.g 620x40")
parser.add_argument("-t","--thresh",type=int,default=0,help="Use cv2.threshold to enhance the subtitle image. Any pixel which is higher than this value will become white, and others will become black.\nIf the value is default 0, cv2.threshold will not be used. Please keep it 0 when the background of subtitle is a single colour.")
parser.add_argument("-sc","--score",type=float,default=0.4,help="The lowest score a part of subtitle should get.")
parser.add_argument("-ml","--minLength",type=int,default=2,help="Only text with a length greater than this value is considered part of the subtitles.")
parser.add_argument('-st', "--similarityThreshold", type=float,default=0.7, help="Consider a new line if the similarity between the newly detected text and the previous detected text is below this value.")
args = parser.parse_args()

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
    capture = cv2.VideoCapture(args.file)
    pos_list = args.position.split('x')

    #check if the arugments are in the range and set default
    if not 0 <= args.thresh <= 255 : raise argparse.ArgumentTypeError("The thresh value should be between 0 and 255")
    else : thresh = args.thresh

    if not 0 <= args.score <= 1: raise argparse.ArgumentTypeError("The score value should be between 0 and 1")
    else: score = args.score

    if not 0 <= args.minLength: raise argparse.ArgumentTypeError("Please enter a sensible number about minLength")
    else: minLength = args.minLength

    if not 0 <= args.similarityThreshold <= 1: raise argparse.ArgumentTypeError("The similarity value should be between 0 and 1")
    else: st = args.similarityThreshold

    #parse the area of the subtitle
    if len(pos_list) != 2:
        raise argparse.ArgumentTypeError("The format of the position cannot be parsed")
    pos_list = [int(pos_list[0]),int(pos_list[1])]

    size_list = args.size.split('x')
    if len(size_list) != 2:
        raise argparse.ArgumentTypeError("The format of the position cannot be parsed")
    size_list = [int(size_list[0]),int(size_list[1])]

    subs_corner = [[pos_list[0]-1,pos_list[1]-1],[pos_list[0]+size_list[0]-1,pos_list[1]+size_list[1]-1]]

    if not capture.isOpened():
        raise argparse.ArgumentError(file,"Cannot open the video file")
    elif not (( 0 <= subs_corner[0][0] < int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) ) and (0 <= subs_corner[0][1] < int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) ) and \
        ( 0 <= subs_corner[1][0] < int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)) ) and (0 <= subs_corner[1][1] < int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)) )):
        raise argparse.ArgumentTypeError("The subtitile area entered is out of the video")
    else:
        fps = capture.get(cv2.CAP_PROP_FPS)
        i = 0
        textOCR = ""
        textNow = ""
        ocr = easyocr.Reader(['en','ch_sim'])
        print(thresh)
        while True:
            i += 1
            ret, img = capture.read()
            if not ret:break
            img = img[subs_corner[0][1]:subs_corner[1][1],subs_corner[0][0]:subs_corner[1][0]]
            if thresh != 0:ret, img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)
            out = ocr.readtext(img)
            if len(out) > 0:
                for j in out:
                    if (j[-1] > score) and (len(j[-2]) > minLength):
                        textOCR = ""
                        break
                for j in out:
                    if (j[-1] > score) and (len(j[-2]) > minLength):
                        textOCR += j[-2] + " "
                if difflib.SequenceMatcher(None,textOCR,textNow).ratio() < st:
                    textNow = textOCR
                    print(lrc_time_format(i/fps),textOCR)

                    

            
