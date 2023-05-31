from collections import namedtuple

import cv2 as cv


CAM_ID = 0
CUBES = 30
CUBE_ID_OFFSET = 1
marker_dict = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_4X4_250)


def detect_cubes():
    detecting = True
    rob = RobustDetector(10, 5)
    cap = cv.VideoCapture(CAM_ID, cv.CAP_DSHOW)
    found_cubes = []
    missing_cubes = list(range(CUBES))
    while detecting:
        ret, img = cap.read()
        if img is not None:
            cv.aruco.detectMarkers(img, marker_dict)
            marker_corners, marker_ids, rej = cv.aruco.detectMarkers(img, marker_dict)
            #if marker_ids is not None:
            f_ids = rob.filter(marker_ids)
            for idx in f_ids:
                cube_id = _marker_id_to_cube_id(idx)
                if cube_id not in found_cubes:
                    found_cubes.append(cube_id)
                if cube_id in missing_cubes:
                    missing_cubes.remove(cube_id)
            if marker_ids is not None:
                cv.aruco.drawDetectedMarkers(img, marker_corners, marker_ids)
            cv.imshow('', img)
            pressed_key = cv.waitKey(16)
            if pressed_key == 32:
                detecting = False
    print(f'Found {len(found_cubes)} cubes.')
    if len(missing_cubes) > 0:
        print(f'{len(missing_cubes)} are missing.\n'
              'Following cubes are missing:')
        strs = []
        # missing_cubes += 1
        for i, cube in enumerate(missing_cubes):
            strs.append(str(cube + 1))
            strs.append(', ')
            if (i + 1) % 6 == 0:
                strs.append('\n')
        missing_cubes_str = ''.join(strs)
        print(missing_cubes_str)
    else:
        print('No cubes are missing.')
    
AGING_STEP = 1

class RobustDetector:
    def __init__(self, max_age: int, min_frames: int):
        self.max_age = max_age
        self.min_frames = min_frames
        self.markers_detected = {}
        self.frame_counter = 0

    def filter(self, marker_ids):
        ret_ids = []
        if marker_ids is not None:
            for i in range(marker_ids.shape[0]):
                idx = marker_ids[i][0]
                if self.detect(idx):
                    ret_ids.append(idx)
        self.aging()
        return ret_ids
        
    def detect(self, marker_id):
        if marker_id in self.markers_detected:
            self.markers_detected[marker_id][0] += 1
            self.markers_detected[marker_id][1] -= AGING_STEP
            if self.markers_detected[marker_id][0] > self.min_frames:
                return True
        else:
            self.markers_detected[marker_id] = [1, 0]
        return False

    def aging(self):
        keys = list(self.markers_detected.keys())
        for key in keys:
            self.markers_detected[key][1] += 1
            if self.markers_detected[key][1] > self.max_age:
                del self.markers_detected[key]

def _marker_id_to_cube_id(marker_id: int):
    cube_id = marker_id // 6
    return cube_id


if __name__ == "__main__":
    detect_cubes()