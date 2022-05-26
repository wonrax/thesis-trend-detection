from matplotlib import pyplot as plt
import numpy as np

plt.figure()
loc = 7
a = np.random.normal(loc=loc, scale=4, size=24)
a = np.concatenate((a, np.random.normal(loc=loc, scale=36, size=16)))

# filter points larger than 36 and smaller than 0
a = a[(a > 0) & (a < 36)]


def rand_color():
    color = list(np.random.choice(range(64, 192), size=3))
    # normalize
    color = [c / 255 for c in color]
    return tuple(color)


# generate length a random rgb color tuples
colors = [rand_color() for _ in range(len(a))]
print(colors[0])


average_point = np.average(a)

print(a)
print(len(a))
print(len(colors))
ax = plt.subplot(111)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines['bottom'].set_position(('data', -0.01))
ax.get_yaxis().set_visible(False)
ax.hlines(0, 0, 36)  # Draw a horizontal line

# for enumerate
for i, point in enumerate(a):
    ax.eventplot(
        [point],
        orientation="horizontal",
        lineoffsets=0,
        linelengths=0.02,
        linewidths=1,
        colors=colors[i],
    )

ax.set(xlabel='Giờ tương đối (h)')
ax.tick_params(axis='both', which='both', length=0)

# plot average point
plt.plot(average_point, 0, "ro", markersize=12)
plt.text(average_point, 0.02, "Trung bình", fontsize=12, horizontalalignment="center")

plt.xlim([0, 36])
plt.ylim([-0.1, 0.1])
# plt.axis('off')
figure = plt.gcf()
figure.set_size_inches(12, 4)
plt.savefig("test.png", transparent=True, dpi=300)
plt.show()
