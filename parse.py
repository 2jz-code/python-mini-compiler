import sys
from lex import *
from emit import *

# parser object keeps track of current token and checks if the code matches the grammar
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        
        self.symbols = set()        # variables declared so far
        self.labelsDeclared = set() # Labels declared so far
        self.labelsGotoed = set()   # Labels goto'ed so far

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken() #called twice to initialize curToken and peekToken

    # return true if the current token matches
    def checkToken(self,kind):
        return kind == self.curToken.kind

    # return true if the next token matches
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    #Try to match current token. If not, throw an error and advance token
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # Advances token
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken() 
    
    def abort(self, message):
        sys.exit("Error. " + message)

    # program ::= {statement}
    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")

        # Since some newlines are required in grammer, need to skip excess newlines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # parse all of the statements in the program
        while not self.checkToken(TokenType.EOF):
            self.statement()

        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        # Check that each label referenced in a GOTO is declared
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to an undeclared label: " + label)

    def statement(self):
        #Check the first token to see what kind of statement this is

        #'PRINT' (expression | string)
        if self.checkToken(TokenType.PRINT):

            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # simple string, so print it
                self.emitter.emitLine("printf(\"" + self.curToken.text + "\\n\");")
                self.nextToken()
            else:
                # Expect an expression and print result as a float
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emitLine("));")

        #'IF' comparison 'THEN' {statement} 'ENDIF'
        elif self.checkToken(TokenType.IF):

            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")

            # Zero or more statements in the body
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")
        
        # 'WHILE' comparison 'REPEAT' {statement} 'ENDWHILE'
        elif self.checkToken(TokenType.WHILE):

            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")

            # zero or more statements in the loop body
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")

        # 'LABEL ident
        elif self.checkToken(TokenType.LABEL):
            
            self.nextToken()

            # Make sure this label doesn't already exist
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)

        # 'GOTO' ident
        elif self.checkToken(TokenType.GOTO):

            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        # 'LET' ident '=' expression
        elif self.checkToken(TokenType.LET):

            self.nextToken()

            # check if ident exist in symbol table. if not, declare it
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()
            self.emitter.emitLine(";")

        # 'INPUT' ident
        elif self.checkToken(TokenType.INPUT):

            self.nextToken()

            # If variable doesn't already exist, declare it
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            #emit scanf and also validate input
            self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " =0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")

            self.match(TokenType.IDENT)

        #invalid statement. throw error
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        self.nl()

    def nl(self):

        # Require at least one newline
        self.match(TokenType.NEWLINE)

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):

        self.expression()

        # Must be at least one comparison operator and another expression
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.curToken.text)

        # can have 0 or more comparison operators and expressions.
            while self.isComparisonOperator():
                self.emitter.emit(self.curToken.text)
                self.nextToken()
                self.expression()
    
    # Returns true if the token is any of the comparison operators below
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)
    
    # expression ::= term {( "-" | "+" ) term}
    def expression(self):

        self.term()

        # can have 0 or more +/- and expressions
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    # term :: unary {("/" | "*") unary}
    def term(self):

        self.unary()

        # can have 0 or more * / / and expressions
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    # unary ::= ["+" | "-"] primary
    def unary(self):

        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
 
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure that variable already exists
            if self.curToken.text not in self.symbols:
                self.abort("Referencing a variable before assignment: " + self.curToken.text)
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        else:
            # error
            self.abort("Unexpected token at " + self.curToken.text)

