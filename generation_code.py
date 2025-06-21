import sys
from analyse_lexicale import FloLexer
from analyse_syntaxique import FloParser
import arbre_abstrait
from table_symboles import TableSymboles

table = TableSymboles()
fonction_courante = None
num_etiquette_courante = -1 
afficher_table = False
afficher_code = False

def erreur(s):
    print("Erreur:", s, file=sys.stderr)
    exit(1)

def printifm(*args, **kwargs):
    if afficher_code:
        print(*args, **kwargs)

def printift(*args, **kwargs):
    if afficher_table:
        print(*args, **kwargs)

def arm_comment(comment):
    if comment != "":
        printifm("\t\t @ " + comment)  # le point virgule indique le début d'un commentaire en ARM
    else:
        printifm("")  

def arm_instruction(opcode, op1="", op2="", op3="", comment=""):
    if op2 == "":
        printifm("\t" + opcode + "\t" + op1 + "\t\t", end="")
    elif op3 == "":
        printifm("\t" + opcode + "\t" + op1 + ",\t" + op2 + "\t", end="")
    else:
        printifm("\t" + opcode + "\t" + op1 + ",\t" + op2 + ",\t" + op3, end="")
    arm_comment(comment)

def gen_instruction(instruction):
    if isinstance(instruction, arbre_abstrait.Ecrire):
        gen_ecrire(instruction)
    elif isinstance(instruction, arbre_abstrait.Fonction):
        gen_def_fonction(instruction)
    elif isinstance(instruction, arbre_abstrait.AppelFonctionInstr):
        gen_appel_fonction_instr(instruction)
    elif isinstance(instruction, arbre_abstrait.Retour):
        gen_retour(instruction)
    elif isinstance(instruction, arbre_abstrait.Conditionnelle):
        gen_conditionnelle(instruction)
    elif isinstance(instruction, arbre_abstrait.Boucle):
        gen_boucle(instruction)
    elif isinstance(instruction, arbre_abstrait.Declaration):
        gen_declaration(instruction)
    elif isinstance(instruction, arbre_abstrait.DeclarationAffectation):
        gen_declaration_affectation(instruction)
    elif isinstance(instruction, arbre_abstrait.Affectation):
        gen_affectation(instruction)
    else:
        erreur("Génération type instruction non implémenté " + str(type(instruction)))


def gen_declaration_affectation(decl):
    # Calculer l'adresse
    adresse = -4 * (len(table.variables) + 1)
    table.ajouter_variable(decl.nom, decl.type, adresse)
    # Générer l'expression et stocker dans la variable
    gen_expression(decl.expr)
    arm_instruction("pop", "{r0}", "", "", f"valeur pour {decl.nom}")
    arm_instruction("str", "r0", f"[fp, #{adresse}]", "", f"stocke dans {decl.nom}")

def gen_affectation(aff):
    var_info = table.get_variable(aff.nom)
    if var_info is None:
        erreur(f"Variable {aff.nom} non déclarée")
    gen_expression(aff.expr)
    arm_instruction("pop", "{r0}", "", "", f"valeur pour {aff.nom}")
    arm_instruction("str", "r0", f"[fp, #{var_info['adresse']}]", "", f"affecte {aff.nom}")

def gen_declaration(decl):
    # Calculer l'adresse en fonction de la profondeur
    adresse = -4 * (len(table.variables) + 1)
    table.ajouter_variable(decl.nom, decl.type, adresse)
    # Réserver l'espace sur la pile
    arm_instruction("sub", "sp", "sp", "#4", f"réserve espace pour {decl.nom}")

    
def gen_programme(programme):
    # Header
    header = """.LC0:
    .ascii "%d\\000"
    .align 2
.LC1:
    .ascii "%d\\012\\000"
    .text
    .align 2
    .global main
    .global __aeabi_idiv       
    .global __aeabi_idivmod"""
    printifm(header)

    # Ajouter toutes les fonctions à la table des symboles
    for instr in programme.listeInstructions.instructions:
        if isinstance(instr, arbre_abstrait.Fonction):
            table.ajouter_fonction(instr.nom, instr.type, instr.params)

    # Traiter le code global comme une fonction main
    printifm('main:')
    arm_instruction("push", "{fp, lr}")
    arm_instruction("add", "fp", "sp", "#4")
    
    # Générer les instructions globales
    for instr in programme.listeInstructions.instructions:
        if not isinstance(instr, arbre_abstrait.Fonction):
            gen_instruction(instr)
    
    arm_instruction("mov", "r0", "#0")  # Code de retour 0
    arm_instruction("pop", "{fp, pc}")

    # Générer le code des fonctions
    for instr in programme.listeInstructions.instructions:
        if isinstance(instr, arbre_abstrait.Fonction):
            gen_def_fonction(instr)


