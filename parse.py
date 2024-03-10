import sys
from lex import *

# parser object keeps track of current token and checks if the code matches the grammar
class Parser:
    def __init__(self, lexer):
        pass

    # return true if the current token matches
    def checkToken(self,kind):
        pass

    # return true if the next token matches
    def checkPeek(self, kind):
        pass

    #Try to match current token. If not, throw an error and advance token
    def match(self, kind):
        pass

    # Advances token
    def nextToken(self):
        pass
    
    def abort(self, message):
        sys.exit("Error. " + message)
    