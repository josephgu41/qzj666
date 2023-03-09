from xvfbwrapper import Xvfb

# 创建一个 Xvfb 服务器并启动
vdisplay = Xvfb()
vdisplay.start()

# 在虚拟 X 服务器中运行需要显示图形界面的程序
# 例如 matplotlib 绘图库
import matplotlib.pyplot as plt
plt.plot([1,2,3,4])
plt.show()

# 关闭 Xvfb 服务器
vdisplay.stop()
