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
    else:
        erreur("Génération type instruction non implémenté " + str(type(instruction)))

def gen_programme(programme):
    header = """.LC0:
    .ascii "%d\\000"
    .align 2
.LC1:
    .ascii "%d\\012\\000"
    .text
    .align 2
    .global main"""
    printifm(header)

    for instr in programme.listeInstructions.instructions:
        if isinstance(instr, arbre_abstrait.Fonction):
            table.ajouter_fonction(instr.nom, instr.type, instr.params)

    printifm('main:')
    arm_instruction("push", "{fp, lr}", "", "", "")
    arm_instruction("add", "fp", "sp", "#4", "")
    gen_listeInstructions(programme.listeInstructions)
    arm_instruction("mov", "r1", "#0", "", "")
    arm_instruction("pop", "{fp, pc}", "", "", "")

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
        gen_appel_fonction(expression)
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
        arm_instruction("ldr", "r0", "=.LC0")
        arm_instruction("sub", "sp", "sp", "#4")
        arm_instruction("movs", "r1", "sp")
        arm_instruction("bl", "scanf")
        arm_instruction("ldr", "r2", "[sp]")
        arm_instruction("add", "sp", "sp", "#4")
        arm_instruction("push", "{r2}")
    elif isinstance(expression, arbre_abstrait.OperationLogique):
        gen_operation_logique(expression)
    else:
        erreur("type d'expression inconnu : " + str(type(expression)))

def gen_operation(operation):
    op = operation.op
    gen_expression(operation.exp1)  # on calcule et empile la valeur de exp1
    gen_expression(operation.exp2)  # on calcule et empile la valeur de exp2
    arm_instruction("pop", "{r1}", "", "", "dépile exp2 dans r1")
    arm_instruction("pop", "{r0}", "", "", "dépile exp1 dans r0")
    
    code = {"+": "add", "*": "mul"}  # Un dictionnaire qui associe à chaque opérateur sa fonction arm
    if op in ['+', '*']:
        arm_instruction(code[op], "r1", "r0", "r1", "effectue l'opération r0 " + op + " r1 et met le résultat dans r0")
    else:
        erreur("opérateur \"" + op + "\" non implémenté")
    arm_instruction("push", "{r1}", "", "", "empile le résultat")

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

def gen_appel_fonction_instr(instr):
    f = table.get_fonction(instr.nom)
    if not f or len(f['params']) != len(instr.args):
        erreur(f"Appel incorrect à {instr.nom}")
    for arg in instr.args:
        gen_expression(arg)
    arm_instruction("bl", f"_{instr.nom}")

def gen_retour(instr):
    if fonction_courante is None:
        erreur("Instruction 'retourner' hors fonction")
    type_expr = gen_expression(instr.expr)  # à améliorer si nécessaire
    if type_expr != fonction_courante.type:
        erreur("Type de retour incompatible")
    arm_instruction("pop", "{r2}")
    arm_instruction("sub", "sp", "fp", "#4")
    arm_instruction("pop", "{fp, pc}")
