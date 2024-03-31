import json
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Load file
    with open('emotions.json') as fp:
        tracks = json.load(fp)

    plt.clf()

    xs = []
    ys = []
    labels = []
    for id in tracks:
        x, y = tracks[id]["emotion"]
        xs.append((x*2)-1)
        ys.append((y*2)-1)
        artists = ', '.join(tracks[id]['artists'])
        labels.append(f"{tracks[id]['name']} BY {artists}")

    plt.scatter(xs, ys, c=ys, cmap='plasma')

    ax = plt.gca()
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    # adding vertical line in data co-ordinates
    plt.axvline(0, c='black', ls='--')
    # adding horizontal line in data co-ordinates
    plt.axhline(0, c='black', ls='--')

    for idx, label in enumerate(labels):
        x = xs[idx]
        y = ys[idx]

        plt.annotate(label,  # this is the text
                     (x, y),  # these are the coordinates to position the label
                     textcoords="offset points",  # how to position the text
                     xytext=(0, 10),  # distance from text to points (x,y)
                     ha='center')  # horizontal alignment can be left, right or center

    plt.show()

