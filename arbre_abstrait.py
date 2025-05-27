def afficher(s, indent=0):
    print(" " * indent + s)

class Programme:
    def __init__(self, listeInstructions):
        self.listeInstructions = listeInstructions
    def afficher(self, indent=0):
        afficher("<programme>", indent)
        self.listeInstructions.afficher(indent + 1)
        afficher("</programme>", indent)

class ListeInstructions:
    def __init__(self):
        self.instructions = []
    def afficher(self, indent=0):
        afficher("<listeInstructions>", indent)
        for instruction in self.instructions:
            instruction.afficher(indent + 1)
        afficher("</listeInstructions>", indent)

class Ecrire:
    def __init__(self, exp):
        self.exp = exp
    def afficher(self, indent=0):
        afficher("<ecrire>", indent)
        self.exp.afficher(indent + 1)
        afficher("</ecrire>", indent)

class EcrireChaine:
    def __init__(self, chaine):
        self.chaine = chaine
    def afficher(self, indent=0):
        afficher(f"<ecrire chaine={self.chaine}>", indent)

class Operation:
    def __init__(self, op, exp1, exp2):
        self.exp1 = exp1
        self.op = op
        self.exp2 = exp2
    def afficher(self, indent=0):
        afficher(f"<operation {self.op}>", indent)
        if self.exp1 is not None:
            self.exp1.afficher(indent + 1)
        self.exp2.afficher(indent + 1)
        afficher("</operation>", indent)

class OperationLogique:
    def __init__(self, op, exp1, exp2):
        self.exp1 = exp1
        self.op = op
        self.exp2 = exp2
    def afficher(self, indent=0):
        afficher(f"<operation_logique {self.op}>", indent)
        self.exp1.afficher(indent + 1)
        if self.exp2 is not None:
            self.exp2.afficher(indent + 1)
        afficher("</operation_logique>", indent)

class Comparaison:
    def __init__(self, op, exp1, exp2):
        self.exp1 = exp1
        self.op = op
        self.exp2 = exp2
    def afficher(self, indent=0):
        afficher(f"<comparaison {self.op}>", indent)
        self.exp1.afficher(indent + 1)
        self.exp2.afficher(indent + 1)
        afficher("</comparaison>", indent)

class Entier:
    def __init__(self, valeur):
        self.valeur = valeur
    def afficher(self, indent=0):
        afficher(f"[Entier:{self.valeur}]", indent)

class Booleen:
    def __init__(self, valeur):
        self.valeur = valeur
    def afficher(self, indent=0):
        afficher(f"[Booleen:{self.valeur}]", indent)

class Variable:
    def __init__(self, nom):
        self.nom = nom
    def afficher(self, indent=0):
        afficher(f"[Variable:{self.nom}]", indent)

class Lire:
    def __init__(self):
        pass
    def afficher(self, indent=0):
        afficher("[lire]", indent)

class Declaration:
    def __init__(self, type_, nom):
        self.type = type_
        self.nom = nom
    def afficher(self, indent=0):
        afficher("<declaration>", indent)
        afficher(f"[type:{self.type}]", indent + 1)
        afficher(f"[nom:{self.nom}]", indent + 1)
        afficher("</declaration>", indent)

class Affectation:
    def __init__(self, nom, expr):
        self.nom = nom
        self.expr = expr
    def afficher(self, indent=0):
        afficher("<affectation>", indent)
        afficher(f"[nom:{self.nom}]", indent + 1)
        self.expr.afficher(indent + 1)
        afficher("</affectation>", indent)

class DeclarationAffectation:
    def __init__(self, type_, nom, expr):
        self.type = type_
        self.nom = nom
        self.expr = expr
    def afficher(self, indent=0):
        afficher("<declarationAffectation>", indent)
        afficher(f"[type:{self.type}]", indent + 1)
        afficher(f"[nom:{self.nom}]", indent + 1)
        self.expr.afficher(indent + 1)
        afficher("</declarationAffectation>", indent)

class Conditionnelle:
    def __init__(self, condition, bloc_si, bloc_sinon=None):
        self.condition = condition
        self.bloc_si = bloc_si
        self.bloc_sinon = bloc_sinon
    def afficher(self, indent=0):
        afficher("<conditionnelle>", indent)
        afficher("<condition>", indent + 1)
        self.condition.afficher(indent + 2)
        afficher("</condition>", indent + 1)
        afficher("<si>", indent + 1)
        self.bloc_si.afficher(indent + 2)
        afficher("</si>", indent + 1)
        if self.bloc_sinon is not None:
            afficher("<sinon>", indent + 1)
            self.bloc_sinon.afficher(indent + 2)
            afficher("</sinon>", indent + 1)
        afficher("</conditionnelle>", indent)

class Boucle:
    def __init__(self, condition, bloc):
        self.condition = condition
        self.bloc = bloc
    def afficher(self, indent=0):
        afficher("<boucle>", indent)
        afficher("<condition>", indent + 1)
        self.condition.afficher(indent + 2)
        afficher("</condition>", indent + 1)
        afficher("<bloc>", indent + 1)
        self.bloc.afficher(indent + 2)
        afficher("</bloc>", indent + 1)
        afficher("</boucle>", indent)

class Retour:
    def __init__(self, expr):
        self.expr = expr
    def afficher(self, indent=0):
        afficher("<retour>", indent)
        self.expr.afficher(indent + 1)
        afficher("</retour>", indent)

class AppelFonctionExpr:
    def __init__(self, nom, args):
        self.nom = nom
        self.args = args
    def afficher(self, indent=0):
        afficher("<appelFonctionExpr>", indent)
        afficher(f"[nom:{self.nom}]", indent + 1)
        afficher("<arguments>", indent + 1)
        for arg in self.args:
            arg.afficher(indent + 2)
        afficher("</arguments>", indent + 1)
        afficher("</appelFonctionExpr>", indent)

class AppelFonctionInstr:
    def __init__(self, nom, args):
        self.nom = nom
        self.args = args
    def afficher(self, indent=0):
        afficher("<appelFonctionInstr>", indent)
        afficher(f"[nom:{self.nom}]", indent + 1)
        afficher("<arguments>", indent + 1)
        for arg in self.args:
            arg.afficher(indent + 2)
        afficher("</arguments>", indent + 1)
        afficher("</appelFonctionInstr>", indent)

class Fonction:
    def __init__(self, type_, nom, params, corps):
        self.type = type_           # type de retour ('entier', 'booleen', etc.)
        self.nom = nom              # nom de la fonction (string)
        self.params = params        # liste de paramètres (list de tuples (type, nom) ou liste d’objets paramètre)
        self.corps = corps          # bloc d’instructions (un objet ListeInstructions)

    def afficher(self, indent=0):
        afficher("<fonction>", indent)
        afficher(f"[type:{self.type}]", indent + 1)
        afficher(f"[nom:{self.nom}]", indent + 1)
        afficher("<parametres>", indent + 1)
        for p in self.params:
            # Supposons que p est un tuple (type, nom)
            afficher(f"[param type:{p[0]} nom:{p[1]}]", indent + 2)
        afficher("</parametres>", indent + 1)
        afficher("<corps>", indent + 1)
        self.corps.afficher(indent + 2)
        afficher("</corps>", indent + 1)
        afficher("</fonction>", indent)
