from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.name)


class Category(models.Model):
    name = models.CharField(max_length=100)
    sub_category = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.name)


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    model = models.CharField(max_length=100, null=True, blank=True)
    composition = models.CharField(max_length=100)
    UOM = models.TextField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.name)

