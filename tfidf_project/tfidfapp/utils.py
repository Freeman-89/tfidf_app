import math
from collections import Counter
from typing import List, Dict, Union, BinaryIO, Tuple
from django.db.models import Count
from .models import WordsInDocument, Word


class TfIdfCompute:
    """
    Используем фасад, для обработки логики вычислений tfidf
    """
    def __init__(self, file: BinaryIO, document_name) -> None:
        self.file = file
        self.document_name= document_name
        self.file.seek(0)  # Переносим курсор в начало файла

    def get_words(self) -> List[str]:
        text: str = self.file.read().decode('utf-8').replace('\n', ' ')
        punctuations: str = ".,!?-«»—…“”‘’"
        clean_text: str = ''

        for char in text:
            if char not in punctuations:
                clean_text += char

        words: List[str] = clean_text.split()
        return words

    def compute_tf(self) -> Dict[str, float]:
        words: List[str] = self.get_words()
        total_words: int = len(words)
        word_counts: Counter = Counter(words)
        tf_dict: Dict[str, float] = {word: count / total_words for word, count in word_counts.items()}

        for word, tf in tf_dict.items():
            word_obj, created = Word.objects.get_or_create(text=word)
            WordsInDocument.objects.create(word=word_obj, uuid_document_name=self.document_name, tf=tf)
        return tf_dict

    def compute_idf(self) -> dict[str, float]:
        document_count: int = WordsInDocument.objects.values('uuid_document_name').distinct().count()
        word_df_qs = WordsInDocument.objects.values("word_id").annotate(
            df=Count("uuid_document_name", distinct=True)
        )

        df_map = {row['word_id']: row['df'] for row in word_df_qs}
        idf_dict: Dict[str, float] = {}
        words_to_update: List[Word] = []

        for word_obj in Word.objects.all().iterator():
            df = df_map.get(word_obj.id, 0)
            idf_value: float = math.log((1 + document_count) / (1 + df)) + 1
            word_obj.idf = idf_value
            words_to_update.append(word_obj)
            idf_dict[word_obj.text] = idf_value
        Word.objects.bulk_update(words_to_update, ['idf'])
        return idf_dict

    def compute_tfidf(self) -> Tuple[Dict[str, float], Dict[str, float]]:
        tf_dict: Dict[str, float] = self.compute_tf()
        full_idf: Dict[str, float] = self.compute_idf()
        idf_dict: Dict[str, float] = {word: full_idf[word] for word in tf_dict.keys()}
        return tf_dict, idf_dict
