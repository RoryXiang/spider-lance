import random
import numpy as np
import time
from selenium.webdriver.common.action_chains import ActionChains


def sigmod_similary_tracks_finaldis(distance: int):
    """生成滑动轨迹，最终二位数组是[[滑动时间间隔，滑块到开始滑动的距离]]
    Arguments:
            distance {[[float, float]]} -- [[滑动时间间隔，滑块到开始滑动的距离]]
    """
    distance += 10
    tracks = []
    x_time = 0.2
    delta_time = random.randint(6, 45) / 100

    def sigmod(x):
        return (1 / (1 + np.exp((-x + 0.6) * 0.4))) * (distance + 3)
    final_distance = sigmod(x_time)
    while final_distance < distance:
        if not tracks:
            tracks.append([x_time, final_distance])
        else:
            tracks.append([delta_time, final_distance])
        delta_time = random.randint(6, 45) / 100
        x_time += delta_time
        final_distance = sigmod(x_time)
    tracks.append([delta_time, final_distance])
    tracks.extend([
        [0.05, distance - 3], [0.05, distance - 5],
        [0.05, distance - 8], [0.05, distance - 9], [0.05, distance - 10]
    ])
    return tracks


def sigmod_similary_tracks_slidedis(distance: int):
    """生成滑动轨迹，最终二位数组是[[滑动时间间隔，滑动时间间隔内滑动的距离]]

    Arguments:
            distance {[[float, float]]} -- [[滑动时间间隔，滑动时间间隔内滑动的距离]]
    """
    distance += 10
    tracks = []
    x_time = 0.2
    delta_time = random.randint(6, 45) / 100

    def sigmod(x):
        return (1 / (1 + np.exp((-x + 0.6) * 0.4))) * (distance + 3)
    final_distance = sigmod(x_time)
    while final_distance < distance:
        if not tracks:
            tracks.append([x_time, final_distance])
        else:
            slide_gap = final_distance - sigmod(x_time - delta_time)
            tracks.append([delta_time, slide_gap])
        delta_time = random.randint(6, 45) / 100
        x_time += delta_time
        final_distance = sigmod(x_time)
    slide_gap = final_distance - tracks[-1][-1]
    tracks.append([delta_time, slide_gap])
    tracks.extend([
        [0.05, -3], [0.05, -2],
        [0.05, -3], [0.05, -1], [0.05, -1]
    ])
    return tracks


class Slider(object):

    def __init__(self, browser, gap, distance):
        """
        Arguments:
            browser {[selenium browser]} -- [浏览器对象]
            gap {[browser element]} -- [滑块对象]
            distance {[float]} -- [需要滑动的距离]
        """
        self.browser = browser
        self.gap = gap
        self.distance = distance

    def move_gap_to_target(self, tracks):
        ActionChains(self.browser).click_and_hold(self.gap).perform()
        while tracks:
            track = tracks.pop(0)
            ActionChains(self.browser).move_by_offset(
                xoffset=track[-1], yoffset=0
            ).perform()
            time.sleep(track[0])

    def slide(self):
        tracks = sigmod_similary_tracks_slidedis(self.distance)
        self.move_gap_to_target(tracks)
