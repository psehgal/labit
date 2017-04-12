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
        print len(tests_values)
        print tests_values
        for test in tests_values:
            print "test[1]", test[1]
            order = OrderMessage(ordering_practitioner=Practitioner.objects.get(name=practitioner),
                                 care_team_doctor_1=care_team_1,
                                 care_team_doctor_2=care_team_2,
                                 patient=Patient.objects.get(name=patient),
                                 test=LabTest.objects.get(test_name=test[1]),
                                 value=test[0],
                                 room=room,
                                 critical=test[1],
                                 taken_by_doctor=False,
                                 time_ordered=timezone.localtime(timezone.now()))
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
        test_name = result["test_name"].replace("^", " ")
        value_and_units = result["test_value"] + result["test_units"] + ","
        room = "Room: " + hl7_context_dictionary["room_number"]
        push_notification = " ".join([test_name, value_and_units, room])
        notifications.append(push_notification)
    return notifications


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
            "notifications": notifs
        }
        #SEND PUSH NOTIFICATIONS HERE
        return render(request, "messagegenerator/pushdetails.html", context)
    else:
        return render(request, "messagegenerator/error.html", {"error": "Error parsing HL7 message."})


@csrf_exempt
def get_ordered_tests(request, taken_by_dr=False):
    orders_list = []
    if request.method == "POST":
        request_json = json.loads(request.body)
        practitioner_fhir_id = request_json["practitioner_fhir_id"]
        practitioner = Practitioner.objects.get(fhir_id=practitioner_fhir_id)
        orders = OrderMessage.objects.all()
        for order in orders:
            if order.time_remaining() > 1 and order.taken_by_doctor == taken_by_dr and order.is_on_care_team(practitioner):
                order_dict = order.to_dict()
                orders_list.append(order_dict)
    # json_response = json.dumps(orders_list)
    json_response = orders_list
    return JsonResponse(json_response, safe=False)


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
    json_response = json.dumps(doctors)
    return JsonResponse(json_response, safe=False)


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
            return JsonResponse(json.dumps(resp), safe=False)
        except (ObjectDoesNotExist, KeyError):
            resp["status"] = "user not found"
            return JsonResponse(json.dumps(resp), safe=False)

