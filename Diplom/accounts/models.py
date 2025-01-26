from django.db import models
import hashlib

class Users(models.Model):
    Username = models.CharField(max_length=10, unique=True)
    Email = models.CharField(max_length=100, unique=True)
    Password = models.CharField(max_length=128)

    @staticmethod
    def hash_value(value):
        # Хэшируем значение с использованием SHA-256
        return hashlib.sha256(value.encode()).hexdigest()

    def set_email(self, email):
        # Хэшируем email перед сохранением
        self.Email = self.hash_value(email)

    def set_password(self, password):
        # Хэшируем пароль перед сохранением
        self.Password = self.hash_value(password)

    def check_password(self, password):
        # Проверяем пароль
        return self.Password == self.hash_value(password)