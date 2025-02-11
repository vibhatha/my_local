from django.db import models

class Region(models.Model):
    """Base model for regions/entities"""
    entity_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, default="PD")
    
    class Meta:
        app_label = 'population_stats'
    
    def __str__(self):
        return self.name

class TotalPopulation(models.Model):
    """Total population statistics"""
    region = models.OneToOneField(Region, on_delete=models.CASCADE, primary_key=True)
    total_population = models.IntegerField()
    year = models.IntegerField(default=2012)
    
    class Meta:
        app_label = 'population_stats'
        verbose_name_plural = "Total Population"
    
    def __str__(self):
        return f"{self.region} - Population: {self.total_population}"

class AgeDistribution(models.Model):
    """Population by age groups"""
    region = models.OneToOneField(Region, on_delete=models.CASCADE, primary_key=True)
    total_population = models.IntegerField()
    less_than_10 = models.IntegerField()
    age_10_to_19 = models.IntegerField()
    age_20_to_29 = models.IntegerField()
    age_30_to_39 = models.IntegerField()
    age_40_to_49 = models.IntegerField()
    age_50_to_59 = models.IntegerField()
    age_60_to_69 = models.IntegerField()
    age_70_to_79 = models.IntegerField()
    age_80_to_89 = models.IntegerField()
    age_90_and_above = models.IntegerField()
    year = models.IntegerField(default=2012)

    class Meta:
        verbose_name_plural = "Age Distributions"

class EthnicityDistribution(models.Model):
    """Population by ethnicity"""
    region = models.OneToOneField(Region, on_delete=models.CASCADE, primary_key=True)
    total_population = models.IntegerField()
    sinhalese = models.IntegerField()
    sl_tamil = models.IntegerField()
    ind_tamil = models.IntegerField()
    sl_moor = models.IntegerField()
    burgher = models.IntegerField()
    malay = models.IntegerField()
    sl_chetty = models.IntegerField()
    bharatha = models.IntegerField()
    other_eth = models.IntegerField()
    year = models.IntegerField(default=2012)

    class Meta:
        verbose_name_plural = "Ethnicity Distributions"

class GenderDistribution(models.Model):
    """Population by gender"""
    region = models.OneToOneField(Region, on_delete=models.CASCADE, primary_key=True)
    total_population = models.IntegerField()
    male = models.IntegerField()
    female = models.IntegerField()
    year = models.IntegerField(default=2012)

    class Meta:
        verbose_name_plural = "Gender Distributions"

class MaritalStatus(models.Model):
    """Population by marital status"""
    region = models.OneToOneField(Region, on_delete=models.CASCADE, primary_key=True)
    total_population = models.IntegerField()
    never_married = models.IntegerField()
    married_registered = models.IntegerField()
    married_customary = models.IntegerField()
    separated_legally = models.IntegerField()
    separated_non_legal = models.IntegerField()
    divorced = models.IntegerField()
    widowed = models.IntegerField()
    not_stated = models.IntegerField()
    year = models.IntegerField(default=2012)


    class Meta:
        verbose_name_plural = "Marital Status Distributions"

class ReligiousAffiliation(models.Model):
    """Population by religious affiliation"""
    region = models.OneToOneField(Region, on_delete=models.CASCADE, primary_key=True)
    total_population = models.IntegerField()
    christian = models.IntegerField()
    buddhist = models.IntegerField()
    hindu = models.IntegerField()
    muslim = models.IntegerField()
    jewish = models.IntegerField()
    other_religion = models.IntegerField()
    no_religion = models.IntegerField()
    not_stated = models.IntegerField()
    year = models.IntegerField(default=2012)

    class Meta:
        verbose_name_plural = "Religious Affiliations"