# contient le tokenizer et le modèle de sentiment
from typing import Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification
# sert à faire les calculs du modèle
import torch
from src.etl.utils.data_utils import DataUtils


def predict_sentiment(text: str) -> Dict[str, str]:
    """
    Prédit le sentiment d'un texte à l'aide d'un modèle de NLP (Natural Language Processing => 
    Traitement du langage naturel).

    :param text (str): Texte brut à analyser (avis utilisateur).

    :return:
        Dict[str, str] : Dictionnaire contenant :
            - "text_clean" : texte nettoyé utilisé pour la prédiction
            - "sentiment" : sentiment prédit par le modèle (Très négatif, Négatif, Neutre, Positif, Très positif)
    """

    text_clean = DataUtils.clean_text(text)

    if not text_clean:
        raise ValueError("L'avis fourni est vide ou non valide.")

    model_name = "tabularisai/multilingual-sentiment-analysis"
    tokenizer = AutoTokenizer.from_pretrained(
        model_name, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, local_files_only=True)

    sentiment_map = {
        0: "Très négatif",
        1: "Négatif",
        2: "Neutre",
        3: "Positif",
        4: "Très positif"
    }

    # Tokenisation du texte
    inputs = tokenizer(
        text_clean,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=512
    )

    # Passage du texte tokenisé dans le modèle
    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

    # _ permet d'ignorer le score, seule la classe prediction est utilisé
    _, prediction = torch.max(probabilities, dim=-1)

    return {
        "text_clean": text_clean,
        "sentiment": sentiment_map[prediction.item()],
    }


# TODO: A retirer plus tard, juste pour tester la fonction
if __name__ == "__main__":
    text = input("Entre un avis : ")
    result = predict_sentiment(text)
    print(f"Avis : {result['text_clean']}")
    print(f"Sentiment : {result['sentiment']}")
