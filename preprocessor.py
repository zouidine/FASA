import re
import torch
import string

class Preprocessor():
    def __init__(self, precprocess, tokenizer):
        self.tokenizer = tokenizer
        self.precprocess = precprocess

    def clean(self, text):
        # Remove punctuations
        arabic_punctuations = '''`÷×؛<>_()*&^%][ـ،/:"؟.,'{}~¦+|!”…“–ـ'''
        english_punctuations = string.punctuation
        punctuations_list = arabic_punctuations + english_punctuations
        translator = str.maketrans('', '', punctuations_list)
        text = text.translate(translator)
        # Remove english characters
        text = re.sub(r'[a-zA-Z]+', '', text)
        # Remove numbers
        text = re.sub(r'[1-9]+', '', text)
        # Normalize arabic
        text = re.sub("[إأآا]", "ا", text)
        text = re.sub("ى", "ي", text)
        text = re.sub("ة", "ه", text)
        return text

    def clean_and_tokenize(self, sentences, labels):
        clean_sentences = []
        clean_labels = []
        for i in range(len(sentences)):
            text = sentences[i]
            # Cleaning
            text = self.precprocess(self.clean(text))
            # Tokenization
            text = self.tokenizer.tokenize(text)
            if len(text) != 0:
                if len(text)>510:
                    text = text[:255] + text[-255:]
                text.insert(0, self.tokenizer.cls_token)
                text.append(self.tokenizer.sep_token)
                clean_sentences.append(text)
                clean_labels.append(labels[i])
        return clean_sentences, clean_labels

    def creat_tensor(self, sentences):
        max_len = max([len(sen) for sen in sentences])
        batch = len(sentences)
        tensor_data = torch.zeros(batch, max_len, dtype=torch.int64)
        tensor_mask = torch.zeros(batch, max_len, dtype=torch.int64)
        for i in range(batch):
            ids = self.tokenizer.convert_tokens_to_ids(sentences[i])
            tensor_data[i, 0:len(ids)] = torch.tensor(ids, dtype=torch.int64)
            tensor_mask[i, 0:len(ids)] = torch.ones(1, len(ids), dtype=torch.int64)
        return tensor_data, tensor_mask