def arm_nouvelle_etiquette():
    global num_etiquette_courante
    num_etiquette_courante += 1
    return "e" + str(num_etiquette_courante)

def gen_listeInstructions(listeInstructions):
    for instruction in listeInstructions.instructions:
        gen_instruction(instruction)

def gen_conditionnelle(cond):
    etiquette_sinon = arm_nouvelle_etiquette()
    etiquette_fin = arm_nouvelle_etiquette()

    gen_expression(cond.condition)
    arm_instruction("pop", "{r0}", "", "", "condition -> r0")
    arm_instruction("cmp", "r0", "#0", "", "si 0, alors faux")
    arm_instruction("beq", etiquette_sinon, "", "", "aller à sinon si condition fausse")

    gen_listeInstructions(cond.bloc_si)
    arm_instruction("b", etiquette_fin, "", "", "saut fin if")
    printifm(f"{etiquette_sinon}:")
    
    if cond.bloc_sinon:
        gen_listeInstructions(cond.bloc_sinon)

    printifm(f"{etiquette_fin}:")

def gen_boucle(boucle):
    etiquette_debut = arm_nouvelle_etiquette()
    etiquette_fin = arm_nouvelle_etiquette()

    printifm(f"{etiquette_debut}:")
    gen_expression(boucle.condition)
    arm_instruction("pop", "{r0}", "", "", "évalue condition")
    arm_instruction("cmp", "r0", "#0", "", "compare avec 0")
    arm_instruction("beq", etiquette_fin, "", "", "saut si faux")

    gen_listeInstructions(boucle.bloc)
    arm_instruction("b", etiquette_debut, "", "", "retour au début de la boucle")
    printifm(f"{etiquette_fin}:")

def gen_ecrire(ecrire):
    gen_expression(ecrire.exp)  # on calcule et empile la valeur d'expression
    arm_instruction("pop", "{r1}", "", "", "")  # on dépile la valeur d'expression sur r1
    arm_instruction("ldr", "r0", "=.LC1", "", "")
    arm_instruction("bl", "printf", "", "", "")  # on envoie la valeur de r1 sur la sortie standard
def gen_operation_logique(operation):
    """Génère le code pour les opérations logiques (et, ou, non)"""
    op = operation.op
    
    if op == 'non':
        # Opération unaire NON
        gen_expression(operation.exp1)
        arm_instruction("pop", "{r0}", "", "", "dépile l'opérande")
        arm_instruction("cmp", "r0", "#0", "", "compare avec 0")
        arm_instruction("moveq", "r0", "#1", "", "si 0 alors 1")
        arm_instruction("movne", "r0", "#0", "", "si non 0 alors 0")
        arm_instruction("push", "{r0}", "", "", "empile le résultat")
        
    elif op == 'et':
        # Opération binaire ET - évaluation paresseuse
        etiquette_faux = arm_nouvelle_etiquette()
        etiquette_fin = arm_nouvelle_etiquette()
        
        gen_expression(operation.exp1)
        arm_instruction("pop", "{r0}", "", "", "première expression")
        arm_instruction("cmp", "r0", "#0", "", "si première expression fausse")
        arm_instruction("beq", etiquette_faux, "", "", "alors résultat est faux")
        
        gen_expression(operation.exp2)
        arm_instruction("pop", "{r0}", "", "", "deuxième expression")
        arm_instruction("cmp", "r0", "#0", "", "évalue deuxième expression")
        arm_instruction("moveq", "r0", "#0", "", "si faux alors 0")
        arm_instruction("movne", "r0", "#1", "", "si vrai alors 1")
        arm_instruction("b", etiquette_fin, "", "", "aller à la fin")
        
        printifm(f"{etiquette_faux}:")
        arm_instruction("mov", "r0", "#0", "", "résultat faux")
        
        printifm(f"{etiquette_fin}:")
        arm_instruction("push", "{r0}", "", "", "empile le résultat")
        
    elif op == 'ou':
        # Opération binaire OU - évaluation paresseuse
        etiquette_vrai = arm_nouvelle_etiquette()
        etiquette_fin = arm_nouvelle_etiquette()
        
        gen_expression(operation.exp1)
        arm_instruction("pop", "{r0}", "", "", "première expression")
        arm_instruction("cmp", "r0", "#0", "", "si première expression vraie")
        arm_instruction("bne", etiquette_vrai, "", "", "alors résultat est vrai")
        
        gen_expression(operation.exp2)
        arm_instruction("pop", "{r0}", "", "", "deuxième expression")
        arm_instruction("cmp", "r0", "#0", "", "évalue deuxième expression")
        arm_instruction("moveq", "r0", "#0", "", "si faux alors 0")
        arm_instruction("movne", "r0", "#1", "", "si vrai alors 1")
        arm_instruction("b", etiquette_fin, "", "", "aller à la fin")
        
        printifm(f"{etiquette_vrai}:")
        arm_instruction("mov", "r0", "#1", "", "résultat vrai")
        
        printifm(f"{etiquette_fin}:")
        arm_instruction("push", "{r0}", "", "", "empile le résultat")
    
    else:
        erreur(f"Opération logique non supportée : {op}")

