import sys
from sly import Parser
from analyse_lexicale import FloLexer
import arbre_abstrait
from table_symboles import TableSymboles

class FloParser(Parser):
    tokens = FloLexer.tokens
    debugfile = 'parser.out'

    def __init__(self):
        self.table_symboles = TableSymboles()
        self.validation_active = True  # Pour contrôler la validation

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

    # Expression - niveau le plus élevé
    @_('expr_ou')
    def expr(self, p):
        return p.expr_ou

    # Expressions booléennes avec hiérarchie explicite
    # Niveau 1: OU (priorité la plus faible)
    @_('expr_ou OU expr_et')
    def expr_ou(self, p):
        return arbre_abstrait.OperationLogique('ou', p.expr_ou, p.expr_et)

    @_('expr_et')
    def expr_ou(self, p):
        return p.expr_et

    # Niveau 2: ET
    @_('expr_et ET expr_non')
    def expr_et(self, p):
        return arbre_abstrait.OperationLogique('et', p.expr_et, p.expr_non)

    @_('expr_non')
    def expr_et(self, p):
        return p.expr_non

    # Niveau 3: NON (opérateur unaire)
    @_('NON expr_non')
    def expr_non(self, p):
        return arbre_abstrait.OperationLogique('non', p.expr_non, None)

    @_('expr_comp')
    def expr_non(self, p):
        return p.expr_comp

    # Niveau 4: Comparaisons
    @_('expr_comp EGAL_EGAL expr_add')
    def expr_comp(self, p):
        return arbre_abstrait.Comparaison('==', p.expr_comp, p.expr_add)

    @_('expr_comp DIFFERENT expr_add')
    def expr_comp(self, p):
        return arbre_abstrait.Comparaison('!=', p.expr_comp, p.expr_add)

    @_('expr_comp "<" expr_add')
    def expr_comp(self, p):
        return arbre_abstrait.Comparaison('<', p.expr_comp, p.expr_add)

    @_('expr_comp ">" expr_add')
    def expr_comp(self, p):
        return arbre_abstrait.Comparaison('>', p.expr_comp, p.expr_add)

    @_('expr_comp INFERIEUR_OU_EGAL expr_add')
    def expr_comp(self, p):
        return arbre_abstrait.Comparaison('<=', p.expr_comp, p.expr_add)

    @_('expr_comp SUPERIEUR_OU_EGAL expr_add')
    def expr_comp(self, p):
        return arbre_abstrait.Comparaison('>=', p.expr_comp, p.expr_add)

    @_('expr_add')
    def expr_comp(self, p):
        return p.expr_add

    # Niveau 5: Addition et soustraction
    @_('expr_add "+" expr_mult')
    def expr_add(self, p):
        return arbre_abstrait.Operation('+', p.expr_add, p.expr_mult)

    @_('expr_add "-" expr_mult')
    def expr_add(self, p):
        return arbre_abstrait.Operation('-', p.expr_add, p.expr_mult)

    @_('expr_mult')
    def expr_add(self, p):
        return p.expr_mult

    # Niveau 6: Multiplication, division, modulo
    @_('expr_mult "*" expr_unaire')
    def expr_mult(self, p):
        return arbre_abstrait.Operation('*', p.expr_mult, p.expr_unaire)

    @_('expr_mult "/" expr_unaire')
    def expr_mult(self, p):
        return arbre_abstrait.Operation('/', p.expr_mult, p.expr_unaire)

    @_('expr_mult "%" expr_unaire')
    def expr_mult(self, p):
        return arbre_abstrait.Operation('%', p.expr_mult, p.expr_unaire)

    @_('expr_unaire')
    def expr_mult(self, p):
        return p.expr_unaire

    # Niveau 7: Opérateurs unaires (priorité la plus élevée)
    @_('"-" expr_unaire')
    def expr_unaire(self, p):
        return arbre_abstrait.Operation('-', exp1=p.expr_unaire)


    @_('expr_primaire')
    def expr_unaire(self, p):
        return p.expr_primaire

    # Niveau 8: Expressions primaires (atomes)
    @_('"(" expr ")"')
    def expr_primaire(self, p):
        return p.expr

    @_('ENTIER')
    def expr_primaire(self, p):
        return arbre_abstrait.Entier(p.ENTIER)

    @_('VRAI')
    def expr_primaire(self, p):
        return arbre_abstrait.Booleen(True)

    @_('FAUX')
    def expr_primaire(self, p):
        return arbre_abstrait.Booleen(False)

    @_('IDENTIFIANT')
    def expr_primaire(self, p):
        # Ne pas valider pendant le parsing, juste créer le nœud
        variable = arbre_abstrait.Variable(p.IDENTIFIANT)
        return variable

    @_('LIRE "(" ")"')
    def expr_primaire(self, p):
        return arbre_abstrait.Lire()

    @_('IDENTIFIANT "(" listeArgsOpt ")"')
    def expr_primaire(self, p):
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
        if self.validation_active:
            self.table_symboles.ajouter_variable(p.IDENTIFIANT, p.type, None)
        return arbre_abstrait.Declaration(p.type, p.IDENTIFIANT)

    @_('IDENTIFIANT "=" expr ";"')
    def instruction(self, p):
        # Ne pas valider pendant le parsing des fonctions
        return arbre_abstrait.Affectation(p.IDENTIFIANT, p.expr)

    @_('type IDENTIFIANT "=" expr ";"')
    def instruction(self, p):
        if self.validation_active:
            self.table_symboles.ajouter_variable(p.IDENTIFIANT, p.type, None)
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

    # Définition de fonction
    @_('type IDENTIFIANT "(" listeParamsOpt ")" bloc')
    def instruction(self, p):
        # Désactiver la validation pendant le parsing du corps de la fonction
        ancienne_validation = self.validation_active
        self.validation_active = False
        
        # Créer le nœud fonction
        fonction = arbre_abstrait.Fonction(p.type, p.IDENTIFIANT, p.listeParamsOpt, p.bloc)
        
        # Restaurer la validation
        self.validation_active = ancienne_validation
        
        # Ajouter la fonction à la table des symboles
        if self.validation_active:
            self.table_symboles.ajouter_fonction(p.IDENTIFIANT, p.type, p.listeParamsOpt)
        
        return fonction

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

