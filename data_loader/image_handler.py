import os
from cv2 import cv2
from config_parser.config import CONFIG

ANGLES = [
    0, -45, 45, -90, 90
]

def detect(filename, out_dir=CONFIG.data.faces_dir, cascade_file=CONFIG.data.cascade_file):
    if not os.path.isfile(cascade_file):
        raise RuntimeError("%s: not found" % cascade_file)

    cascade = cv2.CascadeClassifier(cascade_file)
    image = cv2.imread(filename, cv2.IMREAD_COLOR)
    if image is None:
        print(f'[ERROR] Can not read image {filename}')
        return
    cnt = 0
    for angle in ANGLES:
        print(f'Detecting {filename} angle: {angle}...', end='\r')
        rotated_image = rotate(image, angle)
        gray = cv2.cvtColor(rotated_image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = cascade.detectMultiScale(gray,
                                        # detector options
                                        scaleFactor = 1.1,
                                        minNeighbors = 5,
                                        minSize = (24, 24))
        for i, (x, y, w, h) in enumerate(faces):
            cnt += 1
            face = rotated_image[y: y + h, x:x + w, :]
            face = cv2.resize(face, (256, 256))
            save_filename = '{}-{:02d}.jpg'.format(os.path.splitext(filename)[0], cnt)
            # cv2.imshow("AnimeFaceDetect", face)
            # cv2.waitKey(0)
            cv2.imwrite(os.path.join(out_dir, os.path.split(save_filename)[-1]), face)
        if faces != ():
            break

    # cv2.imshow("AnimeFaceDetect", image)
    # cv2.waitKey(0)
    # cv2.imwrite("out.png", image)

def rotate(img_arr, angle):
    if angle == 0:
        return img_arr
    h, w = img_arr.shape[: 2]
    center = (w//2, h//2)
    return cv2.warpAffine(img_arr, cv2.getRotationMatrix2D(center, angle, 1), (w, h))

for file_name in os.listdir(CONFIG.data.origin_images_dir):
    file_path = os.path.join(CONFIG.data.origin_images_dir, file_name)
    detect(file_path)
    file_path_used = os.path.join(CONFIG.data.origin_images_used_dir, file_name)
    # os.rename(file_path, file_path_used)
    with open(file_path, 'rb') as fr:
        with open(file_path_used, 'wb') as fw:
            fw.write(fr.read())
    os.remove(file_path)
