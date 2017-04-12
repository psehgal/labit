from __future__ import unicode_literals

from django.db import models
from datetime import datetime
import random


# Create your models here.


class LabTest(models.Model):
    test_name = models.CharField(max_length=200)
    loinc_id = models.CharField(max_length=50)

    def __str__(self):
        return self.test_name + ", " + self.loinc_id


class TestRanges(models.Model):
    patient_sex = models.CharField(max_length=1)
    age_range_lower_days = models.IntegerField()
    age_range_upper_days = models.IntegerField()
    test_reference_range_lower = models.FloatField()
    test_reference_range_upper = models.FloatField()
    test_low_critical_value = models.FloatField()
    test_high_critical_value = models.FloatField()
    test_units = models.CharField(max_length=10)
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    has_lower_critical_range = models.BooleanField(default=True)
    has_upper_critical_range = models.BooleanField(default=True)

    def __str__(self):
        age_range = "-".join([str(self.age_range_lower_days), str(self.age_range_upper_days)])
        test_ref_range = "-".join([str(self.test_reference_range_lower),
                                   str(self.test_reference_range_upper),
                                   self.test_units])
        critical_range = "-".join([str(self.test_low_critical_value),
                                   str(self.test_high_critical_value),
                                   self.test_units])
        lab_test_str = str(self.lab_test)
        details = " ".join([age_range, test_ref_range, critical_range, lab_test_str])
        return details


def f():
    return random.choice([True, False])


def g():
    zone = random.choice([1,2,3])
    return zone


class Practitioner(models.Model):
    name = models.CharField(max_length=150)
    fhir_id = models.CharField(max_length=50)
    ssn = models.CharField(max_length=9)
    national_provider_identifier = models.CharField(max_length=50)
    michigan_common_key_service_identifier = models.CharField(max_length=50)
    on_call = models.BooleanField(default=f)
    location = models.IntegerField(default=g())

    def __str__(self):
        return self.name + ", " + self.fhir_id


class Patient(models.Model):
    name = models.CharField(max_length=150)
    fhir_id = models.CharField(max_length=50)
    ssn = models.CharField(max_length=9)
    birthday = models.CharField(max_length=15)
    sex = models.CharField(max_length=10)
    michigan_common_key_service_identifier = models.CharField(max_length=50)

    def get_test_value(self, test, critical):
        test_ranges_for_test = TestRanges.objects.filter(lab_test=test)
        p_sex = None
        if self.sex[0] == "m" or self.sex[0] == "M":
            p_sex = "M"
        else:
            p_sex = "F"
        age_days = self.get_age_in_days()
        for range_ in test_ranges_for_test:
            if range_.patient_sex == p_sex and age_days < range_.age_range_upper_days and age_days > range_.age_range_lower_days:
                if range_.has_upper_critical_range:
                    if critical:
                        rand_mult = random.uniform(1.2, 1.9)
                        return range_.test_high_critical_value * rand_mult, range_
                    else:
                        return random.uniform(range_.test_reference_range_lower, range_.test_reference_range_upper), range_
                elif range_.has_lower_critical_range:
                    if critical:
                        rand_mult = random.uniform(0.1, 0.8)
                        return range_.test_low_critical_value * rand_mult, range_
                    else:
                        return random.uniform(range_.test_reference_range_lower, range_.test_reference_range_upper), range_

    def get_age_in_days(self):
        b_date = datetime.strptime(self.birthday, "%Y-%m-%d")
        days = (datetime.today() - b_date).days
        return days

    def __str__(self):
        return self.name + ", " + self.fhir_id


class OrderMessage(models.Model):
    ordering_practitioner = models.ForeignKey(Practitioner, related_name="%(class)s_related", on_delete=models.CASCADE)
    care_team_doctor_1 = models.ForeignKey(Practitioner, related_name="%(class)s_related_created", on_delete=models.CASCADE)
    care_team_doctor_2 = models.ForeignKey(Practitioner, related_name="%(class)s_related_created_here", on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    value = models.FloatField()
    room = models.IntegerField()
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    taken_by_doctor = models.BooleanField(default=False)
    critical = models.BooleanField(default=False)





