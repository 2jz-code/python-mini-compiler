class Lexer:
    def __init__(self, source):
        self.source = source + '\n'
        self.curChar = ''
        self.curPos = -1
        self.nextChar()

    # process next char
    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0' #EOF
        else:
            self.curChar = self.source[self.curPos]
                
    # return the lookahead character
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos + 1]
    
    # invalid token found, send error message and exit
    def abort(self, message):
        pass
    # skips whitespace excpet newline, newline is the end of a statement
    def skipWhitespace(self):
        pass
    # skips comments in code
    def skipComment(self):
        pass
    # get and return next token
    def getToken(self):
        pass
