from time import sleep


def run():
    '''
        Main function.
        Runs sync function every 5 minutes
    '''
    while True:
        sync()
        sleep(1000)



def sync():
    '''

    '''
    print("syncing...")