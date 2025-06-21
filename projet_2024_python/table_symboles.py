class TableSymboles:
    def __init__(self):
        self.fonctions = {}  
        self.variables = []  
        self.profondeur = 0

    def ajouter_fonction(self, nom, type_retour, params):
        if nom in self.fonctions:
            raise Exception(f"Fonction '{nom}' déjà définie")
        mem_args = len(params) * 4
        adresse_args = {}
        for i, (_, nom_param) in enumerate(params):
            adresse_args[nom_param] = 4 * (len(params) - i)
        self.fonctions[nom] = {
            'type': type_retour,
            'params': params,
            'mem_args': mem_args,
            'adresse_args': adresse_args
        }

    def get_fonction(self, nom):
        return self.fonctions.get(nom)

    def entrer_bloc(self):
        self.profondeur += 1

    def sortir_bloc(self):
        self.variables = [v for v in self.variables if v[3] < self.profondeur]
        self.profondeur -= 1

    def ajouter_variable(self, nom, type_, adresse):
        for v in self.variables:
            if v[0] == nom and v[3] == self.profondeur:
                raise Exception(f"Variable '{nom}' déjà déclarée dans ce bloc")
        self.variables.append((nom, type_, adresse, self.profondeur))

    def get_variable(self, nom):
        for v in reversed(self.variables):
            if v[0] == nom:
                return {'type': v[1], 'adresse': v[2]}
        return None

    def get_variable_param(self, nom, nom_fonction):
        f = self.get_fonction(nom_fonction)
        if f and nom in f['adresse_args']:
            index = [p[1] for p in f['params']].index(nom)
            return {
                'type': f['params'][index][0],
                'adresse': f['adresse_args'][nom]
            }
        return None
