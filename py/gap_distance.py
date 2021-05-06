import numpy as np
import cv2
from scipy import signal


class GapCalculator(object):

    def __init__(self, bg_img, slider_img):
        self.bg_array = bg_img
        self.s_array = slider_img
        self._type_change()

    def _type_change(self):
        """
        图片类型转换，将response.content:tytes转换成cv能计算的ndarray
        :return:
        """
        if isinstance(self.bg_array, bytes):
            image = np.fromstring(self.bg_array, np.uint8)
            self.bg_array = cv2.imdecode(image, cv2.IMREAD_COLOR)
        if isinstance(self.s_array, bytes):
            image = np.fromstring(self.s_array, np.uint8)
            self.s_array = cv2.imdecode(image, cv2.IMREAD_COLOR)

    def pic2gray(self, img_array: np.ndarray, save=False) -> np.ndarray:
        """
        图像转为灰度图
        :param img_array: 图片向量
        :param save:
        :return:
        """
        img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        if save:
            cv2.imwrite("tmp.png", img_array)
        return img_array

    def canny_edge(self, img_array: np.ndarray, show=False) -> np.ndarray:
        """
        锐化边缘
        :param img_array:
        :param show:
        :return:
        """
        can = cv2.Canny(img_array, threshold1=200, threshold2=300)
        if show:
            cv2.imshow('candy', can)
            cv2.waitKey()
            cv2.destroyAllWindows()
        return can

    def clear_white(self, img_array: np.ndarray) -> np.ndarray:
        """
        清除空白区
        :param img_array:
        :return:
        """
        rows, cols, _ = img_array.shape
        max_x = 0
        max_y = 0
        min_x = 255
        min_y = 255
        for x in range(1, rows):
            for y in range(1, cols):
                # print(img_array[x, y])
                t = set(img_array[x, y])
                if len(t) >= 2:
                    if x <= min_x:
                        min_x = x
                    elif x >= max_x:
                        max_x = x
                    if y <= min_y:
                        min_y = y
                    elif y >= max_y:
                        max_y = y
        new_img_array = img_array[min_x:max_x, min_y:max_y]
        return new_img_array

    def convolve2d(self, bg: np.ndarray, fillter: np.ndarray) -> np.ndarray:
        """
        same 2d卷积
        :param bg:
        :param fillter:
        :return:
        """
        bg_h, bg_w = bg.shape[:2]
        fillter_h, fillter_w = fillter.shape[:2]
        c_full = signal.convolve2d(bg, fillter, mode="full")
        kr, kc = fillter_h // 2, fillter_w // 2
        c_same = c_full[
                 fillter_h - kr - 1: bg_h + fillter_h - kr - 1,
                 fillter_w - kc - 1: bg_w + fillter_w - kc - 1
                 ]
        return c_same

    def find_max_point(self, arrays: np.ndarray, search_on_horizontal_center=False) -> tuple:
        """
        找二维数组中最大的点
        :param arrays:
        :param search_on_horizontal_center:
        :return:
        """
        max_point = 0
        max_point_pos = None
        array_rows, arrays_cols = arrays.shape

        if search_on_horizontal_center:
            for col in range(array_rows):
                if arrays[array_rows // 2, col] > max_point:
                    max_point = arrays[array_rows // 2, col]
                    max_point_pos = col, array_rows // 2
        else:
            for row in range(array_rows):
                for col in range(arrays_cols):
                    if arrays[row, col] > max_point:
                        max_point = arrays[row, col]
                        max_point_pos = row, col
        max_img = self.bg_array[max_point_pos[0]:max_point_pos[0] + 100, max_point_pos[1]:max_point_pos[1] +100]
        cv2.imshow("best", max_img)
        cv2.waitKey()
        cv2.destroyAllWindows()
        return max_point_pos

    def match(self, bg: np.ndarray, s: np.ndarray):
        res = cv2.matchTemplate(bg, s, cv2.TM_CCOEFF_NORMED)
        # cv2.imshow("res", res)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配
        th, tw = s.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0]+tw, tl[1]+th)  # 右下角点的坐标
        cv2.rectangle(bg, tl, br, (0, 0, 255), 2)  # 绘制矩形
        cv2.imwrite("ttt.png", bg)  # 保存在本地
        return tl[0]

    def find(self):
        self.bg_array = self.pic2gray(self.bg_array)
        self.bg_array = self.canny_edge(self.bg_array)
        fillter = self.clear_white(self.s_array)
        fillter = self.pic2gray(fillter)
        fillter = self.canny_edge(fillter)
        m = self.match(self.bg_array, fillter)
        return m