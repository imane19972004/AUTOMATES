import sys
from sly import Parser
from analyse_lexicale import FloLexer
import arbre_abstrait

class FloParser(Parser):
    tokens = FloLexer.tokens
 

    debugfile = 'parser.out'

    # Programme = liste d'instructions
    @_('listeInstructions')
    def prog(self, p):
        return arbre_abstrait.Programme(p.listeInstructions)

    @_('instruction')
    def listeInstructions(self, p):
        l = arbre_abstrait.ListeInstructions()
        l.instructions.append(p.instruction)
        return l

    @_('instruction listeInstructions')
    def listeInstructions(self, p):
        p.listeInstructions.instructions.insert(0, p.instruction)
        return p.listeInstructions

    # Instructions Ecrire
    @_('ECRIRE "(" expr ")" ";"')
    def instruction(self, p):
        return arbre_abstrait.Ecrire(p.expr)

    @_('ECRIRE "(" CHAINE ")" ";"')
    def instruction(self, p):
        return arbre_abstrait.EcrireChaine(p.CHAINE)

    # Expression booleenne ou arithmetique
    @_('expr_booleen')
    def expr(self, p):
        return p.expr_booleen

    @_('expr_arith')
    def expr_booleen(self, p):
        return p.expr_arith

    @_('VRAI')
    def expr_booleen(self, p):
        return arbre_abstrait.Booleen(True)

    @_('FAUX')
    def expr_booleen(self, p):
        return arbre_abstrait.Booleen(False)

    @_('NON expr_booleen')
    def expr_booleen(self, p):
        return arbre_abstrait.OperationLogique('non', p.expr_booleen, None)

    @_('expr_booleen ET expr_booleen')
    def expr_booleen(self, p):
        return arbre_abstrait.OperationLogique('et', p.expr_booleen0, p.expr_booleen1)

    @_('expr_booleen OU expr_booleen')
    def expr_booleen(self, p):
        return arbre_abstrait.OperationLogique('ou', p.expr_booleen0, p.expr_booleen1)

    @_('expr_arith EGAL_EGAL expr_arith')
    def expr_booleen(self, p):
        return arbre_abstrait.Comparaison('==', p.expr_arith0, p.expr_arith1)

    @_('expr_arith DIFFERENT expr_arith')
    def expr_booleen(self, p):
        return arbre_abstrait.Comparaison('!=', p.expr_arith0, p.expr_arith1)

    @_('expr_arith "<" expr_arith')
    def expr_booleen(self, p):
        return arbre_abstrait.Comparaison('<', p.expr_arith0, p.expr_arith1)

    @_('expr_arith ">" expr_arith')
    def expr_booleen(self, p):
        return arbre_abstrait.Comparaison('>', p.expr_arith0, p.expr_arith1)

    @_('expr_arith INFERIEUR_OU_EGAL expr_arith')
    def expr_booleen(self, p):
        return arbre_abstrait.Comparaison('<=', p.expr_arith0, p.expr_arith1)

    @_('expr_arith SUPERIEUR_OU_EGAL expr_arith')
    def expr_booleen(self, p):
        return arbre_abstrait.Comparaison('>=', p.expr_arith0, p.expr_arith1)

    # Expressions arithmétiques (somme, produit, facteur)
    @_('somme')
    def expr_arith(self, p):
        return p.somme

    @_('somme "+" produit')
    def somme(self, p):
        return arbre_abstrait.Operation('+', p.somme, p.produit)

    @_('somme "-" produit')
    def somme(self, p):
        return arbre_abstrait.Operation('-', p.somme, p.produit)

    @_('produit')
    def somme(self, p):
        return p.produit

    @_('produit "*" facteur')
    def produit(self, p):
        return arbre_abstrait.Operation('*', p.produit, p.facteur)

    @_('produit "/" facteur')
    def produit(self, p):
        return arbre_abstrait.Operation('/', p.produit, p.facteur)

    @_('produit "%" facteur')
    def produit(self, p):
        return arbre_abstrait.Operation('%', p.produit, p.facteur)

    @_('facteur')
    def produit(self, p):
        return p.facteur

    @_('"-" facteur')
    def facteur(self, p):
     return arbre_abstrait.Operation('neg', None, p.facteur)


    @_('"(" expr ")"')
    def facteur(self, p):
        return p.expr

    @_('ENTIER')
    def facteur(self, p):
        return arbre_abstrait.Entier(p.ENTIER)

    @_('IDENTIFIANT')
    def facteur(self, p):
        return arbre_abstrait.Variable(p.IDENTIFIANT)

    @_('LIRE "(" ")"')
    def facteur(self, p):
        return arbre_abstrait.Lire()

    @_('IDENTIFIANT "(" listeArgsOpt ")"')
    def facteur(self, p):
        return arbre_abstrait.AppelFonctionExpr(p.IDENTIFIANT, p.listeArgsOpt)

    # Gestion des types
    @_('ENTIER_TYPE')
    def type(self, p):
        return 'entier'

    @_('BOOLEEN_TYPE')
    def type(self, p):
        return 'booleen'

    # Déclaration simple ou avec affectation
    @_('type IDENTIFIANT ";"')
    def instruction(self, p):
        return arbre_abstrait.Declaration(p.type, p.IDENTIFIANT)

    @_('IDENTIFIANT "=" expr ";"')
    def instruction(self, p):
        return arbre_abstrait.Affectation(p.IDENTIFIANT, p.expr)

    @_('type IDENTIFIANT "=" expr ";"')
    def instruction(self, p):
        return arbre_abstrait.DeclarationAffectation(p.type, p.IDENTIFIANT, p.expr)

    # Bloc d'instructions
    @_('"{" listeInstructions "}"')
    def bloc(self, p):
        return p.listeInstructions

    # Conditionnelle if/else
    @_('SI "(" expr ")" bloc')
    def instruction(self, p):
        return arbre_abstrait.Conditionnelle(p.expr, p.bloc)

    @_('SI "(" expr ")" bloc SINON bloc')
    def instruction(self, p):
        return arbre_abstrait.Conditionnelle(p.expr, p.bloc0, p.bloc1)

    # Boucle while
    @_('TANTQUE "(" expr ")" bloc')
    def instruction(self, p):
        return arbre_abstrait.Boucle(p.expr, p.bloc)

    # Retourner une expression
    @_('RETOURNER expr ";"')
    def instruction(self, p):
        return arbre_abstrait.Retour(p.expr)

    # Appel de fonction en instruction (sans retour)
    @_('IDENTIFIANT "(" listeArgsOpt ")" ";"')
    def instruction(self, p):
        return arbre_abstrait.AppelFonctionInstr(p.IDENTIFIANT, p.listeArgsOpt)

    @_('type IDENTIFIANT "(" listeParamsOpt ")" bloc')
    def instruction(self, p):
        return arbre_abstrait.Fonction(p.type, p.IDENTIFIANT, p.listeParamsOpt, p.bloc)

    # Liste des arguments pour appel de fonction
    @_('expr')
    def listeArgs(self, p):
        return [p.expr]

    @_('listeArgs "," expr')
    def listeArgs(self, p):
        p.listeArgs.append(p.expr)
        return p.listeArgs

    @_('')
    def listeArgsOpt(self, p):
        return []

    @_('listeArgs')
    def listeArgsOpt(self, p):
        return p.listeArgs

    # Liste des paramètres (type + identifiant)
    @_('')
    def listeParamsOpt(self, p):
        return []

    @_('listeParams')
    def listeParamsOpt(self, p):
        return p.listeParams

    @_('type IDENTIFIANT')
    def listeParams(self, p):
        return [(p.type, p.IDENTIFIANT)]

    @_('listeParams "," type IDENTIFIANT')
    def listeParams(self, p):
        p.listeParams.append((p.type, p.IDENTIFIANT))
        return p.listeParams

    def error(self, p):
        print('Erreur de syntaxe', p, file=sys.stderr)
        exit(1)





if __name__ == '__main__':
    lexer = FloLexer()
    parser = FloParser()
    if len(sys.argv) < 2:
        print("usage: python3 analyse_syntaxique.py NOM_FICHIER_SOURCE.flo")
    else:
        with open(sys.argv[1], "r") as f:
            data = f.read()
            try:
                arbre = parser.parse(lexer.tokenize(data))
                arbre.afficher()
                #verifier le type 
                arbre.verifier_type()
                #generatiin de code
                print("Code généré :")
                print(arbre.generer_code())
            except EOFError:
                exit(1)
            except Exception as e:
                print(f"Erreur : {e}")
