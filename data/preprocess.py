from vncorenlp import VnCoreNLP
import re

# VnCoreNLP segmentizer
rdrsegmenter = None


class Preprocess:
    @staticmethod
    def deep_clean(s: str):
        """Do an advanced deep clean of the string

        Args:
            s (str): string to be cleaned

        Returns:
            str: cleaned string
        """

        s = s.replace("\n", " ")

        # normalization 1: xxxThis is a --> xxx. This is a (missing delimiter)
        s = re.sub(r"([a-z])([A-Z])", r"\1\. \2", s)  # before lower case
        # normalization 2: lower case
        s = s.lower()
        # normalization 3: "&gt", "&lt"
        s = re.sub(r"&gt|&lt", " ", s)
        # normalization 4: letter repetition (if more than 2)
        s = re.sub(r"([a-z])\1{2,}", r"\1", s)
        # normalization 5: non-word repetition (if more than 1)
        s = re.sub(r"([\W+])\1{1,}", r"\1", s)
        # normalization 6: string * as delimiter
        s = re.sub(r"\*|\W\*|\*\W", ". ", s)
        # normalization 7: stuff in parenthesis, assumed to be less informal
        s = re.sub(r"\(.*?\)", ". ", s)
        # normalization 8: xxx[?!]. -- > xxx.
        s = re.sub(r"\W+?\.", ".", s)
        # normalization 9: [.?!] --> [.?!] xxx
        s = re.sub(r"(\.|\?|!)(\w)", r"\1 \2", s)
        # normalization 12: phrase repetition
        s = re.sub(r"(.{2,}?)\1{1,}", r"\1", s)

        return s.strip()

    @staticmethod
    def teen_code_decode(text: str) -> str:
        """Replace teen codes with formal ones

        Args:
            text (str): text to be decoded

        Returns:
            str: decoded text
        """
        # TODO use a teen code list
        rep = {
            "k": "không",
            "ko": "không",
            "kh": "không",
            "đc": "được",
            "dc": "được",
            "a": "anh",
            "e": "em",
            "v": "vậy",
            "vs": "với",
            "m": "mình",
        }  # define desired replacements here

        rep_ = dict((r"\b{}\b".format(k), v) for k, v in rep.items())
        pattern = re.compile("|".join(rep_.keys()), flags=re.I)

        result = pattern.sub(lambda m: rep[re.escape(m.group(0)).lower()], text)

        return result

    @staticmethod
    def segmentize(
        text: str,
        do_deep_clean=False,
        do_teen_code=False,
        do_sentences=False,
        do_tokens=False,
        stopword_list=[],
    ) -> dict:
        """Segmentize text (aka "phân đoạn từ") using VnCoreNLP segmentizer.

        Args:
            text (str): the text to be segmentized
            do_deep_clean (bool, optional): Do deep clean on the text, could take much longer to process.
            do_sentences (bool, optional): Either return as the sentence form or not.
            do_tokens (bool, optional): Either return a list of tokens or not.
            stopword_list (list, optional): Words to exclude.

        Returns:
            dict: a dictionary of the form {'tokens': [], 'sentences': []}
        """

        if do_deep_clean:
            text = Preprocess.deep_clean(text)

        if do_teen_code:
            text = Preprocess.teen_code_decode(text)

        global rdrsegmenter

        if not rdrsegmenter:
            rdrsegmenter = VnCoreNLP(
                "lib/VnCoreNLP/VnCoreNLP-1.1.1.jar",
                annotators="wseg,pos",
                max_heap_size="-Xmx2g",
            )

        segmented = rdrsegmenter.annotate(text)["sentences"]

        sentences = None
        if do_sentences:
            paragraphs = []
            for paragraph in segmented:
                words = []
                for x in paragraph:
                    if x["form"].lower() not in stopword_list:
                        words.append(x["form"])
                paragraphs.append(" ".join(words))
            sentences = " ".join(paragraphs)

        tokens = []
        if do_tokens:
            for paragraph in segmented:
                for word in paragraph:
                    if (
                        word["form"].lower() not in stopword_list
                        and len(word["form"]) > 1
                        and word["posTag"]
                        in [
                            "N",  # Noun
                            "V",  # Verb
                            "Np",  # Proper noun (e.g. "Việt Nam")
                            "M",  # Numeric (e.g. "34")
                            "A",  # Adjective
                            "Ny", # Noun Abbreviation (e.g. "WTO")
                            "Nb", # Noun borrowed (e.g. Internet)
                            "Vb"  # Verb borrowed (e.g. "chat")
                        ]
                        # See more POS tag description:
                        # https://github.com/vncorenlp/VnCoreNLP/blob/master/VLSP2013_POS_tagset.pdf
                    ):
                        tokens.append(word["form"])

        return {
            "sentences": sentences,
            "tokens": tokens,
        }
