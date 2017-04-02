from __future__ import unicode_literals

from django.db import models
from datetime import datetime


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


class Practitioner(models.Model):
    name = models.CharField(max_length=150)
    fhir_id = models.CharField(max_length=50)
    ssn = models.CharField(max_length=9)
    national_provider_identifier = models.CharField(max_length=50)
    michigan_common_key_service_identifier = models.CharField(max_length=50)

    def __str__(self):
        return self.name + ", " + self.fhir_id


class Patient(models.Model):
    name = models.CharField(max_length=150)
    fhir_id = models.CharField(max_length=50)
    ssn = models.CharField(max_length=9)
    birthday = models.CharField(max_length=15)
    sex = models.CharField(max_length=10)
    michigan_common_key_service_identifier = models.CharField(max_length=50)

    def get_age_in_days(self):
        b_date = datetime.strptime(self.birthday, "%Y-%m-%d")
        days = (datetime.today() - b_date).days
        return days

    def __str__(self):
        return self.name + ", " + self.fhir_id


class OrderMessage(models.Model):
    ordering_practitioner = models.OneToOneField(Practitioner, on_delete=models.CASCADE)
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)





