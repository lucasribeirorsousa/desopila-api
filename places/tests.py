from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from model_bakery import baker

from PIL import Image
import tempfile

from places.models import PlaceAds, Plan, WeekDay


class PlaceAdsTests(APITestCase):
    def setUp(self):
        for i in range(7):
            baker.make('places.WeekDay', day=i)

    def test_create_place_ads(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')

        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        user = baker.make('authentication.User')
        asset = baker.make('asset.Asset', file_high=tmp_file)

        body = {
            "address": {
                "map_string": "Map Street String",
                "reference": "reference",
                "cep": "84268660",
                "latitude": 4532534254,
                "longitude": 5432543
            },
            "place_title": "Title",
            "place_description": "Description",
            "capacity": 50,
            "local_type": 1,
            "status": 1,
            "images": [asset.id],
            "plans": [
                {
                    "week_days": [0,1,2,3,4,5,6],
                    "plan_type": 1,
                    "name": "plan name",
                    "price": 50
                },
                {
                    "week_days": [0,6],
                    "plan_type": 2,
                    "name": "plan name",
                    "price": 90
                }
            ]
        }
        self.client.force_authenticate(user)
        url = reverse("places_urls:places-ads-list")
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
       
        place_ads = PlaceAds.objects.get()
        plans = Plan.objects.filter(place_ads=place_ads)
        
        #place_ads
        self.assertEqual(place_ads.place_title, body["place_title"])
        self.assertEqual(place_ads.place_description, body["place_description"])
        self.assertEqual(place_ads.capacity, body["capacity"])
        self.assertEqual(place_ads.local_type, body["local_type"])
        
        #address
        self.assertEqual(place_ads.address.map_string, body["address"]["map_string"])
        self.assertEqual(place_ads.address.reference, body["address"]["reference"])
        self.assertEqual(place_ads.address.cep, body["address"]["cep"])
        self.assertEqual(place_ads.address.latitude, body["address"]["latitude"])
        self.assertEqual(place_ads.address.longitude, body["address"]["longitude"])

        #plans
        plan1 = plans[0]
        plan2 = plans[1]
        self.assertEqual(plan1.plan_type, body["plans"][0]["plan_type"])
        self.assertEqual(plan1.name, body["plans"][0]["name"])
        self.assertEqual(plan1.price, body["plans"][0]["price"])

        #week_days
        self.assertEqual(len(plan1.week_days.all()), len(body['plans'][0]['week_days']))
        self.assertEqual(len(plan2.week_days.all()), len(body['plans'][1]['week_days']))

        for day in plan1.week_days.all():
            self.assertEqual(day.day in body['plans'][0]['week_days'], True)

        for day in plan2.week_days.all():
            self.assertEqual(day.day in body['plans'][1]['week_days'], True)

    def test_list_place_ads(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')

        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        asset = baker.prepare('asset.Asset', file_high=tmp_file, _quantity=2)
        user = baker.make('authentication.User')
        address = baker.make('places.Address')
        place_ads = baker.make('places.PlaceAds', user=user, address=address, images=asset)
        plan = baker.make('places.Plan' ,place_ads=place_ads ,week_days=WeekDay.objects.all())

        self.client.force_authenticate(user)
        url = f'{reverse("places_urls:places-ads-list")}{place_ads.id}/'
        response = self.client.get(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        #place_ads
        self.assertEqual(place_ads.place_title, response.data["place_title"])
        self.assertEqual(place_ads.place_description, response.data["place_description"])
        self.assertEqual(place_ads.capacity, response.data["capacity"])
        self.assertEqual(place_ads.local_type, response.data["local_type"])
        
        #address
        self.assertEqual(place_ads.address.map_string, response.data["address"]["map_string"])
        self.assertEqual(place_ads.address.reference, response.data["address"]["reference"])
        self.assertEqual(place_ads.address.cep, response.data["address"]["cep"])
        self.assertEqual(place_ads.address.latitude, response.data["address"]["latitude"])
        self.assertEqual(place_ads.address.longitude, response.data["address"]["longitude"])

        #plans
        self.assertEqual(plan.plan_type, response.data["plans"][0]["plan_type"])
        self.assertEqual(plan.name, response.data["plans"][0]["name"])
        self.assertEqual(plan.price, response.data["plans"][0]["price"])

        #week_days
        self.assertEqual(len(plan.week_days.all()), 7)

        for day in plan.week_days.all():
            self.assertEqual(day.id in response.data['plans'][0]['week_days'], True)

    def test_update_place_ads(self):
        image = Image.new(mode='RGB', size=(200, 20), color='blue')

        tmp_file = tempfile.NamedTemporaryFile(suffix='.png')
        image.save(tmp_file)
        tmp_file.seek(0)

        asset = baker.prepare('asset.Asset', file_high=tmp_file, _quantity=2)
        user = baker.make('authentication.User')
        address = baker.make('places.Address')
        place_ads = baker.make('places.PlaceAds', user=user, address=address, images=asset)
        plan1 = baker.make('places.Plan', place_ads=place_ads, week_days=WeekDay.objects.all())
        plan2 = baker.make('places.Plan', place_ads=place_ads, week_days=WeekDay.objects.all())

        body= {
            "address": {
                "id": address.id,
                "map_string": "Map Street String",
                "reference": "reference",
                "cep": "84268660",
                "latitude": 4532534254,
                "longitude": 5432543
            },
            "place_title": "Title",
            "place_description": "Description",
            "capacity": 50,
            "local_type": 1,
            "images": [
                asset[0].id, asset[1].id
            ],
            "plans": [
                {
                    "id": plan1.id,
                    "week_days": [
                        0,1,2,3,4,5,6
                    ],
                    "plan_type": 1,
                    "name": "plan name",
                    "price": 50
                },
                {
                    "week_days": [
                        0,1,2,3,4,5,6
                    ],
                    "plan_type": 1,
                    "name": "New plan name",
                    "price": 50
                }
            ]
        }

        self.client.force_authenticate(user)
        url = f'{reverse("places_urls:places-ads-list")}{place_ads.id}/'
        response = self.client.put(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        #place_ads
        place_ads = PlaceAds.objects.get(id=place_ads.id)
        self.assertEqual(place_ads.place_title, body["place_title"])
        self.assertEqual(place_ads.place_description, body["place_description"])
        self.assertEqual(place_ads.capacity, body["capacity"])
        self.assertEqual(place_ads.local_type, body["local_type"])
        
        #address
        self.assertEqual(place_ads.address.map_string, body["address"]["map_string"])
        self.assertEqual(place_ads.address.reference, body["address"]["reference"])
        self.assertEqual(place_ads.address.cep, body["address"]["cep"])
        self.assertEqual(place_ads.address.latitude, body["address"]["latitude"])
        self.assertEqual(place_ads.address.longitude, body["address"]["longitude"])
        
        #plans
        #O plano que existia antes mas não está presente na requisição foi deletado?
        self.assertEqual(Plan.objects.filter(id=plan2.id).exists(), False)

        #O plano que existia antes e está na requisição foi atualizado?
        plan1 = Plan.objects.get(id=plan1.id)
        self.assertEqual(plan1.plan_type, body["plans"][0]["plan_type"])
        self.assertEqual(plan1.name, body["plans"][0]["name"])
        self.assertEqual(plan1.price, body["plans"][0]["price"])

        for day in plan1.week_days.all():            
            self.assertEqual(day.day in body['plans'][0]['week_days'], True)

        #O plano que não existia antes e está na requisição foi criado?
        plan3 = Plan.objects.get(name=body['plans'][1]['name'])
        self.assertEqual(plan3.plan_type, body["plans"][1]["plan_type"])
        self.assertEqual(plan3.name, body["plans"][1]["name"])
        self.assertEqual(plan3.price, body["plans"][1]["price"])

        for day in plan3.week_days.all():
            self.assertEqual(day.day in body['plans'][1]['week_days'], True)

