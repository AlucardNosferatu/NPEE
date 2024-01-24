import cv2
import numpy as np
import pytesseract
from PIL import Image


def cv_read_img(params):
    cv_params = params['cv']
    img_path = cv_params['img_path']
    flags_dict = {
        'color': cv2.IMREAD_COLOR,
        'gscale': cv2.IMREAD_GRAYSCALE
    }
    if 'flags' not in cv_params.keys():
        img_array = cv2.imread(filename=img_path)
    else:
        flags = flags_dict[cv_params['flags']]
        img_array = cv2.imread(filename=img_path, flags=flags)
    cv_params['img_array'] = img_array
    return params


def cv_cut_img(params):
    cv_params = params['cv']
    img_array: np.array = cv_params['img_array']
    shape = {'x': img_array.shape[1], 'y': img_array.shape[0]}
    point_ul = cv_params['point_ul']
    point_dr = cv_params['point_dr']
    if 0 <= point_ul['x'] < shape['x'] and 0 <= point_ul['y'] < shape['y'] and 0 <= point_dr['x'] < shape['x'] and 0 <= point_dr['y'] < shape['y']:
        if point_ul['x'] < point_dr['x'] and point_ul['y'] < point_dr['y']:
            cv_params['img_array'] = np.copy(img_array[point_ul['y']:point_dr['y'], point_ul['x']:point_dr['x'], :])
            cv_params['exception'] = None
        else:
            cv_params['exception'] = 'Plz check the order of cut points.'
    else:
        cv_params['exception'] = 'At least 1 cut point is out of img!'
    return params


def cv_ocr_img(params):
    cv_params = params['cv']
    img_array: np.array = cv_params['img_array']
    img_pillow = Image.fromarray(img_array)
    ocr_res = pytesseract.image_to_string(image=img_pillow, config='--psm 6')
    cv_params['ocr_res'] = ocr_res
    return params


def cv_show_img(params):
    cv_params = params['cv']
    img_array: np.array = cv_params['img_array']
    if 'winname' in cv_params.keys():
        winname = cv_params['winname']
    else:
        winname = 'img'
    cv2.imshow(winname=winname, mat=img_array)
    if 'delay' in cv_params.keys():
        delay = cv_params['delay']
        cv2.waitKey(delay=delay)
    else:
        cv2.waitKey()
    return params


def cv_init_cap(params):
    cv_params = params['cv']
    filename = cv_params['filename']
    video_cap = cv2.VideoCapture(filename=filename)
    cv_params['video_cap'] = video_cap
    cv_params['fps'] = video_cap.get(cv2.CAP_PROP_FPS)
    cv_params['frame_count'] = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cv_params['width'] = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cv_params['height'] = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return params


def cv_close_cap(params):
    cv_params = params['cv']
    video_cap: cv2.VideoCapture = cv_params['video_cap']
    video_cap.release()
    return params


def cv_is_cap_opened(params):
    cv_params = params['cv']
    video_cap: cv2.VideoCapture = cv_params['video_cap']
    cv_params['is_opened'] = video_cap.isOpened()
    return params


def cv_read_cap(params):
    cv_params = params['cv']
    video_cap: cv2.VideoCapture = cv_params['video_cap']
    _, frame = video_cap.read()
    cv_params['frame_count'] -= 1
    print('剩余帧个数:{}'.format(cv_params['frame_count']))
    if frame is not None:
        cv_params['img_array'] = frame
        cv_params['exception'] = None
    else:
        cv_params['img_array'] = None
        cv_params['exception'] = 'VideoCap returned null frame array.'
    return params


if __name__ == '__main__':
    params_ = {
        'cv': {
            'img_path': 'reports/WZRY.png',
            'point_ul': {'x': 2029, 'y': 12},
            'point_dr': {'x': 2109, 'y': 36}
        }
    }
    params_ = cv_read_img(params=params_)
    params_ = cv_cut_img(params=params_)
    params_ = cv_ocr_img(params=params_)
    params_['cv']['winname'] = params_['cv']['ocr_res']
