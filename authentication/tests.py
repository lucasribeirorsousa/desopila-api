import tempfile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django_rest_passwordreset.models import ResetPasswordToken
from model_bakery import baker
from PIL import Image

from checkout.models import Credit, Gateway, GatewayUser

from .models import User

GATEWAY='pagarme'

class UserTests(APITestCase):
    def setUp(self) -> None:
        if not Gateway.objects.filter(name=GATEWAY).exists():
            self.gateway = baker.make('checkout.Gateway', name=GATEWAY, id=2)
        else:
            self.gateway = Gateway.objects.get(name=GATEWAY)
        return super().setUp()
    #create
    def test_create_user(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        asset = baker.make('asset.Asset', file_high=tmp_file)
        body = {
            "asset": asset.id,
            "address": {
                "map_string": "Rua das Carlotas, 123",
                "reference": "Em frente ao atacado varejo",
                "cep": "84268660",
                "latitude": -5.820903,
                "longitude": -35.188911
            },
            "cpf_cnpj": "12345678910",
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887777",
            "whatsapp": "84988887777",
            "first_name": "New",
            "last_name": "User",
            "password": "user",
        }

        url = reverse('authentication_urls:users-list')
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # User creation
        user = User.objects.get()
        self.assertEqual(user.asset.id, asset.id)
        self.assertEqual(user.cpf_cnpj, body['cpf_cnpj'])
        self.assertEqual(user.email, body['email'])
        self.assertEqual(user.username, body['username'])
        self.assertEqual(user.phone, body['phone'])
        self.assertEqual(user.whatsapp, body['whatsapp'])
        self.assertEqual(user.first_name, body['first_name'].upper())
        self.assertEqual(user.last_name, body['last_name'].upper())

        # Address creation
        self.assertEqual(user.address.map_string, body["address"]['map_string'])
        self.assertEqual(user.address.reference, body["address"]['reference'])
        self.assertEqual(user.address.cep, body["address"]['cep'])
        self.assertEqual(user.address.latitude, body["address"]['latitude'])
        self.assertEqual(user.address.longitude, body["address"]['longitude'])

        # GatewayUser creation
        gateway_user = GatewayUser.objects.get(user=user)
        self.assertEqual(gateway_user.user, user)
        self.assertNotEqual(gateway_user.user_on_gateway_id, '')

        # Credit creation
        credit = Credit.objects.filter(user=user)
        self.assertEqual(credit.exists(), True)
        self.assertEqual(credit[0].amount, 0)

    def test_dont_create_user_if_cpf_cnpj_is_already_used(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        baker.make('authentication.User', cpf_cnpj="12345678910")
        asset = baker.make('asset.Asset', file_high=tmp_file)
        body = {
            "asset": asset.id,
            "address": {
                "map_string": "Rua das Carlotas, 123",
                "reference": "Em frente ao atacado varejo",
                "cep": "84268660",
                "latitude": -5.820903,
                "longitude": -35.188911
            },
            "cpf_cnpj": "12345678910",
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887777",
            "whatsapp": "84988887777",
            "first_name": "New",
            "last_name": "User",
            "password": "user",
        }

        url = reverse('authentication_urls:users-list')
        response = self.client.post(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['cpf_cnpj'], 'CPF ou CNPJ já usado em outro cadastro.')

    def test_dont_create_user_if_username_is_already_used(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        baker.make('authentication.User', username="user")
        asset = baker.make('asset.Asset', file_high=tmp_file)
        body = {
            "asset": asset.id,
            "address": {
                "map_string": "Rua das Carlotas, 123",
                "reference": "Em frente ao atacado varejo",
                "cep": "84268660",
                "latitude": -5.820903,
                "longitude": -35.188911
            },
            "cpf_cnpj": "12345678910",
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887777",
            "whatsapp": "84988887777",
            "first_name": "New",
            "last_name": "User",
            "password": "user",
        }

        url = reverse('authentication_urls:users-list')
        response = self.client.post(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'],
                         'Username já usado em outro cadastro.')

    def test_dont_create_user_if_email_is_already_used(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        baker.make('authentication.User', email="user@hotmail.com")
        asset = baker.make('asset.Asset', file_high=tmp_file)
        body = {
            "asset": asset.id,
            "address": {
                "map_string": "Rua das Carlotas, 123",
                "reference": "Em frente ao atacado varejo",
                "cep": "84268660",
                "latitude": -5.820903,
                "longitude": -35.188911
            },
            "cpf_cnpj": "12345678910",
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887777",
            "whatsapp": "84988887777",
            "first_name": "New",
            "last_name": "User",
            "password": "user",
        }

        url = reverse('authentication_urls:users-list')
        response = self.client.post(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'],
                         'Email já usado em outro cadastro.')

    def test_dont_create_user_if_phone_number_is_already_used(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        baker.make('authentication.User', phone="84988887777")
        asset = baker.make('asset.Asset', file_high=tmp_file)
        body = {
            "asset": asset.id,
            "address": {
                "map_string": "Rua das Carlotas, 123",
                "reference": "Em frente ao atacado varejo",
                "cep": "84268660",
                "latitude": -5.820903,
                "longitude": -35.188911
            },
            "cpf_cnpj": "12345678910",
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887777",
            "whatsapp": "84988887777",
            "first_name": "New",
            "last_name": "User",
            "password": "user",
        }

        url = reverse('authentication_urls:users-list')
        response = self.client.post(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['phone'], 'Numero de telefone já usado em outro cadastro.')

    def test_dont_create_user_if_whatsapp_number_is_already_used(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        baker.make('authentication.User', whatsapp="84988887777")
        asset = baker.make('asset.Asset', file_high=tmp_file)
        body = {
            "asset": asset.id,
            "address": {
                "map_string": "Rua das Carlotas, 123",
                "reference": "Em frente ao atacado varejo",
                "cep": "84268660",
                "latitude": -5.820903,
                "longitude": -35.188911
            },
            "cpf_cnpj": "12345678910",
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887777",
            "whatsapp": "84988887777",
            "first_name": "New",
            "last_name": "User",
            "password": "user",
        }

        url = reverse('authentication_urls:users-list')
        response = self.client.post(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['whatsapp'],
                         'Numero de whatsapp já usado em outro cadastro.')
    
    #password recovery
    def test_recover_password(self):
        old_password = 'senhavelha'
        new_password = 'senhanova'
        email = 'desopila@desopila.app'

        url = reverse('reset-password:reset-password-request')
        baker.make(
            User,
            email=email,
            password=old_password,
            status=1,
        )

        body = {
            "email": email,
        }
        
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = ResetPasswordToken.objects.get().key
        
        url = reverse('reset-password:reset-password-confirm')
        body = {
            "token": token,
            "password": new_password,
        }

        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('login')
        body = {
            "email": email,
            "password": new_password,
        }
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dont_recover_password_if_token_is_wrong(self):
        old_password = 'senhavelha'
        new_password = 'senhanova'
        email = 'desopila@desopila.app'

        url = reverse('reset-password:reset-password-request')
        baker.make(
            User,
            email=email,
            password=old_password,
            status=1,
        )

        body = {
            "email": email,
        }
        
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = ResetPasswordToken.objects.get().key

        url = reverse('reset-password:reset-password-confirm')
        body = {
            "token": "cf46fb6ed635f7e3f8bd15f6c70651c717a2",
            "password": new_password,
        }

        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        url = reverse('login')
        body = {
            "email": email,
            "password": new_password,
        }
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dont_recover_password_if_there_is_no_user_with_the_email(self):
        old_password = 'senhavelha'
        email = 'desopila@desopila.app'

        url = reverse('reset-password:reset-password-request')
        baker.make(
            User,
            email=email,
            password=old_password,
            status=1,
        )

        body = {
            "email": "outro@email.com",
        }
        
        response = self.client.post(url, body, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ResetPasswordToken.objects.all().exists(),False)
    
    #update
    def test_parcial_update_user(self):
        user = baker.make('authentication.User')

        body = {
            "email": "user@hotmail.com",
            "username": "user",
            "phone": "84988887777",
            "whatsapp": "84988887777",
        }

        self.client.force_authenticate(user)
        url = f"{reverse('authentication_urls:users-list')}{user.id}/"

        response = self.client.patch(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get()
        self.assertEqual(user.email, body['email'])
        self.assertEqual(user.username, body['username'])
        self.assertEqual(user.phone, body['phone'])
        self.assertEqual(user.whatsapp, body['whatsapp'])

    def test_dont_parcial_update_user_if_the_field_is_prohibited(self):
        user = baker.make('authentication.User')

        body = {
            "cpf_cnpj": "12345678910",
            "email": "user@hotmail.com",
        }
        self.client.force_authenticate(user)
        url = f"{reverse('authentication_urls:users-list')}{user.id}/"

        response = self.client.patch(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.get()
        self.assertNotEqual(user.cpf_cnpj, body['cpf_cnpj'])
        self.assertEqual(user.email, body['email'])



class AuthenticationTests(APITestCase):
    def test_generate_token(self):
        user = baker.make('authentication.User', password="user")
        body = {
            "email": user.email,
            "password": "user"
        }
        
        url = reverse('login')
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('refresh' in response.data, True)
        self.assertEqual('access' in response.data, True)
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['username'], user.username)

    def test_dont_generate_token_if_user_not_exists(self):
        body = {
            "email": "user@hotmail.com",
            "password": "user"
        }
        
        url = reverse('login')
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        user = baker.make('authentication.User', password="user")

        body = {
            "email": user.email,
            "password": "user"
        }
        url = reverse('login')
        response = self.client.post(url, body, format='json')

        body2 = {
            'refresh': response.data['refresh']
        }

        url = reverse('refresh')
        response = self.client.post(url, body2, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('refresh' in response.data, True)
        self.assertEqual('access' in response.data, True)

    def test_dont_refresh_token_if_token_is_invalid(self):

        body2 = {
            'refresh': '1q24rasr2341'
        }

        url = reverse('refresh')
        response = self.client.post(url, body2, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

