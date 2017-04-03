from django.shortcuts import render
from django.http import HttpResponse
from models import Practitioner, Patient, LabTest
import pdb
import hl7tools

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
        critical = request.POST.get("iscritical")
        is_critical = True if critical is not None else False
        critical = "(Critical)" if is_critical else ""

        #generate the hl7 message here
        practitioner_id = Practitioner.objects.get(name=practitioner).fhir_id
        patient_id = Patient.objects.get(name=patient).fhir_id
        hl7message = hl7tools.generate_hl7_message(practitioner_id, patient_id, tests, is_critical)

        context = {
            "practitioner": practitioner,
            "patient": patient,
            "tests": tests,
            "critical": critical,
            "hl7message": hl7message.split('\n')
        }
        return render(request, "messagegenerator/orderdetails.html", context)
    context = {
        'title': 'LabIT - Order a Test',
        'practitioners': Practitioner.objects.all(),
        'patients': Patient.objects.all(),
        'labtests': LabTest.objects.all()
    }
    return render(request, "messagegenerator/orderspecific.html", context)