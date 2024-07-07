from django.db import models


class CSVMetaData(models.Model):
    filename = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