def gen_expression(expression):
    if isinstance(expression, arbre_abstrait.Operation):
        gen_operation(expression)
    elif isinstance(expression, arbre_abstrait.Entier):
        arm_instruction("mov", "r1", f"#{expression.valeur}")
        arm_instruction("push", "{r1}")
    elif isinstance(expression, arbre_abstrait.Comparaison):
        gen_expression(expression.exp1)
        gen_expression(expression.exp2)
        arm_instruction("pop", "{r1}")
        arm_instruction("pop", "{r0}")
        arm_instruction("cmp", "r0", "r1")
        etiquette_vrai = arm_nouvelle_etiquette()
        etiquette_fin = arm_nouvelle_etiquette()
        saut = {
            "==": "beq",
            "!=": "bne",
            "<": "blt",
            "<=": "ble",
            ">": "bgt",
            ">=": "bge"
        }.get(expression.op)

        if saut is None:
            erreur("opérateur de comparaison non supporté : " + expression.op)

        arm_instruction(saut, etiquette_vrai)
        arm_instruction("mov", "r1", "#0")
        arm_instruction("b", etiquette_fin)
        printifm(f"{etiquette_vrai}:")
        arm_instruction("mov", "r1", "#1")
        printifm(f"{etiquette_fin}:")
        arm_instruction("push", "{r1}")
    elif isinstance(expression, arbre_abstrait.AppelFonctionExpr):
        gen_appel_fonction_expr(expression)
    elif isinstance(expression, arbre_abstrait.Variable):
        var = table.get_variable(expression.nom)
        if var is None:
            var = table.get_variable_param(expression.nom, fonction_courante.nom)
        if var is None:
            erreur(f"Variable {expression.nom} non déclarée")
        arm_instruction("ldr", "r2", f"[fp, #{var['adresse']}]")
        arm_instruction("push", "{r2}")
    elif isinstance(expression, arbre_abstrait.Booleen):
        val = "#1" if expression.valeur else "#0"
        arm_instruction("mov", "r1", val)
        arm_instruction("push", "{r1}")
    elif isinstance(expression, arbre_abstrait.Lire):
        arm_instruction("ldr", "r0", "=.LC0", "", "charge l'adresse de la chaîne de format")
        arm_instruction("sub", "sp", "sp", "#4", "réserve espace sur la pile")
        arm_instruction("movs", "r1", "sp", "", "copie l'adresse dans r1")
        arm_instruction("bl", "scanf", "", "appel scanf")
        arm_instruction("ldr", "r2", "[sp]", "", "charge la valeur lue")
        arm_instruction("add", "sp", "sp", "#4", "libère l'espace temporaire")
        arm_instruction("push", "{r2}", "", "empile la valeur lue")
    elif isinstance(expression, arbre_abstrait.OperationLogique):
        gen_operation_logique(expression)
    else:
        erreur("type d'expression inconnu : " + str(type(expression)))
