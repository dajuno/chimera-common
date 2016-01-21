''' Pulse sequence definitions for the Bloch solver '''


def PGSE(t, dt1, dt2):
    ''' PGSE Pulsed Gradient Spin Echo (Stejskal & Tanner) '''
    if t < dt1:
        return 1
    elif t > dt2 and t < dt1+dt2:
        return -1
    else:
        return 0
