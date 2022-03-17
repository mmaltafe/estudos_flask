import json
import logging
from base64 import b64decode
from datetime import timedelta
from time import time
import secrets

from app.extensions import db
from app.models import User
from click import password_option
from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource, reqparse
from werkzeug.security import check_password_hash, generate_password_hash
from app.services.mail import send_mail


class Login(Resource):
    def get(self):
        if not request.headers.get("Authorization"):
            return {"error", "Login e Senha invalidos"}, 400

        basic, code = request.headers["Authorization"].split(" ")

        email, password = b64decode(code).decode().split(":")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return {"error", "Login e Senha invalidos"}, 400

        token = create_access_token({"id": user.id}, expires_delta=timedelta(hours=3))

        return {"acces_token": token}


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True, help="O campo email é obrigatorio")
        parser.add_argument(
            "password", required=True, help="O campo password é obrigatorio"
        )
        args = parser.parse_args()

        """SELECT id, email, password FROM USERS
        WHERE email == $args.email$
        LIMIT 1"""
        user = User.query.filter_by(email=args.email).first()

        if user:
            return {"error": "email já registrado!"}, 400

        password = generate_password_hash(args.password, salt_length=10)
        user = User(email=args.email, password=password)

        db.session.add(user)

        try:
            db.session.commit()
            send_mail(
                "Bem-Vindo",
                user.email,
                "welcome",
                email=user.email,
            )
            return {"message": "Usuario registrado com sucesso"}, 201
        except Exception as e:
            db.session.rollback()
            logging.critical(str(e))
            return {"error": "Não foi possivel executar o registro do usuario"}, 500


class ForgetPassword(Resource):
    def post(self):
        parser = reqparse.RequestParser(trim=True)
        parser.add_argument("email", required=True, help="O campo email é obrigatorio")
        args = parser.parse_args()

        user = User.query.filter_by(email=args.email).first()

        if not user:
            return {"error": "Usuario não encontrado"}, 400

        password_temp = secrets.token_hex(8)
        user.password = generate_password_hash(password_temp)

        db.session.add(user)
        db.session.commit()

        send_mail(
            "Recuperação de Conta",
            user.email,
            "forget-password",
            password_temp=password_temp,
        )
        return {"message": "Email enviado com sucesso"}