#mine
def gen_operation(operation):
    op = operation.op
    print(f"[DEBUG] Operation {op} avec exp1={operation.exp1}, exp2={operation.exp2}")

    # Check for unary minus specifically
    if op == '-' and operation.exp2 is None: # This signifies a unary minus
        if operation.exp1 is None:
            erreur(f"Opérande manquante dans l'opération unitaire {op}")
        gen_expression(operation.exp1) # Generate code for the single operand
        arm_instruction("pop", "{r0}", "", "", "dépile l'opérande dans r0")
        arm_instruction("RSB", "r0", "r0", "#0", "r0 = -r0 (négation)")
        arm_instruction("push", "{r0}", "", "", "empile le résultat de la négation")
        return # Important: exit the function after handling unary minus

    if operation.exp1 is None or operation.exp2 is None:
        erreur(f"Opérande manquante dans l'opération binaire {op}")

    gen_expression(operation.exp1)
    gen_expression(operation.exp2)

    arm_instruction("pop", "{r1}", "", "", "dépile exp2 dans r1")
    arm_instruction("pop", "{r0}", "", "", "dépile exp1 dans r0")

    if op == '+':
        arm_instruction("ADDS", "r0", "r0", "r1", "r0 = r0 + r1 (addition)")
    elif op == '-':
        arm_instruction("SUBS", "r0", "r0", "r1", "r0 = r0 - r1 (soustraction)")
    elif op == '*':
        arm_instruction("MUL", "r0", "r0", "r1", "r0 = r0 * r1 (multiplication)")
    elif op == '/':
        gen_division_entière_signée()
    elif op == '%':
        gen_modulo_entier_signé()
       

    arm_instruction("push", "{r0}", "", "", "empile le résultat")

def gen_division_entière_signée():

    arm_instruction("push {r2, r3}")
    
    arm_instruction("mov r2, r0")  # r2 = dividende
    arm_instruction("mov r3, r1")  # r3 = diviseur
    
    arm_instruction("mov r4, #0")  # r4 = 0 : positif
    
    arm_instruction("cmp r2, #0")
    arm_instruction("bge .Ldiv_abs_dividende")  # si >=0, pas de changement
    arm_instruction("rsb r2, r2, #0")            # r2 = -r2 (valeur absolue)
    arm_instruction("eor r4, r4, #1")            # inverser signe résultat
    
    arm_instruction(".Ldiv_abs_dividende:")
    
    # Gérer le signe du diviseur (r3)
    arm_instruction("cmp r3, #0")
    arm_instruction("bge .Ldiv_abs_diviseur")
    arm_instruction("rsb r3, r3, #0")            # r3 = -r3 (valeur absolue)
    arm_instruction("eor r4, r4, #1")            # inverser signe résultat
    
    arm_instruction(".Ldiv_abs_diviseur:")
    
    # Initialiser quotient en r0 à 0
    arm_instruction("mov r0, #0")
    
    # Boucle de soustraction: tant que r2 >= r3
    arm_instruction(".Ldiv_loop:")
    arm_instruction("cmp r2, r3")
    arm_instruction("blt .Ldiv_end")              # si r2 < r3, sortir
    
    arm_instruction("sub r2, r2, r3")             # r2 = r2 - r3
    arm_instruction("add r0, r0, #1")             # quotient++
    
    arm_instruction("b .Ldiv_loop")
    
    arm_instruction(".Ldiv_end:")
    
    # Appliquer le signe au quotient dans r0
    arm_instruction("cmp r4, #0")
    arm_instruction("beq .Ldiv_done")              # si signe positif, fini
    
    arm_instruction("rsb r0, r0, #0")              # r0 = -r0 (quotient négatif)
    
    arm_instruction(".Ldiv_done:")
    
    # Restaurer r2 et r3
    arm_instruction("pop {r2, r3}")

