from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from models import Practitioner, Patient, LabTest, OrderMessage
import pdb
import hl7tools
from django.views.decorators.csrf import csrf_exempt
import json
import random
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import requests
import pprint
import hashlib

# Create your views here.


def home(request):
    context = {
        'title': 'LabIT - Home'
    }
    return render(request, "messagegenerator/home.html", context)


def order_test_home(request):
    if request.method == "POST":
        practitioner = request.POST.get("practitioner")
        patient = request.POST.get("patient")
        tests = request.POST.getlist("tests")
        care_team = request.POST.getlist("care_team")

        care_team_1 = None
        care_team_2 = None

        if len(care_team) == 1:
            care_team_1 = Practitioner.objects.get(name=care_team[0])
            care_team_2 = random.choice(Practitioner.objects.all())

        elif len(care_team) == 2:
            care_team_1 = Practitioner.objects.get(name=care_team[0])
            care_team_2 = Practitioner.objects.get(name=care_team[1])

        else:
            care_team_1 = random.choice(Practitioner.objects.all())
            care_team_2 = random.choice(Practitioner.objects.all())


        critical = request.POST.get("iscritical")
        is_critical = True if critical is not None else False
        critical = "(Critical)" if is_critical else ""

        #generate the hl7 message here
        practitioner_id = Practitioner.objects.get(name=practitioner).fhir_id
        patient_id = Patient.objects.get(name=patient).fhir_id
        hl7message, tests_values, room = hl7tools.generate_hl7_message(practitioner_id, patient_id, tests, is_critical)
        hl7_context_dict = hl7tools.parse_hl7_message(hl7message)

        messages = generate_push_notification(hl7_context_dict)

        for message, message_val, rr in messages:
            for test in tests_values:
                diff = abs(float(test[0])-float(message_val))
                thresh = 0.00001
                if diff < thresh:
                    test.append(message)
                    test.append(rr)



        print len(tests_values)
        print tests_values
        for test in tests_values:
            print "test[0]", test[0]
            print "test[1]", test[1]
            message = ""
            rr = ""
            if len(test) == 5:
                message = test[3]
                rr = test[4]
            order = OrderMessage(ordering_practitioner=Practitioner.objects.get(name=practitioner),
                                 care_team_doctor_1=care_team_1,
                                 care_team_doctor_2=care_team_2,
                                 patient=Patient.objects.get(name=patient),
                                 test=LabTest.objects.get(test_name=test[1]),
                                 value=test[0],
                                 room=room,
                                 critical=test[2],
                                 taken_by_doctor=False,
                                 time_ordered=timezone.localtime(timezone.now()),
                                 time_claimed=timezone.localtime(timezone.now()),
                                 push_message=message,
                                 reference_range=rr)
            order.save()

        context = {
            "practitioner": practitioner,
            "patient": patient,
            "tests": tests,
            "critical": critical,
            "hl7message": hl7message.replace('\r','\n').split('\n'),
            "hl7message_one_line": json.dumps(hl7message.split('\n'))
        }
        return render(request, "messagegenerator/orderdetails.html", context)
    context = {
        'title': 'LabIT - Order a Test',
        'practitioners': Practitioner.objects.all(),
        'patients': Patient.objects.all(),
        'labtests': LabTest.objects.all()
    }
    return render(request, "messagegenerator/orderspecific.html", context)


def generate_push_notification(hl7_context_dictionary):
    notifications = []
    for result in hl7_context_dictionary["results"]:
        if result["is_critical"] == "AA":
            test_name = result["test_name"].replace("^", " ") + ","
            value_and_units = result["test_value"] + result["test_units"]
            room = "Location: " + hl7_context_dictionary["room_number"] + ","
            push_notification = " ".join([room, test_name, value_and_units])
            reference_range = result["reference_range"]
            notifications.append((push_notification, result["test_value"], reference_range))
    return notifications


def get_reference_ranges(hl7_context_dict):
    ranges = []
    for result in hl7_context_dict["results"]:
        reference_range = result["reference_range"]
        ranges.append(reference_range)
    return ranges


