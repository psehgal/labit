from hl7apy.core import Message, Segment
import hl7apy.parser as hl7parser
from models import Practitioner, Patient, LabTest
import random
import pdb

# These are from Robert's email to us with HL7 messages
SENDING_APPLICATION = "13^1.2.840.114350.1.13.244.2.7.2.695071^ISO"
SENDING_FACILITY = "1^1.2.840.114350.1.13.244.2.7.2.768368^ISO"

# Make our server the receiving application of the message
RECEIVING_APPLICATION = "LabIT"


def print_hl7_message(message):
    print message.to_er7().replace('\r', '\n')


def get_hl7_string(message):
    return message.to_er7()


def parse_hl7_message(hl7message):
    m = hl7parser.parse_message(hl7message)
    segments = hl7parser.parse_segments(hl7message)
    hl7_parsed_context = {}
    tests = []
    for segment in segments:
        if segment.name == "PV1":
            hl7_parsed_context["practitioner"] = segment.pv1_7.to_er7()
            hl7_parsed_context["room_number"] = segment.pv1_3.to_er7()
        elif segment.name == "PID":
            patient_id = segment.pid_1.to_er7()
            patient_name = segment.pid_5.to_er7().replace("^", " ")
            patient_sex = segment.pid_8.to_er7()
            hl7_parsed_context["patient_id"] = patient_id
            hl7_parsed_context["patient_name"] = patient_name
            hl7_parsed_context["patient_sex"] = patient_sex
        elif segment.name == "OBX":
            individual_test = {}
            test_loinc_id = segment.obx_4.to_er7()
            test_name = segment.obx_3.to_er7()
            test_value = segment.obx_5.to_er7()
            test_units = segment.obx_6.to_er7()
            is_critical = segment.obx_8.to_er7()
            individual_test["test_loinc_id"] = test_loinc_id
            individual_test["test_name"] = test_name
            individual_test["test_value"] = test_value
            individual_test["test_units"] = test_units
            individual_test["is_critical"] = is_critical
            individual_test["reference_range"] = segment.obx_7.to_er7()
            tests.append(individual_test)
    hl7_parsed_context["results"] = tests
    return hl7_parsed_context


def generate_hl7_message(practitioner, patient, tests, critical):
    patient_object = Patient.objects.get(fhir_id=patient)
    practitioner_object = Practitioner.objects.get(fhir_id=practitioner)

    hl7message = Message("ORU_R01")
    hl7message.msh.msh_3 = SENDING_APPLICATION
    hl7message.msh.msh_4 = SENDING_FACILITY
    hl7message.msh.msh_5 = RECEIVING_APPLICATION
    hl7message.msh.msh_9 = "ORU^R01^ORU_R01"
    hl7message.msh.msh_10 = str(random.randint(1,100))
    hl7message.msh.msh_11 = str(random.randint(1, 100))
    hl7message.msh.msh_12 = str(2.5)

    pid = Segment("PID")
    hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.PID.pid_1 = patient
    hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.PID.pid_3 = patient
    # TODO: last, first
    hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.PID.pid_5 = patient_object.name.replace(' ', '^')
    hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.PID.pid_7 = patient_object.birthday
    hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_PATIENT.PID.pid_8 = patient_object.sex[0]
    #10 - Race
    #11 - Address
    #Should those ^ be queried from fhir?
    #More PID fields here, but I think the above are necessary... https://corepointhealth.com/resource-center/hl7-resources/hl7-pid-segment

    pv1 = Segment("PV1")
    #PV1 - Patient Visit Information Segement (https://corepointhealth.com/resource-center/hl7-resources/hl7-pv1-patient-visit-information-segment)
    #PV1_3 is patient location - ask Cotterman if this has room number and how to parse it.
    locations = ["Room " + str(x) for x in range(1, 51)] + ["Waiting Room"] * 50 + ["Zone 1"] * 20 + ["Zone 2"] * 20 + ["Zone 3"] * 20

    room = random.choice(locations)
    pv1.pv1_3 = room
    pv1.pv1_2 = "E"
    pv1.pv1_7 = practitioner
    hl7message.add(pv1)
    tests_values = []
    for i, test in enumerate(tests):

        test_object = LabTest.objects.get(test_name=test)
        if i == 0:
            hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.OBR.obr_4 = test_object.loinc_id
            hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_3 = test.replace(" ", "^")
            hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_4 = test_object.loinc_id
            value, test_range = patient_object.get_test_value(test_object, critical)
            hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_5 = str(value)
            hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_6 = test_range.test_units
            hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_7 = str(test_range.test_reference_range_lower) + "-" + str(test_range.test_reference_range_upper)
            hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_11 = "F"
            if critical:
                hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_8 = "AA"
            else:
                hl7message.ORU_R01_PATIENT_RESULT.ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_8 = "N"
            tests_values.append( [value, test, critical] )
        else:
            hl7message.add_group("ORU_R01_PATIENT_RESULT")
            hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.OBR.obr_4 = test_object.loinc_id
            hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_3 = test.replace(" ", "^")
            hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_4 = test_object.loinc_id
            value, test_range = patient_object.get_test_value(test_object, critical)
            hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_5 = str(value)
            hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_6 = test_range.test_units
            hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_7 = str(test_range.test_reference_range_lower) + "-" + str(test_range.test_reference_range_upper)
            hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_11 = "F"
            if critical:
                hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_8 = "AA"
            else:
                hl7message.ORU_R01_PATIENT_RESULT[i].ORU_R01_ORDER_OBSERVATION.ORU_R01_OBSERVATION.OBX.obx_8 = "N"
            tests_values.append( [value, test, critical] )
    return get_hl7_string(hl7message), tests_values, room

