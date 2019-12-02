from django.db import models

# Create your models here.
class Rank(models.Model):
    name = models.CharField(max_length=255)
    to_name = models.CharField(max_length=255, blank=True, null=True)
    for_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=255)
    parent_unit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_all_parents(self, include_self=False):
        """return all parent units """
        parents_units = []
        if include_self:
            parents_units.append(self)
        for unit in Unit.objects.filter(unit=self):
            _r = unit.get_all_parents(include_self=True)
            if 0 <= len(_r):
                parents_units.extend(_r)
        return parents_units


class Position(models.Model):
    position_title = models.CharField(max_length=255)
    position_tail = models.CharField(max_length=255, blank=True)
    unit = models.ForeignKey('Unit', on_delete=models.DO_NOTHING)

    supervisor = models.BooleanField(blank=True, null=True)
    temp_supervisor = models.BooleanField(blank=True, null=True)

    def __str__(self):
        if self.temp_supervisor:
            pos_result = "Тимчасово виконуючий обов'язки\n" + self.position_title.split()[0] + "а"
        else:
            pos_result = self.position_title
        return pos_result.capitalize() + " " + \
               self.unit.name + \
               self.position_tail


    def get_to_position(self):
        """return comprehenced position name with unit name for current tier"""
        pos_result = ""
        position_tail_str = ""
        if self.temp_supervisor:
            pos_result = "Тимчасово виконуючому обов'язки\n" + self.position_title.split()[0] + "а" #начальник[а]
        elif self.supervisor:
            pos_result = self.position_title.split()[0] + "у" #начальник[у]

        # "- заступник[у] начальника"
        if len(self.position_tail) > 0:
            temp_tail = self.position_tail.split()
            temp_tail[1] = temp_tail[1] + "у"
            position_tail_str = " ".join(temp_tail)

        return pos_result.capitalize() + " " + \
               self.unit.name + " " + \
               position_tail_str


class Serviceman(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


    to_first_name = models.CharField(max_length=255)
    to_last_name = models.CharField(max_length=255)

    for_first_name = models.CharField(max_length=255)
    for_last_name = models.CharField(max_length=255)

    rank = models.ForeignKey('Rank', on_delete=models.DO_NOTHING)
    unit = models.ForeignKey('Unit', on_delete=models.DO_NOTHING)
    position = models.ForeignKey('Position', on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_last_first_name(self):
        return self.last_name + " " + self.first_name

    def get_first_last_name(self):
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return self.first_name + " " + self.last_name.upper()

    def get_full_name_to(self):
        return self.to_first_name + " " + self.to_last_name.upper()

    def get_full_name_for(self):
        return self.for_first_name.capitalize() + " " + self.for_last_name.capitalize()


class Report(models.Model):
    title = models.CharField(max_length=255, null=True)
    body_sample = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class TestReport(models.Model):

    REPORT_TITLES = (
        (0, 'Report_1'),
        (1, 'Report_2'),
        (2, 'Report_3')
    )
    report_title = models.IntegerField(default=-1, choices=REPORT_TITLES)
    # report_title = models.IntegerField(default=0, choices=REPORT_TITLES)
    report_fields = models.CharField(max_length=1024)

    def __str__(self):
        return self.REPORT_TITLES[self.report_title][1] + " " + self.report_fields

