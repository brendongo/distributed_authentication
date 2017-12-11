import numpy as np
import matplotlib.pyplot as plt
import json

def smooth(values, weight=.5):
    """First-order low pass filter -- filter out high frequencies.

    This is the same method as in Tensorboard.
    """
    smoothed = []
    for x in values:
        if not smoothed:
            smoothed.append(x)
        else:
            smoothed.append(smoothed[-1] * weight + x * (1 - weight))
    return np.array(smoothed)

DOMAINS = ["rsa"]

fig = plt.figure(figsize=(10, 5))
for domain in DOMAINS:
    with open(domain, "r") as f:
        data = json.loads(f.read())
        plt.plot(data, xrange(len(data)), label=domain)
plt.title("RSA vs ECDSA")
plt.ylabel("Fulfilled Requests")
plt.xlabel("Time (s)")
plt.legend()
fig.savefig("figure.pdf")
