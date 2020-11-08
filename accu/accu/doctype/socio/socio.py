# -*- coding: utf-8 -*-
# Copyright (c) 2020, ACCU Catalunya and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class Socio(Document):
    def getnombrecompleto(self):
        "Returns the person's full name"
        return self.nombre + ' ' + self.apellidos

    def validate_iban(self):
        '''
        Algorithm: https://en.wikipedia.org/wiki/International_Bank_Account_Number#Validating_the_IBAN
        '''
        def encode_char(c):
            # Position in the alphabet (A=1, B=2, ...) plus nine
	        return str(9 + ord(c) - 64)
            # remove whitespaces, upper case to get the right number from ord()
	    # iban = ''.join(self.iban.split(' ')).upper()
        iban = self.iban
	# Move country code and checksum from the start to the end
	flipped = iban[4:] + iban[:4]
	# Encode characters as numbers
	encoded = [encode_char(c) if ord(c) >= 65 and ord(c)
	                       <= 90 else c for c in flipped]

	try:
	    to_check = int(''.join(encoded))
	except ValueError:
	    frappe.throw(_('Error en el formato del IBAN'))

    if to_check % 97 != 1:
	    frappe.throw(_('Error en los dígitos de comprobación del IBAN'))

    def validate(self):
        # campos calculados
        self.nombrecompleto = self.getnombrecompleto()

        # comprobaciones de coherencia
        # datos del pagador

        # primero, si los campos nombre completo, tipo ID y numero ID del pagador están vacios, entonces copiamos todos esos datos del socio y lo damos por correcto,
        # asumiendo que el socio es tambien el pagador

        if self.nombre_pagador in (None, "") and self.numero_id_pagador in (None, ""):
            self.nombre_pagador = self.getnombrecompleto()
            self.numero_id_pagador = self.numero_id
            self.tipo_id_pagador = self.tipo_id

        # en este punto, y tras la comprobacion anterior, los campos de nombre completo y numero de ID del pagador deberian tener algun valor,
        # salvo que solamente uno de los dos estuviera rellenado, cosa que seria incorrecta y por tanto pasamos a cancelar el guardado y avisar al usuario

        if (self.nombre_pagador in (None, "") or self.numero_id_pagador in (None, ""):
            # los datos de pagador parecen parcialmente rellenados
            frappe.throw("Incoherencia en el DNI y el nombre del pagador.<br/>Si se introducen datos en uno de los dos campos, " + 
            "deben introducrse tambien en el otro.<br/>Si el socio y la persona que paga son la misma persona, se deben dejar los dos campos vacios. " +
            "El sistema copiará los datos del socio al pagador.", "Problema con los datos del pagador")
            # return False

        # IBAN
        if (self.medio_de_pago == "Domiciliación Bancaria"):
            # IBAN es obligatorio
            self.iban=''.joint(self.iban.split(' ')).upper()
            self.validate_iban

        else:
            # IBAN deberia estar en blanco
            if self self.iban not in (None, ""):
                frappe.throw("El campo IBAN solo debe tener datos cuando el medio de pago es domiciliación bancaria",
                             "IBAN residual o medio de pago incorrecto")
