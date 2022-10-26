from db import db

class User:
    def __init__(self, id_us, name_us, email_us, pwd_us, perfil_us):
        self.id_us = id_us
        self.name_us = name_us
        self.email_us = email_us
        self.pwd_us = pwd_us
        self.perfil_us = perfil_us

