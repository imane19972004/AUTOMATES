import sys
from sly import Lexer

class FloLexer(Lexer):
    tokens = (
        IDENTIFIANT, ENTIER, ECRIRE, LIRE, RETOURNER, TANTQUE, FONCTION,
        INFERIEUR_OU_EGAL, SUPERIEUR_OU_EGAL, EGAL_EGAL, DIFFERENT,
        ET, OU, NON, SI, SINON, VRAI, FAUX, ENTIER_TYPE, BOOLEEN_TYPE,
        CHAINE
    )

    literals = {'+', '-', '*', '/', '%', '(', ')', ';', '=', '{', '}', ',', '>', '<'}
    ignore = ' \t'
    ignore_comment = r'\#.*'

    INFERIEUR_OU_EGAL = r'<='
    SUPERIEUR_OU_EGAL = r'>='
    EGAL_EGAL = r'=='
    DIFFERENT = r'!='

    CHAINE = r'"[^\n"]*"'

    @_(r'0|[1-9][0-9]*')
    def ENTIER(self, t):
        t.value = int(t.value)
        return t

    IDENTIFIANT = r'[a-zA-Z][a-zA-Z0-9_]*'

    IDENTIFIANT['ecrire'] = ECRIRE
    IDENTIFIANT['lire'] = LIRE
    IDENTIFIANT['si'] = SI
    IDENTIFIANT['sinon'] = SINON
    IDENTIFIANT['retourner'] = RETOURNER
    IDENTIFIANT['tantque'] = TANTQUE
    IDENTIFIANT['fonction'] = FONCTION    # <-- Ajout ici
    IDENTIFIANT['et'] = ET
    IDENTIFIANT['ou'] = OU
    IDENTIFIANT['non'] = NON
    IDENTIFIANT['VRAI'] = VRAI
    IDENTIFIANT['FAUX'] = FAUX
    IDENTIFIANT['entier'] = ENTIER_TYPE
    IDENTIFIANT['booleen'] = BOOLEEN_TYPE
    
   



    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print(f'Ligne {self.lineno}: caractère inattendu "{t.value[0]}"', file=sys.stderr)
        self.index += 1
        exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("usage: python3 analyse_lexicale.py NOM_FICHIER_SOURCE.flo")
    else:
        with open(sys.argv[1], 'r') as f:
            data = f.read()
            lexer = FloLexer()
            for tok in lexer.tokenize(data):
                print(tok)
