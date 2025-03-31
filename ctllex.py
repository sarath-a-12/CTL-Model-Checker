from sly import Lexer

class CTLLexer(Lexer):
    #set of token names
    tokens = {AF, EF, AG, EG, AX, EX, VAR, IMPLIES, TRUE, FALSE}
    # tokens = {VAR, MAIN}
    ignore = ' \t '
    literals = {'[',']', '(', ')', '&','|', ',', '~', 'U', 'A', 'E'}

    # ignore_comment = r'\/\/.*'
    # ignore_newline = r'\n+'
    IMPLIES = r'->'
    TRUE = r'T'
    FALSE = r'F'
    # ADD = r'\+'
    # SUB = r'-'
    # MUL = r'\*'
    # DIV = r'/'
    # EQ = r'=='
    # ASSIGN = r'='
    # LTE = r'<='
    # LT = r'<'
    # GTE = r'>='
    # GT = r'>'
    # NE = r'!='

    VAR = r'[a-z_][a-z0-9_]*'




    # def error(self, t):
    #     print(f"Illegal character encountered {t.value[0]}") 


    @_('AF')
    def AF(self, t):
        return t

    @_('EF')
    def EF(self, t):
        return t

    @_('AG')
    def AG(self, t):
        return t

    @_('EG')
    def EG(self, t):
        return t

    @_('AX')
    def AX(self, t):
        return t

    @_('EX')
    def EX(self, t):
        return t

    @_('AU')
    def AU(self, t):
        return t

    @_('EU')
    def EU(self, t):
        return t


    # @_(r'\n+')
    # def ignore_newline(self, t):
    #     self.lineno += len(t.value)


# if __name__ == "__main__":
#     lexer = CalcLexer()
#     for token in lexer.tokenize('AG(AU[p,EF(q&!r)])'):
#         # print(f"{token.type} , {token.value}")
#         pass
    # for token in lexer.tokenize('AF EG EX'):
    #     print(f"This is the token = {token}")
