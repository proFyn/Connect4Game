

def setDiff() :
    while True : 
            try :
                level= int(input("select the difficulty : easy(1) , medium(2) , hard(3), expert(4) :"))
            except :
                print('invalid input')
                continue
            if ( level>4 or level<1 ) :
                print('choose difficulty between 1 and 4 ')
                continue
            break
    return level


