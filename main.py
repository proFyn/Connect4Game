# main.py
from board import board
from players import player, ai_player
import numpy as np
from vars import setDiff

level=setDiff()
while True :

   if not player(1) :
       break
   if np.all(board !=0) :
            print("Draw!")
            break
        
   if not ai_player(2,level) : 
       break
   if np.all(board !=0) :
            print("Draw!")
            break
   


   