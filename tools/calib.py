import cv2 as cv
import numpy as np

vidCap = cv.VideoCapture(2)
vidCap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
vidCap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)


def create_obj_points(size):
    obj_ps = []
    for i in range(8):
        for k in range(5):
            obj_ps.append((k*25, i * 25, 0))
    list_obj = []
    for i in range(size):
        list_obj.append(np.array(obj_ps))
    return np.array(np.array(list_obj, dtype=np.float32))


img_points = []
state = 0
while state > -1:
    ret, img = vidCap.read()
    print(ret)
    print(img.shape)
    ret, corners = cv.findChessboardCorners(img, (5, 8), flags= cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE + cv.CALIB_CB_FILTER_QUADS + cv.CALIB_CB_FAST_CHECK)
    out_img = cv.drawChessboardCorners(img, (5, 8), corners, ret)
    cv.imshow(None, out_img)
    key = cv.waitKey(20)
    if key == 32:
        img_points.append(corners)
        print(len(img_points))
    elif key == 27:
        state = -1


ret, img = vidCap.read()
print(img.shape[:2][::-1])
cv.destroyAllWindows()
obj_points = create_obj_points(len(img_points))
print(obj_points)
print(img_points)
print(len(img_points))
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(obj_points, img_points, img.shape[:2][::-1], None, None)
print(ret)
np.savez("calib_webcam.npz", mtx, dist)