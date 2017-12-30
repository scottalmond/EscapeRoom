import numpy as np
import cv2

#sample 2D array that featues concentric circles
circlesArr = np.ndarray((512,512),dtype=np.float32)
for i in range(10,600,10): cv2.circle(circlesArr,(256,256),i-10,np.random.randint(60,500),thickness=4)

#logpolar
lp = np.ndarray((512,512),dtype=np.float32)
cv2.linearPolar(circlesArr,lp,(256,256),100,cv2.WARP_FILL_OUTLIERS)

#logpolar Inverse
#lpinv = np.ndarray((512,512),dtype=np.float32)
#cv2.linearPolar(lp,lpinv,(256,256),100, cv2.WARP_INVERSE_MAP + cv2.WARP_FILL_OUTLIERS)

#display images
from scipy.misc import toimage
toimage(lp, mode="L").show()
#toimage(lpinv, mode="L").show()
