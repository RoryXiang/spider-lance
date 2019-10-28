#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-09-18 15:57:20
# @Author  : RoryXiang (pingping19901121@gmail.com)
# @Link    : ${link}
# @Version : $Id$


import random
import numpy as np
import time
from selenium.webdriver.common.action_chains import ActionChains


def get_simple_sigmoid_tracks(dis):
    """
    通过一个sigmoid函数来生成轨迹数据，函数的整体斜率通过dis控制
    :param dis: 需要滑动的距离
    :return: 轨迹数组 [时间差，x轴总移动距离， y轴总移动距离]
    """
    dis += 10
    track = []
    t = 0.15
    tt = random.randint(6, 25) / 1000

    def sigmoid(x):
        return (1 / (1 + np.exp((-x + 0.6) * 4))) * (dis + 3)

    final_dis = sigmoid(t)
    while final_dis < dis:
        track.append([tt, final_dis, random.choice([-1, 0, 1])])
        tt = random.randint(6, 25) / 1000
        t += tt
        final_dis = sigmoid(t)
    track.append([tt, dis, random.choice([-1, 0, 1])])
    track.extend([[random.randint(6, 50) / 1000, dis,
                   random.choice([-1, 0, 1])]] * 2)
    track.extend([[0.05, dis - 3, random.choice([-1, 0, 1])],
                  [0.05, dis - 5, random.choice([-1, 0, 1])],
                  [0.05, dis - 7, random.choice([-1, 0, 1])],
                  [0.05, dis - 8, random.choice([-1, 0, 1])],
                  [0.05, dis - 9, random.choice([-1, 0, 1])],
                  [0.05, dis - 10, random.choice([-1, 0, 1])]])
    return track


class Slider(object):

    def __init__(self, browser, slider, gap_distance):
        """
        :param browser:  浏览器对象
        :param slider: 滑块对象
        :param gap_distance: 需要滑动的距离
        """
        self.browser = browser
        self.distance = gap_distance
        self.slider = slider

    def ease_out_quart(self, x):
        """
        轨迹核心函数
        :param x: 时间
        :return: 距离
        """
        return 1 - pow(1 - x, 4)

    def get_tracks(self, distance, seconds, ease_func):
        """
        根据轨迹离散分布生成的数学生成
        成功率很高 90% 往上
        :param distance: 缺口位置
        :param seconds:  时间
        :param ease_func: 生成函数
        :return: 轨迹数组
        """
        distance += 20
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            ease = ease_func
            offset = round(ease(t / seconds) * distance)
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        tracks.extend([-3, -2, -3, -2, -2, -2, -2, -1, -0, -1, -1, -1])
        return tracks

    def move_to_gap(self, tracks):
        """
        将滑块拖拽到缺口处
        :param tracks: 轨迹数组
        :return: None
        """
        ActionChains(self.browser).click_and_hold(self.slider).perform()
        while tracks:
            x = tracks.pop(0)
            ActionChains(self.browser).move_by_offset(
                xoffset=x, yoffset=0).perform()
            time.sleep(0.02)

        ActionChains(self.browser).release().perform()

    def slide(self):
        """
        整套滑动函数
        :return:
        """
        tracks = self.get_tracks(self.distance, random.randint(2, 4),
                                 self.ease_out_quart)
        self.move_to_gap(tracks)