def valider_semantique(arbre, table_symboles):
    """Validation sémantique après le parsing"""
    
    def valider_noeud(noeud, contexte_fonction=None):
        if isinstance(noeud, arbre_abstrait.Programme):
            for instruction in noeud.listeInstructions.instructions:
                if isinstance(instruction,arbre_abstrait.Fonction):
                    table_symboles.ajouter_fonction(instruction.nom, instruction.type, instruction.params)
            # Puis valider le reste
            for instruction in noeud.listeInstructions.instructions:
                if not isinstance(instruction, arbre_abstrait.Fonction):
                    valider_noeud(instruction)
                
        elif isinstance(noeud, arbre_abstrait.Fonction):
            # Créer un contexte temporaire pour la fonction
            contexte_local = {}
            for type_param, nom_param in noeud.params:
                contexte_local[nom_param] = type_param
            
            # Valider le corps avec ce contexte
            valider_noeud(noeud.corps, contexte_local)
            
        elif isinstance(noeud, arbre_abstrait.ListeInstructions):
            for instruction in noeud.instructions:
                valider_noeud(instruction, contexte_fonction)
                
        elif isinstance(noeud, arbre_abstrait.Variable):
            # Vérifier si la variable existe
            if contexte_fonction and noeud.nom in contexte_fonction:
                noeud.type = contexte_fonction[noeud.nom]
            else:
                var_info = table_symboles.get_variable(noeud.nom)
                if var_info is None:
                    raise Exception(f"Erreur : variable '{noeud.nom}' non déclarée.")
                noeud.type = var_info['type']
                noeud.adresse = var_info['adresse']
                
        elif isinstance(noeud, arbre_abstrait.Affectation):
            # Vérifier que la variable existe
            if contexte_fonction and noeud.nom in contexte_fonction:
                pass  # OK, c'est un paramètre
            else:
                var_info = table_symboles.get_variable(noeud.nom)
                if var_info is None:
                    raise Exception(f"Erreur : variable '{noeud.nom}' non déclarée.")
            valider_noeud(noeud.expr, contexte_fonction)
            
        # Continuer la validation récursivement pour les autres types de nœuds
        elif hasattr(noeud, '__dict__'):
            for attr_name, attr_value in noeud.__dict__.items():
                if isinstance(attr_value, (list, tuple)):
                    for item in attr_value:
                        if hasattr(item, 'afficher'):  # C'est probablement un nœud de l'AST
                            valider_noeud(item, contexte_fonction)
                elif hasattr(attr_value, 'afficher'):  # C'est probablement un nœud de l'AST
                    valider_noeud(attr_value, contexte_fonction)
    
    valider_noeud(arbre)

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
                if arbre:
                    # Faire la validation sémantique après le parsing
                    valider_semantique(arbre, parser.table_symboles)
                    arbre.afficher()
                else:
                    print("Erreur: Aucun arbre généré")
            except EOFError:
                exit(1)
            except Exception as e:
                print(f"Erreur lors du parsing: {e}", file=sys.stderr)
                exit(1)