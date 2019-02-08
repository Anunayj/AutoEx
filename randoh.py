import random
import string
def randoo():
    randoh = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(24)])
    return(randoh)
