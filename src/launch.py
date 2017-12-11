from utils import CONSTANTS
from fabric.api import local
import time

for n in xrange(CONSTANTS.N):
    local('python messaging_service.py {} 2> e{}.txt &'.format(n, n))
    time.sleep(0.5)
