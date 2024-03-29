from typing import Optional, Union, List, Dict, Tuple
import re
import collections
from collections import defaultdict


class BPETokenizer:
    def __init__(self, corpus: Optional[Union[List[str], str]] = None):
        self.vocab = {}
        if corpus is not None:
            self.add_corpus(corpus)

    def add_corpus(self, corpus: Union[List[str], str]) -> None:
        if isinstance(corpus, str):
            corpus = [corpus]
        for text in corpus:
            # 전처리 등 추가적인 처리가 필요하다면 여기에서 수행
            self.vocab[' '.join(list(text))] = self.vocab.get(' '.join(list(text)), 0) + 1

    def get_stats(self):
        pairs = collections.defaultdict(int)
        for word, freq in self.vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[symbols[i], symbols[i + 1]] += freq
        return pairs

    def merge_vocab(self, pair):
        v_out = {}
        bigram = re.escape(' '.join(pair))
        p = re.compile(r'(?<!\\S)' + bigram + r'(?!\\S)')
        for word in self.vocab:
            w_out = p.sub(''.join(pair), word)
            v_out[w_out] = self.vocab[word]
        return v_out

    def train(self, n_iter: int) -> None:
        for i in range(n_iter):
            pairs = self.get_stats()
            best = max(pairs, key=pairs.get)
            self.vocab = self.merge_vocab(best)

    def tokenize(self, text: Union[List[str], str], padding: bool = False, max_length: Optional[int] = None) -> Union[List[List[int]], List[int]]:
        if isinstance(text, str):
            text = [text]

        tokenized_texts = []
        for sentence in text:
            symbols = sentence.split()
            token_ids = []
            for symbol in symbols:
                token_ids.append(self.vocab.get(symbol, -1))  # -1로 처리되지 않은 token에 대한 ID 부여
            tokenized_texts.append(token_ids)

        if padding:
            max_len = max(len(tokens) for tokens in tokenized_texts)
            tokenized_texts = [tokens + [0] * (max_len - len(tokens)) for tokens in tokenized_texts]

        if max_length is not None:
            tokenized_texts = [tokens[:max_length] for tokens in tokenized_texts]

        return tokenized_texts

    def __call__(self, text: Union[List[str], str], padding: bool = False, max_length: Optional[int] = None) -> Union[List[List[int]], List[int]]:
        return self.tokenize(text, padding, max_length)

class WordTokenizer:
    def __init__(self, corpus: Optional[Union[List[str], str]] = None):
        self.vocab = defaultdict(int)
        self.vocab_token_index = {}

        if corpus is not None:
            self.add_corpus(corpus)

    def add_corpus(self, corpus: Union[List[str], str]) -> None:
        if isinstance(corpus, str):
            corpus = [corpus]

        for line in corpus:
            self.add_line_to_vocab(line)

    def add_line_to_vocab(self, line: str):
        for word in line.strip().split():
            self.vocab[word] += 1

    def build_vocab(self, *args, **kwargs) -> None:
        self.vocab_token_index = {word: idx for idx, word in enumerate(self.vocab)}

    def tokenize(self, text: Union[List[str], str]) -> Union[List[List[int]], List[int]]:
        if isinstance(text, str):
            text = [text]

        tokenized_texts = []
        for line in text:
            tokens = line.strip().split()
            tokenized_text = [self.vocab_token_index.get(token, -1) for token in tokens]
            tokenized_texts.append(tokenized_text)

        return tokenized_texts if len(tokenized_texts) > 1 else tokenized_texts[0]

    def __call__(self, text: Union[List[str], str], *args, **kwargs) -> Union[List[List[int]], List[int]]:
        return self.tokenize(text)
