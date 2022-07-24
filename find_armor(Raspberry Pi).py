# -*-coding: utf-8 -*-
"""
MIT LICENSE:
#----------------------------------------------------------------------------------------#
CopyRight(C) 2021 gavin_xiang(ohhhyea) All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#----------------------------------------------------------------------------------------#
    @Project: python(Raspberry Pi 4b 2G)
    @E-mail : gavin_xiang666@qq.com
#----------------------------------------------------------------------------------------#
"""
#导入第三方库
import numpy as np
import cv2
import time, serial

index_bool = False
AspectRation = 0
# 设置需要识别的颜色
#蓝色armor
Color_lower = np.array([100, 123, 120])
Color_upper = np.array([160, 255, 230])  # 这里是设置颜色
#红色armor
#Color_lower = np.array([120, 150,100])
#Color_upper = np.array([180, 255, 250])

serial_port = 115200#设置串口波特率
Serial = serial.Serial("/dev/ttyUSB0", serial_port)#设置初始化串口(usb转ttl)


# 摄像头参数定义,设置
def Camera_init():
    cap.set(3, 1000)
    cap.set(4, 1000)

    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)

    cap.set(cv2.CAP_PROP_BRIGHTNESS, 1)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    cap.set(cv2.CAP_PROP_EXPOSURE, 7)#设置曝光
    # cap.set(cv2.CAP_PROP_SATURATION, 100)


try:  # try尝试语句,防止报错:
    cap = cv2.VideoCapture(0)
    index_bool = True
    Camera_init()
except:  # 如果报错则运行下面的代码:
    index_bool = False
    print("摄像头异常.....")


# 主函数代码
def Start_Program(bool_set):
    if bool_set == True:
        if index_bool == True:
            while True:#重复运行
                ret, frame = cap.read()  # 读取摄像头,获取视频流,ret表示是否读取到视频流,frame表示获取到的图像信息

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # HSV颜色设置
                mask = cv2.inRange(hsv, Color_lower, Color_upper)#提取在HSV范围内的图像

                kernel = np.ones((1, 1), np.uint8)

                k = np.ones((2, 2), np.uint)
                mask = cv2.dilate(mask, k, iterations=5)#膨胀
                k = np.ones((3, 3), np.uint)
                mask = cv2.dilate(mask, k, iterations=2)#膨胀
                res = cv2.bitwise_and(frame, frame, mask=mask)
                # 寻找轮廓并绘制轮廓
                cnts = cv2.findContours(mask.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
                try:  # try尝试语句,防止报错:
                    cnt = max(cnts, key=cv2.contourArea)#找到最大的轮廓
                    (x1, y1), r = cv2.minEnclosingCircle(cnt)#获取轮廓的x,y坐标，半径参数
                    x, y, w, h = cv2.boundingRect(cnts[0])#获取宽高等参数w,h
                except:#如果报错则运行下面代码
                    r = 0  # Nothing
                if len(cnts) >= 0 and r > 1:#当扫描到了轮廓，且半径大于1
                    if y > 200 and w >= 4 and h >= 4 and w < 200 and h < 200:#根据场地光线编写特殊判断
                        cv2.circle(frame, (int(x1), int(y1)), int(r), (255, 255, 67), 2)
                        # 找到物体的位置坐标,获得颜色物体的位置，可以来控制小车的转向
                        print("X_position:", int(x1), "Y_position:", int(y1), "s:", r)
                        string = str(int(x1)) + "," + str(int(y1)) + "," + str(int(r))#设置要发送出去的信息
                        Serial.write(string.encode('utf-8'))#发送信息给EP机器人
                        time.sleep(0.05)#增加一点延迟,可根据情况更改
                #显示部分，可以注释，不影响程序运行
                cv2.imshow('frame', frame)
                cv2.imshow('mask', mask)
                cv2.imshow('res', res)
                if cv2.waitKey(5) & 0xFF == 27:
                    break#退出
            # -----------END------------
            cap.release()
            cv2.destroyAllWindows()
        elif index_bool == False:
            print("--请检查摄像头连接----------------")
        else:
            print("程序异常,请尝试重启...")
    elif bool_set == False:
        pass  # 跳过
    else:
        print("<attention:>请注意修改主函数的bool_set值...")

#主程序运行处
if __name__ == "__main__":
    Start_Program(True)  # bool_set

