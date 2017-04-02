from django.shortcuts import render
from django.http import HttpResponse
from models import Practitioner, Patient, LabTest
import pdb

# Create your views here.


def home(request):
    context = {
        'title': 'LabIT - Home'
    }
    return render(request, "messagegenerator/home.html", context)


def order_test_home(request):
    if request.method == "POST":
        print "got a post"
        practitioner = request.POST.get("practitioner")
        patient = request.POST.get("patient")
        tests = request.POST.getlist("tests")
        critical = request.POST.get("iscritical")
        critical = "(Critical)" if critical is not None else ""
        #generate the hl7 message here
        context = {
            "practitioner": practitioner,
            "patient": patient,
            "tests": tests,
            "critical": critical
        }
        return render(request, "messagegenerator/orderdetails.html", context)
    context = {
        'title': 'LabIT - Order a Test',
        'practitioners': Practitioner.objects.all(),
        'patients': Patient.objects.all(),
        'labtests': LabTest.objects.all()
    }
    return render(request, "messagegenerator/orderspecific.html", context)