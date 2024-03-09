from enum import Enum
import sys

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
        sys.exit("Lexing error. " + message)
    # skips whitespace excpet newline, newline is the end of a statement
    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()
    # skips comments in code
    def skipComment(self):
        pass
    # get and return next token
    def getToken(self):
        self.skipWhitespace()
        # check the first char of token to see what it is
        # if it is a multiple char token, i.e. '!=' we will process the rest
        token = None
        # below are the basic arithmetic/end of input tokens
        if self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS)
        elif self.curChar == '-':
            token = Token(self.curChar, TokenType.MINUS)
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)
        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.NEWLINE)
        elif self.curChar == '\0':
            token = Token(self.curChar, TokenType.EOF)
        else:
            #unknown token
            self.abort("Unknown token: " + self.curChar)

        self.nextChar()
        return token

# contains original token text and type of token
class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText
        self.kind = tokenKind

# TokenType is the enum for all the types of tokens
class TokenType(Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    INDENT = 2
    STRING = 3
    # keywords
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211