def gen_modulo_entier_signé():
    # r0 = dividende, r1 = diviseur
    # Résultat : reste (modulo) dans r0
    
    # Sauvegarder r2 et r3 (utilisés pour calculs)
    arm_instruction("push {r2, r3}")
    
    # Copier r0 et r1 dans r2 et r3 pour travail sur valeurs absolues
    arm_instruction("mov r2, r0")  # r2 = dividende
    arm_instruction("mov r3, r1")  # r3 = diviseur
    
    # Initialiser registre pour signe du dividende (r4)
    arm_instruction("mov r4, #0")  # r4 = 0 : positif
    
    # Gérer le signe du dividende (r2)
    arm_instruction("cmp r2, #0")
    arm_instruction("bge .Lmod_abs_dividende")  # si >=0, pas de changement
    arm_instruction("rsb r2, r2, #0")            # r2 = -r2 (valeur absolue)
    arm_instruction("mov r4, #1")                 # mémoriser que dividende négatif
    
    arm_instruction(".Lmod_abs_dividende:")
    
    # Gérer le signe du diviseur (r3)
    arm_instruction("cmp r3, #0")
    arm_instruction("bge .Lmod_abs_diviseur")
    arm_instruction("rsb r3, r3, #0")            # r3 = -r3 (valeur absolue)
    
    arm_instruction(".Lmod_abs_diviseur:")
    
    # Boucle de soustraction: tant que r2 >= r3
    arm_instruction(".Lmod_loop:")
    arm_instruction("cmp r2, r3")
    arm_instruction("blt .Lmod_end")              # si r2 < r3, sortir
    
    arm_instruction("sub r2, r2, r3")             # r2 = r2 - r3
    
    arm_instruction("b .Lmod_loop")
    
    arm_instruction(".Lmod_end:")
    
    # r2 contient le reste (positif)
    # Si dividende original était négatif, on remet le signe
    arm_instruction("cmp r4, #0")
    arm_instruction("beq .Lmod_done")
    
    arm_instruction("rsb r2, r2, #0")             # r2 = -r2
    
    arm_instruction(".Lmod_done:")
    
    # Mettre reste dans r0 (valeur de retour)
    arm_instruction("mov r0, r2")
    
    # Restaurer r2 et r3
    arm_instruction("pop {r2, r3}")




def gen_appel_fonction_instr(instr):
    f = table.get_fonction(instr.nom)
    if not f or len(f['params']) != len(instr.args):
        erreur(f"Appel incorrect à {instr.nom}")
    for arg in instr.args:
        gen_expression(arg)
    arm_instruction("bl", f"_{instr.nom}")



if __name__ == "__main__":
    afficher_arm = True
    lexer = FloLexer()
    parser = FloParser()
    
    if len(sys.argv) < 3 or sys.argv[1] not in ["-arm", "-table"]:
        print("usage: python3 generation_code.py -arm|-table NOM_FICHIER_SOURCE.flo")
        exit(1)

    if sys.argv[1] == "-arm":
        afficher_code = True
    else:
        afficher_table = True

    with open(sys.argv[2], "r") as f:
        data = f.read()
        try:
            arbre = parser.parse(lexer.tokenize(data))
            gen_programme(arbre)
        except EOFError:
            exit(1)

def gen_def_fonction(f):
    global fonction_courante
    fonction_courante = f
    printifm(f"_{f.nom}:")
    arm_instruction("push", "{fp, lr}")
    arm_instruction("add", "fp", "sp", "#4")
    table.entrer_bloc()

    for type_, nom in f.params:
        adresse = table.get_fonction(f.nom)['adresse_args'][nom]
        table.ajouter_variable(nom, type_, adresse)

    gen_listeInstructions(f.corps)
    arm_instruction("sub", "sp", "fp", "#4")
    arm_instruction("pop", "{fp, pc}")

def gen_appel_fonction(appel):
    f = table.get_fonction(appel.nom)
    if not f:
        erreur(f"Fonction {appel.nom} non définie")
    if len(f['params']) != len(appel.args):
        erreur(f"Nombre d’arguments incorrect pour {appel.nom}")
    for arg in appel.args:
        gen_expression(arg)
    arm_instruction("bl", f"_{appel.nom}")
    arm_instruction("push", "{r2}")




def gen_appel_fonction_expr(appel):
    gen_appel_fonction(appel)



def gen_retour(instr):
    if fonction_courante is None:
        erreur("Instruction 'retourner' hors fonction")
    type_expr = gen_expression(instr.expr)  # à améliorer si nécessaire
    if type_expr != fonction_courante.type:
        erreur("Type de retour incompatible")
    arm_instruction("pop", "{r2}")
    arm_instruction("sub", "sp", "fp", "#4")
    arm_instruction("pop", "{fp, pc}")
