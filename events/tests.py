import time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from model_bakery import baker
from datetime import datetime

from events.models import Cancellation, EventOrder
from places.models import WeekDay


class EventOrderTests(APITestCase):
    def setUp(self):
        for i in range(7):
            baker.make('places.WeekDay', day=i)

        self.owner_user = baker.make('authentication.User')
        self.orderer_user = baker.make('authentication.User')
        self.place_ads = baker.make('places.PlaceAds', user=self.owner_user)
        self.plan = baker.make(
            'places.Plan',
            plan_type=1,
            place_ads=self.place_ads,
            week_days=WeekDay.objects.filter().exclude(day=5).exclude(day=6),   #Segunda a sexta
            price=200,
            )

        date1 = "09/12/2021 10:40:00"   #QUINTA 
        date2 = "10/12/2021 04:50:00"   #SEXTA
        date3 = "11/12/2021 04:50:00"   #SABADO
        date4 = "12/12/2021 04:50:00"   #DOMINGO
        self.datetime1 = datetime.strptime(date1, "%d/%m/%Y %H:%M:%S")
        self.datetime2 = datetime.strptime(date2, "%d/%m/%Y %H:%M:%S")
        self.datetime3 = datetime.strptime(date3, "%d/%m/%Y %H:%M:%S")
        self.datetime4 = datetime.strptime(date4, "%d/%m/%Y %H:%M:%S")
        self.timestamp1 = time.mktime(self.datetime1.timetuple())
        self.timestamp2 = time.mktime(self.datetime2.timetuple())
        self.timestamp3 = time.mktime(self.datetime3.timetuple())
        self.timestamp4 = time.mktime(self.datetime4.timetuple())


    def create_event_order(self):
        self.body = {
            "place_ads": self.place_ads.id,
            "dates_selected": [self.timestamp1, self.timestamp2],
            "title": "Título de anúncio",
            "description": "Descrição de anúncio",
            "plan": self.plan.id
        }
        self.client.force_authenticate(self.orderer_user)
        url = reverse("events_urls:event-orders-list")
        
        return self.client.post(url, self.body, format='json')


    #Create
    def test_create_event_order(self):
        response = self.create_event_order()
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        #event_order
        event_order = EventOrder.objects.get()
        self.assertEqual(event_order.user, self.orderer_user)
        self.assertEqual(event_order.place_ads, self.place_ads)
        self.assertEqual(event_order.title, self.body['title'])
        self.assertEqual(event_order.description, self.body['description'])
        self.assertEqual(event_order.status, 1)
        self.assertEqual(event_order.plan_type, self.plan.plan_type)

        #dates_selected
        dates_selected=[]
        for date in self.body['dates_selected']:
            dates_selected.append(datetime.fromtimestamp(date))
        self.assertEqual(event_order.dates_selected, dates_selected)

        #price
        price = self.plan.price * len(self.body['dates_selected'])
        self.assertEqual(event_order.price, price)

    def test_dont_create_event_order_and_show_errors(self):
        body = {
            "place_ads": self.place_ads.id,
            "dates_selected": [self.timestamp1, self.timestamp2],
            "title": "Título de anúncio",
            "description": "Descrição de anúncio"
        }
        self.client.force_authenticate(self.orderer_user)
        url = reverse("events_urls:event-orders-list")
        
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_dont_create_event_order_if_orderer_and_owner_are_the_same(self):
        self.body = {
            "place_ads": self.place_ads.id,
            "dates_selected": [self.timestamp1, self.timestamp2],
            "title": "Título de anúncio",
            "description": "Descrição de anúncio",
            "plan": self.plan.id,
        }
        self.client.force_authenticate(self.owner_user)
        url = reverse("events_urls:event-orders-list")
        
        response = self.client.post(url, self.body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dont_create_event_order_if_dates_arent_in_the_daily_plan(self):
        self.body = {
            "place_ads": self.place_ads.id,
            "dates_selected": [self.timestamp2, self.timestamp3],
            "title": "Título de anúncio",
            "description": "Descrição de anúncio",
            "plan": self.plan.id,
        }
        self.client.force_authenticate(self.orderer_user)
        url = reverse("events_urls:event-orders-list")
        
        response = self.client.post(url, self.body, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_create_event_order_if_dates_arent_the_same_of_package_plan(self):
        plan_package = baker.make(
            'places.Plan',
            plan_type=2,
            place_ads=self.place_ads,
            week_days=WeekDay.objects.filter().exclude(day=0).exclude(day=1).exclude(day=2).exclude(day=3).exclude(day=4),
            price=200,
            )
        
        self.body = {
            "place_ads": self.place_ads.id,
            "dates_selected": [self.timestamp2, self.timestamp3],
            "title": "Título de anúncio",
            "description": "Descrição de anúncio",
            "plan": plan_package.id,
        }
        self.client.force_authenticate(self.orderer_user)
        url = reverse("events_urls:event-orders-list")
        
        response = self.client.post(url, self.body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    #List
    def test_list_event_order(self):
        self.create_event_order()

        self.client.force_authenticate(self.orderer_user)
        url = reverse("events_urls:event-orders-list")
        response = self.client.get(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data['results'][0]
        event_order = EventOrder.objects.get()
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(data['id'], event_order.id)
        self.assertEqual(data['user'], event_order.user.id)
        self.assertEqual(data['place_ads']['id'], event_order.place_ads.id)
        self.assertEqual(data['title'], event_order.title)
        self.assertEqual(data['description'], event_order.description)
        self.assertEqual(float(data['price']), event_order.price)
        self.assertEqual(data['status'], event_order.status)
        self.assertEqual(data['plan_type'], event_order.plan_type)

        dates_selected=[]
        for date in data['dates_selected']:
            dates_selected.append(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S"))
        self.assertEqual(event_order.dates_selected, dates_selected)

    def test_list_just_user_owner_or_orderer_event_order(self):
        self.create_event_order()

        #Owner_user
        self.client.force_authenticate(self.orderer_user)
        url = reverse("events_urls:event-orders-list")
        response = self.client.get(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['user'], self.orderer_user.id)

        #Orderer_user
        self.client.force_authenticate(self.orderer_user)
        url = reverse("events_urls:event-orders-list")
        response = self.client.get(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['place_ads']['user'], self.owner_user.id)

        #Another_user
        another_user = baker.make('authentication.User')
        self.client.force_authenticate(another_user)
        url = reverse("events_urls:event-orders-list")
        response = self.client.get(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']),0)
    
    
class CancellationTests(APITestCase):
    def setUp(self):
        self.owner_user = baker.make('authentication.User')
        self.orderer_user = baker.make('authentication.User')
        self.place_ads = baker.make('places.PlaceAds', user=self.owner_user)
        
        self.event_order = baker.make(
            'events.EventOrder',
            place_ads=self.place_ads,
            user=self.orderer_user,
            status=1
        )

    def test_cancel_event_order_if_user_is_owner_user(self):
        body = {
            "event_order": self.event_order.id,
            "justification": "Porque eu quis."
        }
        
        self.client.force_authenticate(self.owner_user)
        url = reverse("events_urls:cancellations-list")
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        #event_order
        self.assertEqual(EventOrder.objects.get(id=self.event_order.id).status, 4)

        #cancellation
        cancellation = Cancellation.objects.get()
        self.assertEqual(cancellation.justification, body['justification'])
        self.assertEqual(cancellation.event_order.id, body['event_order'])

    def test_dont_cancel_event_order_if_user_isnt_owner_or_orderder(self):
        other_user = baker.make('authentication.User')
        body = {
            "event_order": self.event_order.id,
            "justification": "Porque eu quis."
        }
        
        self.client.force_authenticate(other_user)
        url = reverse("events_urls:cancellations-list")
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dont_cancel_event_order_if_status_isnt_1_or_2(self):
        event_order2 = baker.make(
            'events.EventOrder',
            place_ads=self.place_ads,
            user=self.orderer_user,
            status=3
        )
        
        body = {
            "event_order": event_order2.id,
            "justification": "Porque eu quis."
        }
        
        self.client.force_authenticate(self.owner_user)
        url = reverse("events_urls:cancellations-list")
        response = self.client.post(url, body, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_cancel_event_order_if_event_order_doesnt_exists(self):
        body = {
            "event_order": self.event_order.id+1,
            "justification": "Porque eu quis."
        }
        
        self.client.force_authenticate(self.owner_user)
        url = reverse("events_urls:cancellations-list")
        response = self.client.post(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_owner_event_cancellations(self):
        correct_cancellation = baker.make('events.Cancellation', event_order=self.event_order)
        other_cancellation = baker.make('events.Cancellation')

        self.client.force_authenticate(self.owner_user)
        url = f'{reverse("events_urls:cancellations-list")}'
        response = self.client.get(url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], correct_cancellation.id)

    
class AcceptOrRefuseOrderTests(APITestCase):
    def setUp(self):
        self.owner_user = baker.make('authentication.User')
        self.orderer_user = baker.make('authentication.User')
        self.place_ads = baker.make('places.PlaceAds', user=self.owner_user)
        self.credit = baker.make('checkout.Credit', user=self.owner_user, amount=100)
        self.event_order = baker.make(
            'events.EventOrder',
            place_ads=self.place_ads,
            user=self.orderer_user,
            status=1
        )

    def test_accept_event_order(self):
        body = {
            "event_order": self.event_order.id
        }

        self.client.force_authenticate(self.owner_user)
        url = reverse("accept-order")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EventOrder.objects.get(id=self.event_order.id).status, 2)

    def test_refuse_event_order(self):
        body = {
            "event_order": self.event_order.id,
        }

        self.client.force_authenticate(self.owner_user)
        url = reverse("refuse-order")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(EventOrder.objects.get(id=self.event_order.id).status, 3)

    def test_dont_accept_event_order_if_user_isnt_owner(self):
        body = {
            "event_order": self.event_order.id,
        }

        self.client.force_authenticate(self.orderer_user)
        url = reverse("accept-order")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(EventOrder.objects.get(id=self.event_order.id).status, 2)

    def test_dont_refuse_event_order_if_user_isnt_owner(self):
        body = {
            "event_order": self.event_order.id,
        }

        self.client.force_authenticate(self.orderer_user)
        url = reverse("refuse-order")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(EventOrder.objects.get(id=self.event_order.id).status, 3)

    def test_dont_unlock_order_if_user_dont_have_credits(self):
        self.credit.amount = 0
        self.credit.save()
        
        body = {
            "event_order": self.event_order.id,
        }

        self.client.force_authenticate(self.owner_user)
        url = reverse("accept-order")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotEqual(EventOrder.objects.get(id=self.event_order.id).status, 3)

    def test_dont_refuse_event_order_if_status_not_1(self):
        self.event_order.status = 2
        self.event_order.save()

        body = {
            "event_order": self.event_order.id
        }

        self.client.force_authenticate(self.owner_user)
        url = reverse("refuse-order")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_accept_event_order_if_status_not_1(self):
        self.event_order.status = 2
        self.event_order.save()

        body = {
            "event_order": self.event_order.id
        }

        self.client.force_authenticate(self.owner_user)
        url = reverse("accept-order")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateDatesSelectedTests(APITestCase):
    def setUp(self):
        self.owner_user = baker.make('authentication.User')
        self.orderer_user = baker.make('authentication.User')
        self.place_ads = baker.make('places.PlaceAds', user=self.owner_user)

        for i in range(7):
            baker.make('places.WeekDay', day=i)
        
        self.plan = baker.make(
            'places.Plan',
            plan_type=1,
            place_ads=self.place_ads,
            week_days=WeekDay.objects.filter().exclude(day=5).exclude(day=6),   #Segunda a sexta
            price=200,
            )
        
        self.event_order = baker.make(
            'events.EventOrder',
            place_ads=self.place_ads,
            user=self.orderer_user,
            plan_type=self.plan.plan_type,
            status=1
        )

        date1 = "09/12/2021 10:40:00"   #QUINTA
        date2 = "10/12/2021 04:50:00"   #SEXTA
        date3 = "11/12/2021 04:50:00"   #SABADO
        date4 = "12/12/2021 04:50:00"   #DOMINGO
        self.datetime1 = datetime.strptime(date1, "%d/%m/%Y %H:%M:%S")
        self.datetime2 = datetime.strptime(date2, "%d/%m/%Y %H:%M:%S")
        self.datetime3 = datetime.strptime(date3, "%d/%m/%Y %H:%M:%S")
        self.datetime4 = datetime.strptime(date4, "%d/%m/%Y %H:%M:%S")
        self.timestamp1 = time.mktime(self.datetime1.timetuple())
        self.timestamp2 = time.mktime(self.datetime2.timetuple())
        self.timestamp3 = time.mktime(self.datetime3.timetuple())
        self.timestamp4 = time.mktime(self.datetime4.timetuple())

    def test_update_dates_selected_from_event_order(self):
        body = {
            "event_order": self.event_order.id,
            "dates_selected": [self.timestamp1, self.timestamp2],
            "plan": self.plan.id,
        }
        
        self.client.force_authenticate(self.orderer_user)
        url = reverse("dates-selected-update")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        event_order = EventOrder.objects.get(id=self.event_order.id)
        self.assertEqual(event_order.dates_selected, [self.datetime1, self.datetime2])
        self.assertEqual(event_order.price, len(body['dates_selected']) * self.plan.price)
    
    def test_dont_update_dates_selected_from_event_order_if_status_isnt_1(self):
        event_order_status_not_1 = baker.make(
            'events.EventOrder',
            place_ads=self.place_ads,
            user=self.orderer_user,
            plan_type=self.plan.plan_type,
            status=2
        )

        body = {
            "event_order": event_order_status_not_1.id,
            "dates_selected": [self.timestamp1, self.timestamp2],
            "plan": self.plan.id,
        }
        
        self.client.force_authenticate(self.orderer_user)
        url = reverse("dates-selected-update")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_update_dates_selected_from_event_order_if_user_isnt_orderer(self):
        body = {
            "event_order": self.event_order.id,
            "dates_selected": [self.timestamp1, self.timestamp2],
            "plan": self.plan.id,
        }
        
        self.client.force_authenticate(self.owner_user)
        url = reverse("dates-selected-update")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dont_update_dates_selected_from_event_order_if_dates_arent_in_the_daily_plan(self):
        body = {
            "event_order": self.event_order.id,
            "dates_selected": [self.timestamp3, self.timestamp4],
            "plan": self.plan.id,
        }
        
        self.client.force_authenticate(self.orderer_user)
        url = reverse("dates-selected-update")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_update_dates_selected_from_event_order_if_dates_arent_the_same_of_package_plan(self):
        plan_package = baker.make(
            'places.Plan',
            plan_type=2,
            place_ads=self.place_ads,
            week_days=WeekDay.objects.filter().exclude(day=0).exclude(day=1).exclude(day=2).exclude(day=3).exclude(day=4),
            price=200,
            )
        
        event_order2 = baker.make(
            'events.EventOrder',
            place_ads=self.place_ads,
            user=self.orderer_user,
            plan_type=plan_package.plan_type,
            status=1
        )

        body = {
            "event_order": event_order2.id,
            "dates_selected": [self.timestamp2, self.timestamp3],
            "plan": plan_package.id,
        }
        
        self.client.force_authenticate(self.orderer_user)
        url = reverse("dates-selected-update")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dont_update_dates_selected_from_event_order_if_plan_type_arent_the_same(self):
        plan_package = baker.make(
            'places.Plan',
            plan_type=2,
            place_ads=self.place_ads,
            week_days=WeekDay.objects.filter().exclude(day=0).exclude(day=1).exclude(day=2).exclude(day=3).exclude(day=4),
            price=200,
            )

        body = {
            "event_order": self.event_order.id,
            "dates_selected": [self.timestamp3, self.timestamp4],
            "plan": plan_package.id,
        }
        
        self.client.force_authenticate(self.orderer_user)
        url = reverse("dates-selected-update")
        response = self.client.patch(url, body, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

