import numpy as np
cimport numpy as np

np.import_array()  # required in order to use C-API

cimport cython
cimport numpy as np
from libc.math cimport fabs, sqrt, exp, cos, pow

ctypedef np.float64_t DTYPE_t
cdef DTYPE = np.float64
ctypedef np.intp_t ITYPE_t

cdef inline DTYPE_t euclidean_dist(DTYPE_t* x1, DTYPE_t* x2, ITYPE_t size) nogil except -1:
    cdef DTYPE_t tmp, d=0
    cdef np.intp_t j
    for j in range(size):
        tmp = x1[j] - x2[j]
        d += tmp * tmp
    return sqrt(d)

cdef inline DTYPE_t custom_dist(DTYPE_t* x1, DTYPE_t* x2) nogil except -1:
    # 0.12 == 360.0/(WALKING_SPEED*1000)
    cdef DTYPE_t d = euclidean_dist(x1, x2, 2) * 0.12 + x1[2]
    return d

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def resolve(np.ndarray[DTYPE_t, ndim=2] stops, np.ndarray[DTYPE_t, ndim=2] gridpoints):
    cdef np.ndarray[DTYPE_t, ndim=2, mode='c'] stops_c = np.ascontiguousarray(stops, dtype = DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=2, mode='c'] gridpoints_c = np.ascontiguousarray(gridpoints, dtype= DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1, mode='c'] out = np.zeros((gridpoints.shape[0],))

    cdef np.intp_t size = gridpoints_c.shape[0]
    cdef np.intp_t nbStops = stops_c.shape[0]
    cdef np.intp_t i = 0
    cdef np.intp_t j = 0
    cdef DTYPE_t dist = 0
    cdef DTYPE_t bestdist = 0

    for i in range(size):
        bestdist = 100000000

        for j in range(nbStops):
            dist = custom_dist(&stops_c[j,0], &gridpoints_c[i,0])
            if dist < bestdist:
                bestdist = dist

        out[i] = bestdist

    return out