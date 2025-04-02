from sly import Lexer

class CTLLexer(Lexer):
    #set of token names
    tokens = {AF, EF, AG, EG, AX, EX, VAR, IMPLIES, TRUE, FALSE}
    ignore = ' \t '
    literals = {'[',']', '(', ')', '&','|', ',', '~', 'U', 'A', 'E'}

    IMPLIES = r'->'
    TRUE = r'T'
    FALSE = r'F'
    VAR = r'[a-z_][a-z0-9_]*'


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
