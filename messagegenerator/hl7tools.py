from hl7apy.core import Message, Segment
from models import Practitioner, Patient, LabTest
import random

# These are from Robert's email to us with HL7 messages
SENDING_APPLICATION = "13^1.2.840.114350.1.13.244.2.7.2.695071^ISO"
SENDING_FACILITY = "1^1.2.840.114350.1.13.244.2.7.2.768368^ISO"

# Make our server the receiving application of the message
RECEIVING_APPLICATION = "LabIT"


def print_hl7_message(message):
    print "This is the hl7 message"
    print message.to_er7().replace('\r', '\n')


def get_hl7_string(message):
    return message.to_er7().replace('\r', '\n')


def generate_hl7_message(practitioner, patient, tests, critical):
    patient_object = Patient.objects.get(fhir_id=patient)
    practitioner_object = Practitioner.objects.get(fhir_id=practitioner)

    hl7message = Message("ORU_R01")
    hl7message.msh.msh_3 = SENDING_APPLICATION
    hl7message.msh.msh_4 = SENDING_FACILITY
    hl7message.msh.msh_5 = RECEIVING_APPLICATION

    pid = Segment("PID")
    pid.pid_1 = patient
    # TODO: last, first
    pid.pid_5 = patient_object.name.replace(' ', '^')
    pid.pid_7 = patient_object.birthday
    pid.pid_8 = patient_object.sex[0]
    #10 - Race
    #11 - Address
    #Should those be queried from fhir?
    #More PID fields here, but I think the above are necessary... https://corepointhealth.com/resource-center/hl7-resources/hl7-pid-segment
    hl7message.add(pid)

    pv1 = Segment("PV1")
    #PV1 - Patient Visit Information Segement (https://corepointhealth.com/resource-center/hl7-resources/hl7-pv1-patient-visit-information-segment)
    #PV1_3 is patient location - ask Cotterman if this has room number and how to parse it.
    pv1.pv1_2 = "E"
    pv1.pv1_3 = "ED"
    pv1.pv1_7 = practitioner
    hl7message.add(pv1)

    for test in tests:
        test_object = LabTest.objects.get(test_name=test)
        obr = Segment('OBR')
        obr.obr_4 = test_object.loinc_id
        hl7message.add(obr)
        obx = Segment('OBX')
        obx.obx_3 = test.replace(" ", "^")
        obx.obx_4 = test_object.loinc_id
        value, test_range = patient_object.get_test_value(test_object, critical)
        obx.obx_5 = str(value)
        obx.obx_6 = test_range.test_units
        obx.obx_7 = str(test_range.test_reference_range_lower) + "-" + str(test_range.test_reference_range_upper)
        if critical:
            obx.obx_8 = "AA"
        else:
            obx.obx_8 = "N"
        hl7message.add(obx)
    return get_hl7_string(hl7message)