@csrf_exempt
def post_hl7_message(request):
    hl7message = None
    if request.method == "POST":
        hl7message = request.POST.get("hl7message")
        hl7message = json.loads(hl7message)[0]
    else:
        return home(request)
    if hl7message is not None:
        hl7_context_dictionary = hl7tools.parse_hl7_message(hl7message.replace('\n', '\r'))
        print hl7_context_dictionary
        notifs = generate_push_notification(hl7_context_dictionary)
        context = {
            "notifications": [n[0] for n in notifs]
        }

        messages = [OrderMessage.objects.get(push_message=n[0]) for n in notifs]

        push_notifications = []
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxNGIxM2NjZS1hY2Q3LTRiODQtYjhkYi03OGIyNjAxMWFkMmEifQ.d4xzSU6Rq-ZuqiTyoW7KxlzqGR1HYBFEPOaN9NdUvGo",
                   "content-type": "application/json"}
        endpoint = "https://api.ionic.io/push/notifications"

        for message in messages:
            push_notification = {}
            push_notification["tokens"] = message.get_tokens_of_care_team()
            push_notification["profile"] = "labitreports"
            notification = {}
            notification["title"] = "LabIT: Critical Result"
            notification["message"] = message.push_message
            payload = {}
            notification["payload"] = payload
            notification["android"] = {"data": {"notId": str(message.id) }}
            payload["id"] = message.id
            push_notification["notification"] = notification
            push_notifications.append(push_notification)

        for notification in push_notifications:
            print "NOTIFICATION"
            print "\n"
            pprint.pprint(json.dumps(notification))
            json_result = requests.post(endpoint, data=json.dumps(notification), headers=headers).json()
            print "RESULT"
            print "\n"
            print json_result





        return render(request, "messagegenerator/pushdetails.html", context)
    else:
        return render(request, "messagegenerator/error.html", {"error": "Error parsing HL7 message."})


def get_ordered_tests_(practitioner_fhir_id, taken_by_dr=False):
    orders_list = []
    practitioner_fhir_id = practitioner_fhir_id
    practitioner = Practitioner.objects.get(fhir_id=practitioner_fhir_id)
    orders = OrderMessage.objects.all()
    for order in orders:
        if order.time_remaining() > 1 and order.taken_by_doctor == taken_by_dr and order.is_on_care_team(practitioner):
            order_dict = order.to_dict()
            orders_list.append(order_dict)
    # json_response = json.dumps(orders_list)
    json_response = orders_list
    response = JsonResponse(json_response, safe=False)
    # response["Access-Control-Allow-Origin"] = "*"
    return response


def dashboard(request):
    valid_orders = []
    orders = OrderMessage.objects.all()
    for order in orders:
        if order.time_remaining() is not None:
            valid_orders.append( order )
    valid_orders.sort(key=lambda x: x.time_remaining())
    print valid_orders
    print len(valid_orders)
    return render(request, "messagegenerator/dashboard.html", {"orders": valid_orders})


@csrf_exempt
def get_ordered_tests(request, taken_by_dr=False):
    orders_list = []
    if request.method == "POST":
        request_json = json.loads(request.body)
        practitioner_fhir_id = request_json["practitioner_fhir_id"]
        practitioner = Practitioner.objects.get(fhir_id=practitioner_fhir_id)
        orders = OrderMessage.objects.all()
        for order in orders:
            #order.time_remaining() > 1 and
            if order.time_remaining() > 1 and order.taken_by_doctor == taken_by_dr and order.is_on_care_team(practitioner):
                order_dict = order.to_dict()
                orders_list.append(order_dict)
    # json_response = json.dumps(orders_list)
    json_response = orders_list
    response = JsonResponse(json_response, safe=False)
    # response["Access-Control-Allow-Origin"] = "*"
    return response


@csrf_exempt
def get_taken_tests(request):
    return get_ordered_tests(request, taken_by_dr=True)


@csrf_exempt
def get_doctors_on_call(request):
    doctors = []
    if request.method == "GET":
        on_call_doctors = Practitioner.objects.filter(on_call=True)
        for on_call_doctor in on_call_doctors:
            doctors.append(on_call_doctor.name)
    json_response = {"doctors": doctors}
    response = JsonResponse(json_response, safe=False)
    # response["Access-Control-Allow-Origin"] = "*"
    return response


@csrf_exempt
def login(request):
    resp = {}
    if request.method == "POST":
        request_json = json.loads(request.body)
        try:
            practitioner = Practitioner.objects.get(fhir_id=request_json["practitioner_fhir_id"])
            practitioner.push_token = request_json["token"]
            practitioner.save()
            resp["status"] = "success"
            response = JsonResponse(resp, safe=False)
            # response["Access-Control-Allow-Origin"] = "*"
            return response
        except (ObjectDoesNotExist, KeyError):
            resp["status"] = "user not found"
            response = JsonResponse(resp, safe=False)
            # response["Access-Control-Allow-Origin"] = "*"
            return response


@csrf_exempt
def take_test(request):
    resp = {}
    if request.method == "POST":
        request_json = json.loads(request.body)
        try:
            practitioner_fhir_id = request_json["practitioner_fhir_id"]
            test_id = request_json["id"]
            test = OrderMessage.objects.get(id=test_id)
            test.claimer = practitioner_fhir_id
            test.taken_by_doctor = True
            test.time_claimed = timezone.localtime(timezone.now())
            test.save()
            resp["status"] = "success"
        except (ObjectDoesNotExist, KeyError):
            resp["status"] = "error"
    return JsonResponse(resp, safe=False)

