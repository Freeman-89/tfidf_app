from django.db import models


class Word(models.Model):
    text = models.CharField(verbose_name='слово_глобально', max_length=64, unique=True)
    idf = models.FloatField(default=0.0)

    def __str__(self):
        return self.text


class WordsInDocument(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    uuid_document_name = models.CharField(verbose_name='имя документа', max_length=64)
    tf = models.FloatField(verbose_name='tf')

    def __str__(self):
        return f"{self.word} in {self.uuid_document_name}"
