from django.db import models


# Create your models here.
class Rank(models.Model):
    name = models.CharField(max_length=255, verbose_name="військове звання (полковник, лейтенант..)")
    to_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="військове звання, давальний відмінок (полковнику, лейтенанту..)")
    for_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="військове звання, знахідний відмінок (полковника, лейтенанта..)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Військові звання__"
        verbose_name_plural = "Військові звання"


class Unit(models.Model):
    name = models.CharField(max_length=255, verbose_name="назва підрозділу в РОДОВОМУ відміноку (відділу аналізу інцидентів кібернетичної безпеки)")
    parent_unit = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, verbose_name="вищій підрозділ (віддліл->центр->..)")

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

    class Meta:
        verbose_name = "Підрозділ"
        verbose_name_plural = "Підрозділи"


class Position(models.Model):
    position_title = models.CharField(max_length=255, verbose_name="посада (офіцер, старший офіцер, начальник)")
    position_tail = models.CharField(max_length=255, default='', blank=True, verbose_name="додаткова посада. Наприклад:(заступник начальника, перший заступник командира...)  !!! назву підрозділу НЕ ВКАЗУВАТИ  !!!")
    unit = models.ForeignKey('Unit', on_delete=models.DO_NOTHING, verbose_name="підрозділ")

    supervisor = models.BooleanField(default=False, blank=True, null=True, verbose_name="командир/начальник підрозділу")
    temp_supervisor = models.BooleanField(default=False, blank=True, null=True, verbose_name="тимчасово виконуючий обов'язки командира/начальника")

    def __str__(self):
        if self.temp_supervisor:
            pos_result = "Тимчасово виконуючий обов'язки\n" + self.position_title.split()[0] + "а"
        else:
            pos_result = self.position_title[0].capitalize() + self.position_title[1:]

        # add dash and position tail
        pos_result += " " + self.unit.name
        if len(self.position_tail) > 0:
            pos_result += " – " + self.position_tail

        return pos_result

    def get_to_position(self):
        """return comprehenced position name with unit name for current tier"""
        pos_result = ""
        if self.temp_supervisor:
            pos_result = "Тимчасово виконуючому обов'язки\n" + self.position_title.split()[0] + "а"  # начальник[а]
        elif self.supervisor:
            pos_result = (self.position_title.split()[0] + "у").capitalize()  # начальник[у]

        pos_result += " " + self.unit.name

        # ' - заступник[у] начальника' adding ending
        if len(self.position_tail) > 0:
            temp_tail = self.position_tail.split()
            temp_tail[0] = temp_tail[0] + "у"
            position_tail_str = " ".join(temp_tail)
            pos_result += " – " + position_tail_str

        return pos_result

    class Meta:
        verbose_name = "Посада__"
        verbose_name_plural = "Посади"


class Serviceman(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="Ім'я")
    last_name = models.CharField(max_length=255, verbose_name="Прізвище")


    to_first_name = models.CharField(max_length=255, verbose_name="Ім'я, давальний відмінок (Петру, Євгенії, Дмитру...)")
    to_last_name = models.CharField(max_length=255, verbose_name="Прізвище, давальний відмінок (Яцуку, Куріло, Павленку...)")

    for_first_name = models.CharField(max_length=255, verbose_name="Ім'я, знахідний відмінок (Петра, Євгенії, Дмитра...)")
    for_last_name = models.CharField(max_length=255, verbose_name="Прізвище, знахідний відмінок (Яцука, Куріло, Павленка...)")

    rank = models.ForeignKey('Rank', on_delete=models.DO_NOTHING, verbose_name="військове звання")
    unit = models.ForeignKey('Unit', on_delete=models.DO_NOTHING, verbose_name="Підрозділ")
    position = models.ForeignKey('Position', on_delete=models.DO_NOTHING, null=True, verbose_name="Посада")

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

    class Meta:
        verbose_name = "Військовослужбовці__"
        verbose_name_plural = "Військовослужбовці"


class Report(models.Model):
    REPORT_TYPES = [
        ('regular', 'звичайний рапорт'),
        ('custom', 'рапорт по специфічному шаблону'),
    ]
    type = models.CharField(max_length=100, choices=REPORT_TYPES, default='regular', verbose_name="тип рапорту")

    title = models.CharField(max_length=255, null=True, verbose_name="Назва рапорту")

    body_sample = models.TextField(blank=True, null=True, verbose_name="зразок тексту рапорту")
    body_template = models.TextField(blank=True, null=True, verbose_name="шаблон рапорту (змінюється адміністратором, див. у документації)")

    default_header_position = models.ForeignKey(Position, related_name='report_header_position_set', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="посада на кого цей рапорт")
    default_footer_position = models.ForeignKey(Position, related_name='report_footer_position_set', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="посада від кого цей рапорт")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Рапорти__"
        verbose_name_plural = "Рапорти"

