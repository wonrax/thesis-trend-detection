import matplotlib.pyplot as plt
import math
from matplotlib import font_manager
import numpy as np

font_path = r"C:\Program Files\Fonts\Cascadia\CascadiaCode-Regular.otf"  # Your font path goes here
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = prop.get_name()

x = np.arange(0.0, 25.0, 0.1)
y = [2 / math.log(0.01 * e + 1.05) for e in x]
y2 = [2 / math.log(0.1 * e + 1.05) for e in x]
fig = plt.figure() 
#matplotlib.pyplot.axhline(y=0, xmin=0, xmax=1, hold=None, **kwargs)
plt.axhline(linewidth=1, color='#252025') #adds thick red line @ y=0
#matplotlib.pyplot.axvline(x=0, ymin=0, ymax=1, hold=None, **kwargs)
plt.axvline(linewidth=1, color='#252025') #adds thick red line @ x=0
ax = plt.subplot(111)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
plt.plot(x[0], y[0], 'go')
ax.yaxis.set_label_position("right")
ax.yaxis.tick_right()
plt.plot(x, y, '-r', label=r"$\alpha=0.01$")
plt.plot(x, y2, '-b', label=r"$\alpha=0.1$")
plt.xlabel('x', color='#1C2833')
plt.ylabel('y', color='#1C2833')
plt.title(r"Đồ thị cho công thức $\frac{2}{ln(\alpha x + 1.05)}$", color='#252025')
plt.legend(loc='upper left')
ax.legend(loc="upper right")
plt.grid()
plt.show()